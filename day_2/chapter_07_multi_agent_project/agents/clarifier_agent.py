"""
Agent: Clarifier
==================
Takes the user's raw problem statement, elaborates it into a
detailed specification, and incorporates user feedback.

This is the first agent in the pipeline. Its job is to ensure
the requirements are clear and complete BEFORE any code is written.
"""

from framework.base_agent import BaseAgent
from openai import OpenAI
import os

class ClarifierAgent(BaseAgent):
    """
    Elaborates vague problem statements into detailed specifications.

    The Clarifier:
        1. Analyses the user's raw input
        2. Identifies ambiguities and missing details
        3. Produces a structured specification covering:
           - Purpose & goals
           - Features & functionality
           - Technical considerations
           - User flows
           - Edge cases & constraints
    """

    def __init__(self, client: OpenAI):
        super().__init__(
            client=client,
            name="Clarifier",
            system_prompt=self._build_system_prompt(),
            model=os.getenv("OPENAI_MODEL"),
            max_iterations=5,
            color="blue",
        )

    def _build_system_prompt(self) -> str:
        return """You are a senior requirements analyst. Your job is to take a raw, 
possibly vague problem statement and elaborate it into a clear, detailed, 
structured specification.

When analyzing a problem statement, you MUST cover:

1. **Purpose & Goals** — What is the software trying to achieve? What problem does it solve?
2. **Core Features** — List every feature with a brief description
3. **Technical Stack** — Recommended programming language, frameworks, libraries
4. **User Flows** — How will users interact with the software? Step by step.
5. **Data Model** — What data needs to be stored or processed?
6. **Edge Cases & Constraints** — What could go wrong? What are the limits?
7. **Out of Scope** — What is explicitly NOT included in this version?

Format your output as a clean, well-structured markdown document.
Be thorough but concise. Don't add unnecessary fluff.
Focus on actionable, implementable requirements.

When you have completed your specification, use the task_complete tool to submit it."""
