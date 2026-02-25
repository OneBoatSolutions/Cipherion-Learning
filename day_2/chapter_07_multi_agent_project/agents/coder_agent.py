"""
Agent: Coder
===============
The coding agent that actually writes code files.

Receives a specific coding task from the Planner and uses
file tools, shell tools, and search tools to implement it.

All file paths are handled by the tools — the coder just uses
simple filenames like "index.html" and the sandbox handles the rest.
"""

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

    It uses these tools to create and modify source code files.
    All file operations are automatically sandboxed.
    """

    def __init__(self, client: OpenAI, project_dir: str = "./output"):
        super().__init__(
            client=client,
            name="Coder",
            system_prompt=self._build_system_prompt(),
            max_iterations=10,
            color="magenta",
        )

        # Register all coding tools from the tools package
        for tool_def in ALL_TOOL_SCHEMAS:
            self.tool_registry.register(
                name=tool_def["name"],
                description=tool_def["description"],
                parameters=tool_def["parameters"],
                func=tool_def["func"],
            )

    def _build_system_prompt(self) -> str:
        return """You are an expert software developer. Write clean, working code.

All file operations are automatically sandboxed — just use simple filenames.
For example: write_file("index.html", ...) or write_file("src/app.js", ...).
Do NOT use absolute paths. The tools handle directory creation automatically.

AVAILABLE TOOLS (use ONLY these exact names):
- write_file(file_path, content) — Create/overwrite a file. Just provide the filename.
- read_file(file_path) — Read a previously created file.
- list_directory(directory_path) — List files. Use '.' for project root.
- create_directory(directory_path) — Create a subdirectory.
- run_command(command) — Run a shell command in the project directory.
- search_files(directory, pattern) — Search for files by name.
- grep_in_file(file_path, search_term) — Search inside a file.
- task_complete(result) — Call when ALL files are written. REQUIRED.

EFFICIENCY RULES (you have limited API calls):
1. Write files DIRECTLY. Do NOT call list_directory or read_file before creating NEW files.
2. If the task mentions "previously created files", you MAY use read_file to check them.
3. Create MULTIPLE files in ONE response — batch several write_file calls together.
4. After writing all files, IMMEDIATELY call task_complete.
5. NEVER invent tool names. Only use the exact names listed above.

WORKFLOW:
1. Receive task → write all needed files immediately → call task_complete.
2. If building on previous files, read them first, then write your files.
3. That's it. Don't over-think it.

Write COMPLETE, WORKING code. No placeholder comments like "// TODO"."""
