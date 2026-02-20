"""
Agent: PRD Agent
==================
Takes an approved specification and produces a formal
Product Requirements Document (PRD).

The PRD is the blueprint that the Planner agent uses
to break the project into implementable tasks.
"""

import os
from framework.base_agent import BaseAgent
from openai import OpenAI


class PRDAgent(BaseAgent):
    """
    Generates a structured Product Requirements Document from a specification.

    The PRD includes:
        - Executive summary
        - Functional requirements (numbered)
        - Non-functional requirements
        - Technical architecture
        - File/module structure
        - API definitions
        - Acceptance criteria
    """

    def __init__(self, client: OpenAI):
        super().__init__(
            client=client,
            name="PRD Agent",
            system_prompt=self._build_system_prompt(),
            model=os.getenv("OPENAI_MODEL"),
            max_iterations=5,
            color="green",
        )

    def _build_system_prompt(self) -> str:
        return """You are a senior product manager who writes excellent PRDs.

Given an approved specification, produce a detailed Product Requirements Document with:

## 1. Executive Summary
One paragraph overview of the project.

## 2. Functional Requirements
Numbered list (FR-1, FR-2, ...) of every feature with:
- Description
- Acceptance criteria
- Priority (P0 = must-have, P1 = should-have, P2 = nice-to-have)

## 3. Non-Functional Requirements
Performance, security, usability requirements.

## 4. Technical Architecture
- Programming language and frameworks
- Project structure (list of files/modules)
- Key design patterns to use

## 5. File Structure
```
project_name/
├── file1.py       # description
├── file2.py       # description
└── ...
```

## 6. Implementation Order
Ordered list of which components to build first (dependencies first).

Be specific and actionable. Every requirement should be implementable by a developer.
When you have completed the PRD, use the task_complete tool to submit it."""
