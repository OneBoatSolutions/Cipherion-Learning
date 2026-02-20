"""
Agent: Planner (Master Agent)
===============================
The master orchestration agent.

Takes a PRD, breaks it into coding tasks, and delegates each task
to the Coder agent. Monitors progress and handles task sequencing.
"""

import json
import os
from framework.base_agent import BaseAgent
from openai import OpenAI


class PlannerAgent(BaseAgent):
    """
    Master agent that divides a PRD into tasks and assigns them to the Coder.

    The Planner:
        1. Reads the PRD
        2. Creates a numbered task list
        3. For each task, calls assign_task_to_coder
        4. Collects results and produces a summary
    """

    def __init__(self, client: OpenAI, coder_agent=None):
        super().__init__(
            client=client,
            name="Planner",
            system_prompt=self._build_system_prompt(),
            model=os.getenv("OPENAI_MODEL"),
            max_iterations=25,       # May need many iterations for many tasks
            color="yellow",
        )
        self.coder_agent = coder_agent
        self._task_results = []

        # Register the assign_task tool
        self.tool_registry.register(
            name="assign_task_to_coder",
            description=(
                "Assign a specific coding task to the Coder agent. "
                "The coder will execute the task and return the result. "
                "Call this once per task, in the correct order."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task_number": {
                        "type": "integer",
                        "description": "The task number (e.g. 1, 2, 3...).",
                    },
                    "task_title": {
                        "type": "string",
                        "description": "Short title for the task.",
                    },
                    "task_description": {
                        "type": "string",
                        "description": (
                            "Detailed description of what the coder should do. "
                            "Include: which files to create/modify, what code to write, "
                            "and any specific requirements."
                        ),
                    },
                },
                "required": ["task_number", "task_title", "task_description"],
            },
            func=self._assign_task,
        )

    def _build_system_prompt(self) -> str:
        return """You are a senior technical project manager and architect.

Given a PRD (Product Requirements Document), you must:

1. **Analyze the PRD** carefully
2. **Break it into ordered coding tasks** — each task should be:
   - Small enough for a single coding session
   - Ordered by dependency (foundational tasks first)
   - Specific about which files to create and what code to write
3. **Assign each task** to the Coder using the assign_task_to_coder tool
4. **Track progress** — after all tasks are assigned, summarize what was accomplished

IMPORTANT RULES:
- Assign tasks ONE AT A TIME in order (the coder needs previous files to exist)
- Each task description must be VERY specific (filenames, function signatures, etc.)
- Start with project setup (create directories, config files)
- Then build core modules, then features, then integration

When ALL tasks are assigned and completed, use task_complete with a final summary."""

    def _assign_task(self, task_number: int, task_title: str, task_description: str) -> dict:
        """Delegate a task to the Coder agent."""
        self.log(f"📌 Task {task_number}: {task_title}")

        if not self.coder_agent:
            return {
                "task_number": task_number,
                "status": "error",
                "error": "No coder agent available.",
            }

        # Run the coder agent with this specific task
        coder_result = self.coder_agent.run(
            f"TASK {task_number}: {task_title}\n\n{task_description}"
        )

        result = {
            "task_number": task_number,
            "task_title": task_title,
            "status": "completed",
            "coder_output": coder_result[:500],   # Truncate for context window
        }
        self._task_results.append(result)

        self.log(f"✅ Task {task_number} completed by Coder")
        return result
