"""
Chapter 7: Multi-Agent CLI Software Development System
========================================================
The capstone project — a CLI tool that takes a problem statement and
builds software through a pipeline of AI agents.

Pipeline:
    User Input → Clarifier → PRD Agent → Planner → Coder → Output

This file defines the SPECIFIC pipeline using the GENERIC orchestrator.
The orchestrator itself knows nothing about these agents — it just runs
phases sequentially.

Usage:
    python main.py "Build a todo app with Flask"
    python main.py                                  # Interactive mode

All agents and tools are built from scratch — no external agent frameworks.

Prerequisites:
    pip install openai python-dotenv
    Create a .env file with: OPENAI_API_KEY=sk-your-key-here
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.orchestrator import Orchestrator, Phase
from agents.clarifier_agent import ClarifierAgent
from agents.prd_agent import PRDAgent
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent


def build_pipeline(orchestrator: Orchestrator):
    """
    Define the software development pipeline.

    This is where the specific workflow is configured.
    Change this function to create different pipelines.
    """

    # Phase 1: Clarify the user's requirements
    orchestrator.add_phase(Phase(
        name="Requirement Clarification",
        agent_name="clarifier",
        prompt_template=(
            "The user wants to build the following:\n\n{user_input}\n\n"
            "Elaborate this into a concise specification. "
            "Keep it short: purpose, features, tech stack, file structure."
        ),
        report_filename="01_specification.md",
        needs_approval=True,
    ))

    # Phase 2: Generate a PRD from the approved spec
    orchestrator.add_phase(Phase(
        name="PRD Generation",
        agent_name="prd_agent",
        prompt_template=(
            "Create a concise Product Requirements Document (PRD) based on "
            "this approved specification:\n\n{previous_output}"
        ),
        report_filename="02_prd.md",
    ))

    # Phase 3: Plan tasks and generate code
    orchestrator.add_phase(Phase(
        name="Task Planning & Code Generation",
        agent_name="planner",
        prompt_template=(
            "You have a PRD to implement. Break it down into coding tasks "
            "and use your tools to assign each task to the coding agent.\n\n"
            "PRD:\n{previous_output}"
        ),
        report_filename="03_task_plan.md",
        setup_sandbox=True,
        pass_message_bus=True,
    ))


def main():
    """Entry point for the multi-agent system."""

    # ── Load environment ──
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment.")
        print("   Create a .env file with: OPENAI_API_KEY=sk-your-key-here")
        sys.exit(1)

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL")     
    )

    # ── Get the problem statement ──
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        print("=" * 60)
        print("  🤖 Multi-Agent Software Development System")
        print("=" * 60)
        print("\nDescribe the software you want to build.\n")
        user_input = input("Your idea: ").strip()
        if not user_input:
            print("No input provided. Exiting.")
            sys.exit(0)

    # ── Set up output base directory ──
    output_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    # ── Create agents ──
    clarifier = ClarifierAgent(client=client)
    prd_agent = PRDAgent(client=client)
    coder    = CoderAgent(client=client)
    planner  = PlannerAgent(client=client, coder_agent=coder)

    # ── Create orchestrator, register agents, and define pipeline ──
    orchestrator = Orchestrator(client=client, output_base=output_base)
    orchestrator.register_agent("clarifier", clarifier)
    orchestrator.register_agent("prd_agent", prd_agent)
    orchestrator.register_agent("planner", planner)
    orchestrator.register_agent("coder", coder)

    # Define the pipeline — this is the only project-specific part
    build_pipeline(orchestrator)

    # ── Run the pipeline ──
    try:
        result = orchestrator.run(user_input)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
