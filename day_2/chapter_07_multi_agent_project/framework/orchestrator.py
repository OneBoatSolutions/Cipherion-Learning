"""
Framework: Orchestrator
========================
A GENERIC pipeline runner for multi-agent workflows.

The Orchestrator does NOT know about specific agents (Clarifier, PRD, etc.).
Instead, you define a pipeline of Phases and the orchestrator runs them
sequentially, passing output from one phase to the next.

Usage:
    orchestrator = Orchestrator(client)
    orchestrator.register_agent("my_agent", agent)
    orchestrator.add_phase(Phase(
        name="My Phase",
        agent_name="my_agent",
        prompt_template="Do this: {user_input}",
    ))
    orchestrator.run("Build something")
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from openai import OpenAI
from .message_bus import MessageBus
from tools.sandbox import set_sandbox_root


@dataclass
class Phase:
    """
    A single step in the agent pipeline.

    Attributes:
        name:             Display name for this phase (e.g. "Clarification").
        agent_name:       Key used in register_agent() to look up the agent.
        prompt_template:  Template string with {user_input} and {previous_output}
                          placeholders. These are filled at runtime.
        report_filename:  If set, save the agent's output to this file in reports/.
                          Example: "01_specification.md"
        needs_approval:   If True, show output to user and ask for approval.
                          User can request edits (re-runs the agent with feedback).
        setup_sandbox:    If True, call set_sandbox_root(code_dir) before this phase.
        pass_message_bus: If True, set agent.message_bus = orchestrator's bus.
        pre_hooks:        Optional list of callables to run before the phase.
                          Each receives (agent, phase, context_dict).
        post_hooks:       Optional list of callables to run after the phase.
                          Each receives (agent, phase, output, context_dict).
    """
    name: str
    agent_name: str
    prompt_template: str
    report_filename: str | None = None
    needs_approval: bool = False
    setup_sandbox: bool = False
    pass_message_bus: bool = False
    pre_hooks: list[Callable] = field(default_factory=list)
    post_hooks: list[Callable] = field(default_factory=list)


class Orchestrator:
    """
    Generic pipeline runner for multi-agent workflows.

    The orchestrator:
        1. Creates a timestamped sandbox folder for each run
        2. Runs phases sequentially, passing output between them
        3. Routes messages between agents via the MessageBus
        4. Saves reports and exports the MessageBus log
    """

    COLORS = {
        "header": "\033[1;97m",  # Bold white
        "reset":  "\033[0m",
        "dim":    "\033[2m",
        "green":  "\033[92m",
        "yellow": "\033[93m",
        "cyan":   "\033[96m",
    }

    def __init__(self, client: OpenAI, output_base: str = None):
        self.client = client
        self.message_bus = MessageBus()
        self.agents = {}
        self.phases: list[Phase] = []
        self.output_base = output_base or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "output"
        )

    def register_agent(self, name: str, agent):
        """Register an agent by name."""
        self.agents[name] = agent

    def add_phase(self, phase: Phase):
        """Add a phase to the pipeline."""
        self.phases.append(phase)

    # ──────────────────────────────────────────
    # Pipeline execution
    # ──────────────────────────────────────────

    def run(self, user_input: str) -> str:
        """
        Execute the full pipeline.

        Args:
            user_input: The user's raw input to start the pipeline.

        Returns:
            The final phase's output.
        """
        # Create sandbox
        paths = self._create_sandbox()
        self.log(f"📂 Sandbox: {paths['sandbox']}")

        self._print_header("MULTI-AGENT PIPELINE")
        print(f"  Input: {user_input}")
        print(f"  Sandbox: {paths['sandbox']}")
        print(f"  Phases: {len(self.phases)}\n")

        # Log user input
        self.message_bus.send("user", "orchestrator", "input", user_input)

        # Shared context dict for hooks
        context = {
            "user_input": user_input,
            "paths": paths,
            "message_bus": self.message_bus,
        }

        previous_output = user_input

        for i, phase in enumerate(self.phases, 1):
            self._print_phase(f"Phase {i}/{len(self.phases)}: {phase.name}")

            # Look up agent
            agent = self.agents.get(phase.agent_name)
            if not agent:
                raise RuntimeError(
                    f"Agent '{phase.agent_name}' not registered. "
                    f"Available: {list(self.agents.keys())}"
                )

            # ── Pre-phase setup ──
            if phase.setup_sandbox:
                set_sandbox_root(paths["code"])

            if phase.pass_message_bus:
                agent.message_bus = self.message_bus

            for hook in phase.pre_hooks:
                hook(agent, phase, context)

            # ── Build prompt ──
            prompt = phase.prompt_template.format(
                user_input=user_input,
                previous_output=previous_output,
            )

            # ── Run agent ──
            output = agent.run(prompt)

            # ── User approval loop ──
            if phase.needs_approval:
                output = self._approval_loop(agent, phase, output)

            # ── Post-phase ──
            for hook in phase.post_hooks:
                hook(agent, phase, output, context)

            # Save report
            if phase.report_filename:
                self._save_report(
                    paths["reports"], phase.report_filename,
                    phase.name, output
                )

            # Log to message bus
            next_agent = (
                self.phases[i].agent_name if i < len(self.phases) else "orchestrator"
            )
            self.message_bus.send(
                phase.agent_name, next_agent, "document", output,
                metadata={"phase": phase.name},
            )

            previous_output = output

        # ── Done ──
        self._print_header("ALL PHASES COMPLETE")
        print(previous_output)
        print()

        # Save final report
        self._save_report(paths["reports"], "final_report.md",
                          "Final Report", previous_output)

        # Export message bus log
        bus_log_path = os.path.join(paths["sandbox"], "message_bus_log.md")
        self.message_bus.export_to_markdown(bus_log_path)
        self.log(f"📬 Message bus log: {bus_log_path}")

        print(f"\n📂 Sandbox: {paths['sandbox']}")
        print(f"   📁 Code:    {paths['code']}")
        print(f"   📁 Reports: {paths['reports']}")
        print(f"   📬 Log:     {bus_log_path}\n")

        return previous_output

    # ──────────────────────────────────────────
    # User approval
    # ──────────────────────────────────────────

    def _approval_loop(self, agent, phase: Phase, output: str) -> str:
        """Show output to user and optionally re-run with feedback."""
        print(f"\n{'='*60}")
        print(f"  {phase.name.upper()}")
        print(f"{'='*60}")
        print(output)
        print(f"{'='*60}\n")

        while True:
            feedback = input(
                "Is this correct? (yes / no / type your edits): "
            ).strip()

            if feedback.lower() in ("yes", "y", ""):
                print("  ✅ Approved!\n")
                return output

            # Get the edit request
            if feedback.lower() in ("no", "n"):
                edit_request = input("What should be changed? ").strip()
            else:
                edit_request = feedback

            # Re-run agent with feedback
            output = agent.run(
                f"The user wants changes.\n\n"
                f"Current output:\n{output}\n\n"
                f"User feedback:\n{edit_request}\n\n"
                "Update based on this feedback."
            )

            print(f"\n{'='*60}")
            print(f"  UPDATED {phase.name.upper()}")
            print(f"{'='*60}")
            print(output)
            print(f"{'='*60}\n")

    # ──────────────────────────────────────────
    # Sandbox management
    # ──────────────────────────────────────────

    def _create_sandbox(self) -> dict:
        """Create a timestamped sandbox folder structure."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sandbox = os.path.join(os.path.abspath(self.output_base), f"sandbox_{timestamp}")
        reports_dir = os.path.join(sandbox, "reports")
        code_dir = os.path.join(sandbox, "code")

        os.makedirs(reports_dir, exist_ok=True)
        os.makedirs(code_dir, exist_ok=True)

        return {
            "sandbox": sandbox,
            "reports": reports_dir,
            "code": code_dir,
        }

    def _save_report(self, reports_dir: str, filename: str, title: str, content: str):
        """Save a report as a markdown file."""
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"> Generated: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(content)
            f.write("\n")
        self.log(f"📄 Saved: {filename}")

    # ──────────────────────────────────────────
    # Display helpers
    # ──────────────────────────────────────────

    def log(self, message: str):
        c = self.COLORS
        print(f"{c['green']}[Orchestrator]{c['reset']} {message}")

    def _print_header(self, text: str):
        c = self.COLORS
        width = 60
        print(f"\n{c['header']}{'═' * width}")
        print(f"  {text}")
        print(f"{'═' * width}{c['reset']}\n")

    def _print_phase(self, text: str):
        c = self.COLORS
        print(f"\n{c['cyan']}{'─' * 60}")
        print(f"  {text}")
        print(f"{'─' * 60}{c['reset']}\n")
