"""
Agent: Clarifier
==================
Takes the user's raw problem statement, elaborates it into a
short, focused specification, and incorporates user feedback.

This is the first agent in the pipeline. Its job is to ensure
the requirements are clear and complete BEFORE any code is written.
"""

from framework.base_agent import BaseAgent
from openai import OpenAI


class ClarifierAgent(BaseAgent):
    """
    Elaborates vague problem statements into concise specifications.

    The Clarifier:
        1. Analyses the user's raw input
        2. Identifies the core features needed
        3. Produces a brief specification (purpose, features, tech)
    """

    def __init__(self, client: OpenAI):
        super().__init__(
            client=client,
            name="Clarifier",
            system_prompt=self._build_system_prompt(),
            max_iterations=3,
            color="blue",
        )

    def _build_system_prompt(self) -> str:
        return """You are a requirements analyst. Take the user's raw idea and produce a SHORT, focused specification.

Your output MUST follow this EXACT format and stay UNDER 150 words total:

## Purpose
One sentence describing what the app does.

## Features
A numbered list of 3-6 core features. Keep each to one line. No sub-features.

## Tech Stack
One line listing the technologies (e.g. "HTML5, CSS3, vanilla JavaScript").

## File Structure
A simple list of files to create (3-5 files max for simple projects).

RULES:
- Do NOT add accessibility modules, pub/sub patterns, strategy patterns, or complex architecture.
- Do NOT add "edge cases", "out of scope", "data models", "user flows", or "constraints" sections.
- Do NOT over-engineer. A calculator needs 3 files (HTML, CSS, JS), not 8.
- Keep it SIMPLE. Think MVP — minimum viable product.
- When done, call task_complete with your specification."""
