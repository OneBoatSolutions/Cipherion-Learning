"""
Agent: Coder
===============
The coding agent that actually writes code files.

Receives a specific coding task from the Planner and uses
file tools, shell tools, and search tools to implement it.
"""

import os
from framework.base_agent import BaseAgent
from tools import ALL_TOOL_SCHEMAS
from openai import OpenAI


class CoderAgent(BaseAgent):
    """
    Writes code based on assigned tasks.

    The Coder has access to:
        - File tools: read, write, list, create directories
        - Shell tools: run commands (install packages, run tests)
        - Search tools: find files, grep for patterns

    It uses these tools to actually create and modify source code files.
    """

    def __init__(self, client: OpenAI, project_dir: str = "./output"):
        super().__init__(
            client=client,
            name="Coder",
            system_prompt=self._build_system_prompt(project_dir),
            model=os.getenv("OPENAI_MODEL"),
            max_iterations=15,
            color="magenta",
        )
        self.project_dir = project_dir

        # Register all coding tools from the tools package
        for tool_def in ALL_TOOL_SCHEMAS:
            self.tool_registry.register(
                name=tool_def["name"],
                description=tool_def["description"],
                parameters=tool_def["parameters"],
                func=tool_def["func"],
            )

    def _build_system_prompt(self, project_dir: str) -> str:
        return f"""You are an expert software developer. You write clean, well-documented,
production-quality code.

WORKING DIRECTORY: {project_dir}
All file paths should be relative to or within this directory.

When given a coding task:
1. **Understand** the requirements fully
2. **Plan** the file structure and code architecture
3. **Implement** by using write_file to create each file
4. **Verify** by reading back files or running commands if needed

CODE QUALITY RULES:
- Always include docstrings and comments
- Use meaningful variable and function names
- Handle errors gracefully
- Follow language-specific best practices
- Keep files focused and modular

IMPORTANT:
- Use write_file to create files (it auto-creates parent directories)
- Use read_file to check existing files before modifying
- Use list_directory to see what already exists
- When done implementing, use task_complete with a summary of what you created

Always write COMPLETE, WORKING code. Never use placeholder comments like "# TODO" 
or "# add implementation here"."""
