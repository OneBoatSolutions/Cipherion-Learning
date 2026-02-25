"""
Agent: PRD Agent
==================
Takes an approved specification and produces a minimal
Product Requirements Document (PRD).

The PRD is the blueprint that the Planner agent uses
to break the project into implementable tasks.
"""

from framework.base_agent import BaseAgent
from openai import OpenAI


class PRDAgent(BaseAgent):
    """
    Generates a compact PRD from a specification.

    The PRD includes:
        - Brief summary
        - Functional requirements (numbered, concise)
        - File structure
        - Implementation order
    """

    def __init__(self, client: OpenAI):
        super().__init__(
            client=client,
            name="PRD Agent",
            system_prompt=self._build_system_prompt(),
            max_iterations=3,
            color="green",
        )

    def _build_system_prompt(self) -> str:
        return """You are a product manager. Given an approved specification, produce a SHORT PRD.

Your output MUST follow this EXACT format:

## Summary
2-3 sentences describing the project.

## Requirements
A numbered list (FR-1, FR-2, ...) of requirements. Keep them to ONE LINE each.
Maximum 5-6 requirements for simple projects. Only include P0 (must-have) items.

## File Structure
```
project_name/
├── file1.ext   # brief description
├── file2.ext   # brief description
└── ...
```
Keep it to 3-5 files for simple projects. Do NOT create separate files for
"state management", "accessibility", "pub/sub", etc. unless explicitly requested.

## Implementation Order
A numbered list of 2-3 steps, ordered by dependency. Group related work together.
For example: "1. Create HTML structure and CSS styling" — NOT separate tasks for each.

RULES:
- Do NOT add non-functional requirements, deployment sections, or glossaries.
- Do NOT split simple apps into 10+ files with complex architecture.
- A simple calculator = index.html + styles.css + script.js. That's it.
- Think MINIMAL. When done, call task_complete with your PRD."""
