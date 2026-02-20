"""
Chapter 7: Multi-Agent CLI Software Development System
========================================================
The capstone project — a CLI tool that takes a problem statement and
builds software through a pipeline of AI agents.

Pipeline:
    User Input → Clarifier → PRD Agent → Planner → Coder → Output

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

from framework.orchestrator import Orchestrator
from agents.clarifier_agent import ClarifierAgent
from agents.prd_agent import PRDAgent
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent


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

    # ── Set up output directory ──
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    # ── Create agents ──
    clarifier = ClarifierAgent(client=client)
    prd_agent = PRDAgent(client=client)
    coder    = CoderAgent(client=client, project_dir=output_dir)
    planner  = PlannerAgent(client=client, coder_agent=coder)

    # ── Create orchestrator and register agents ──
    orchestrator = Orchestrator(client=client)
    orchestrator.register_agent("clarifier", clarifier)
    orchestrator.register_agent("prd_agent", prd_agent)
    orchestrator.register_agent("planner", planner)
    orchestrator.register_agent("coder", coder)

    # ── Run the pipeline ──
    try:
        result = orchestrator.run(user_input)
        print(f"\n📁 Output files written to: {output_dir}")
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
