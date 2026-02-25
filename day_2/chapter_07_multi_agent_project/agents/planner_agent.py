"""
Agent: Planner (Master Agent)
===============================
The master orchestration agent.

Takes a PRD, breaks it into a SMALL number of coding tasks,
and delegates each task to the Coder agent.

Tracks files created by earlier tasks and passes that context
to subsequent tasks so the coder can build on previous work.
"""

import json
import os
from framework.base_agent import BaseAgent
from openai import OpenAI
from tools.sandbox import get_sandbox_root


class PlannerAgent(BaseAgent):
    """
    Master agent that divides a PRD into tasks and assigns them to the Coder.

    The Planner:
        1. Reads the PRD
        2. Creates 2-3 consolidated tasks (not 12 micro-tasks)
        3. For each task, calls assign_task_to_coder with file context
        4. Produces a brief summary when done
    """

    def __init__(self, client: OpenAI, coder_agent=None):
        super().__init__(
            client=client,
            name="Planner",
            system_prompt=self._build_system_prompt(),
            max_iterations=10,
            color="yellow",
        )
        self.coder_agent = coder_agent
        self.message_bus = None  # Set by orchestrator at runtime
        self._task_results = []
        self._created_files = []  # Track files created across tasks

        # Register the assign_task tool
        self.tool_registry.register(
            name="assign_task_to_coder",
            description=(
                "Assign a coding task to the Coder agent. "
                "The coder will execute the task and return the result. "
                "Call this once per task, in order. MAXIMUM 3 tasks total."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task_number": {
                        "type": "integer",
                        "description": "The task number (1, 2, or 3).",
                    },
                    "task_title": {
                        "type": "string",
                        "description": "Short title for the task.",
                    },
                    "task_description": {
                        "type": "string",
                        "description": (
                            "Detailed description of what the coder should implement. "
                            "Include ALL file names, ALL code content requirements, "
                            "and ALL details in ONE description. The coder should be able "
                            "to create all files for this task in one go."
                        ),
                    },
                },
                "required": ["task_number", "task_title", "task_description"],
            },
            func=self._assign_task,
        )

    def _build_system_prompt(self) -> str:
        return """You are a technical project manager.

Given a PRD, break it into AT MOST 2-3 coding tasks and assign each to the Coder.

CRITICAL RULES:
- Create AT MOST 3 tasks total. Fewer is better.
- COMBINE related work into single tasks. For example:
  - Task 1: "Create HTML structure with CSS styling" (creates index.html AND styles.css)
  - Task 2: "Implement all JavaScript logic" (creates script.js with ALL functionality)
  - Task 3 (optional): "Final integration and testing"
- Do NOT create a separate task for each file or each feature.
- Each task description must include EVERYTHING the coder needs to create ALL files for that task.
- The coder uses simple filenames (e.g. 'index.html', 'styles.css') — no full paths needed.
- Assign tasks ONE AT A TIME using assign_task_to_coder.
- After all tasks complete, call task_complete with a brief summary.

BAD EXAMPLE (too many tasks):
  Task 1: Create project scaffold
  Task 2: Create state module
  Task 3: Create engine module
  Task 4: Create UI module
  ... (12 total tasks)

GOOD EXAMPLE (consolidated):
  Task 1: Create HTML and CSS (index.html + styles.css)
  Task 2: Implement JavaScript (script.js with all logic)"""

    def _get_file_context(self) -> str:
        """Build a context string of previously created files."""
        if not self._created_files:
            return ""

        context = "\n\nPREVIOUSLY CREATED FILES (you can read these with read_file):\n"
        for f in self._created_files:
            context += f"  - {f}\n"
        return context

    def _scan_sandbox_files(self) -> list[str]:
        """Scan the sandbox for all files created so far."""
        sandbox = get_sandbox_root()
        if not sandbox or not os.path.isdir(sandbox):
            return []

        files = []
        for root, dirs, filenames in os.walk(sandbox):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in filenames:
                rel = os.path.relpath(os.path.join(root, f), sandbox)
                files.append(rel)
        return files

    def _assign_task(self, task_number: int, task_title: str, task_description: str) -> dict:
        """Delegate a task to the Coder agent."""
        self.log(f"📌 Task {task_number}: {task_title}")

        # Log task assignment on the message bus
        if self.message_bus:
            self.message_bus.send(
                "planner", "coder", "task",
                f"Task {task_number}: {task_title}\n\n{task_description}",
                metadata={"task_number": task_number, "task_title": task_title},
            )

        if not self.coder_agent:
            return {
                "task_number": task_number,
                "status": "error",
                "error": "No coder agent available.",
            }

        # Build task with context of previously created files
        file_context = self._get_file_context()
        full_task = f"TASK {task_number}: {task_title}\n\n{task_description}{file_context}"

        # Run the coder agent with this specific task
        coder_result = self.coder_agent.run(full_task)

        # Update the list of created files by scanning the sandbox
        self._created_files = self._scan_sandbox_files()

        result = {
            "task_number": task_number,
            "task_title": task_title,
            "status": "completed",
            "files_created": self._created_files.copy(),
            "coder_output": coder_result[:500],   # Truncate for context window
        }
        self._task_results.append(result)

        # Log task result on the message bus
        if self.message_bus:
            self.message_bus.send(
                "coder", "planner", "result",
                coder_result[:1000],
                metadata={
                    "task_number": task_number,
                    "status": "completed",
                    "files": self._created_files.copy(),
                },
            )

        self.log(f"✅ Task {task_number} completed by Coder")
        self.log(f"   📁 Files in sandbox: {', '.join(self._created_files) or 'none'}")
        return result
