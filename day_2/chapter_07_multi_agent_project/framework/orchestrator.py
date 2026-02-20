"""
Framework: Orchestrator
========================
The master controller that manages the multi-agent workflow.

The Orchestrator defines and executes the pipeline:
    User Input → Clarifier → PRD Agent → Planner → Coder(s) → Done

It uses the MessageBus to route data between agents and manages
the overall state of the project.
"""

from openai import OpenAI
from .message_bus import MessageBus


class Orchestrator:
    """
    Coordinates the multi-agent workflow.

    The orchestrator:
        1. Manages the pipeline of agents
        2. Routes messages between agents
        3. Handles user interaction (for the clarification step)
        4. Reports progress to the console
    """

    COLORS = {
        "header": "\033[1;97m",  # Bold white
        "reset":  "\033[0m",
        "dim":    "\033[2m",
        "green":  "\033[92m",
        "yellow": "\033[93m",
        "cyan":   "\033[96m",
    }

    def __init__(self, client: OpenAI):
        self.client = client
        self.message_bus = MessageBus()
        self.agents = {}

    def register_agent(self, name: str, agent):
        """Register an agent by name."""
        self.agents[name] = agent

    def run(self, user_input: str):
        """
        Execute the full multi-agent pipeline.

        Args:
            user_input: The user's raw problem statement.
        """
        self._print_header("MULTI-AGENT SOFTWARE DEVELOPMENT SYSTEM")
        print(f"  Input: {user_input}\n")

        # ═══════════════════════════════════════
        # PHASE 1: Clarification
        # ═══════════════════════════════════════
        self._print_phase("Phase 1: Requirement Clarification")

        clarifier = self.agents.get("clarifier")
        if not clarifier:
            raise RuntimeError("Clarifier agent not registered.")

        # The clarifier elaborates the problem and produces a spec
        elaborated_spec = clarifier.run(
            f"The user wants to build the following:\n\n{user_input}\n\n"
            "Elaborate this into a detailed, structured specification. "
            "Cover: purpose, features, tech stack, user flows, and edge cases. "
            "Be thorough but concise."
        )

        # Show the elaborated spec to the user and get feedback
        print(f"\n{'='*60}")
        print("  ELABORATED SPECIFICATION")
        print(f"{'='*60}")
        print(elaborated_spec)
        print(f"{'='*60}\n")

        # Interactive feedback loop
        while True:
            feedback = input(
                "Is this specification correct? (yes / no / type your edits): "
            ).strip()

            if feedback.lower() in ("yes", "y", ""):
                print("  ✅ Specification approved!\n")
                break
            elif feedback.lower() in ("no", "n"):
                additional = input("What should be changed? ").strip()
                elaborated_spec = clarifier.run(
                    f"The user wants changes to the specification.\n\n"
                    f"Current spec:\n{elaborated_spec}\n\n"
                    f"User feedback:\n{additional}\n\n"
                    "Update the specification based on this feedback."
                )
                print(f"\n{'='*60}")
                print("  UPDATED SPECIFICATION")
                print(f"{'='*60}")
                print(elaborated_spec)
                print(f"{'='*60}\n")
            else:
                # Treat the input as direct edits
                elaborated_spec = clarifier.run(
                    f"The user wants changes to the specification.\n\n"
                    f"Current spec:\n{elaborated_spec}\n\n"
                    f"User feedback:\n{feedback}\n\n"
                    "Update the specification based on this feedback."
                )
                print(f"\n{'='*60}")
                print("  UPDATED SPECIFICATION")
                print(f"{'='*60}")
                print(elaborated_spec)
                print(f"{'='*60}\n")

        self.message_bus.send("clarifier", "prd_agent", "document", elaborated_spec)

        # ═══════════════════════════════════════
        # PHASE 2: PRD Generation
        # ═══════════════════════════════════════
        self._print_phase("Phase 2: PRD Generation")

        prd_agent = self.agents.get("prd_agent")
        if not prd_agent:
            raise RuntimeError("PRD agent not registered.")

        prd_document = prd_agent.run(
            f"Create a detailed Product Requirements Document (PRD) based on "
            f"this approved specification:\n\n{elaborated_spec}"
        )

        print(f"\n{'='*60}")
        print("  PRODUCT REQUIREMENTS DOCUMENT")
        print(f"{'='*60}")
        print(prd_document)
        print(f"{'='*60}\n")

        self.message_bus.send("prd_agent", "planner", "document", prd_document)

        # ═══════════════════════════════════════
        # PHASE 3: Task Planning & Code Execution
        # ═══════════════════════════════════════
        self._print_phase("Phase 3: Task Planning & Code Generation")

        planner = self.agents.get("planner")
        if not planner:
            raise RuntimeError("Planner agent not registered.")

        # The planner breaks the PRD into tasks and delegates to the coder
        final_report = planner.run(
            f"You have a PRD to implement. Break it down into coding tasks "
            f"and use your tools to assign each task to the coding agent.\n\n"
            f"PRD:\n{prd_document}"
        )

        # ═══════════════════════════════════════
        # DONE
        # ═══════════════════════════════════════
        self._print_header("ALL PHASES COMPLETE")
        print(final_report)
        print()

        return final_report

    # ──────────────────────────────────────────
    # Display helpers
    # ──────────────────────────────────────────

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
