"""
Tools: Shell Commands
======================
Tool for executing shell commands with safety guards and timeout.

Commands automatically run inside the sandbox directory.
Built from scratch — no external tool libraries.
"""

import subprocess
import os
from .sandbox import get_sandbox_root


def run_command(command: str, cwd: str = None) -> dict:
    """
    Execute a shell command and return the output.
    Runs inside the sandbox directory by default.

    Safety measures:
        - Timeout of 30 seconds
        - Captures both stdout and stderr
        - Returns exit code
        - Blocks dangerous commands

    Args:
        command: The shell command to execute.
        cwd:     Working directory (defaults to sandbox root).

    Returns:
        Dict with 'command', 'stdout', 'stderr', 'exit_code'.
    """
    # Basic safety: block obviously dangerous commands
    dangerous = ["rm -rf /", "format ", "del /s /q", "shutdown", "mkfs"]
    for d in dangerous:
        if d in command.lower():
            return {
                "command": command,
                "error": f"Blocked: command contains dangerous pattern '{d}'",
            }

    try:
        # Default to sandbox root, fall back to cwd
        if cwd:
            abs_cwd = os.path.abspath(cwd)
        else:
            sandbox = get_sandbox_root()
            abs_cwd = sandbox if sandbox else os.path.abspath(".")

        # Ensure the cwd directory exists
        os.makedirs(abs_cwd, exist_ok=True)

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=abs_cwd,
        )

        return {
            "command": command,
            "cwd": abs_cwd,
            "stdout": result.stdout[:5000] if result.stdout else "",    # Cap output
            "stderr": result.stderr[:2000] if result.stderr else "",
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "error": "Command timed out after 30 seconds.",
        }
    except Exception as e:
        return {
            "command": command,
            "error": str(e),
        }


# ──────────────────────────────────────────────
# Tool schema
# ──────────────────────────────────────────────

SHELL_TOOL_SCHEMAS = [
    {
        "name": "run_command",
        "description": (
            "Execute a shell command and return stdout, stderr, and exit code. "
            "Commands run inside the project directory by default. "
            "Use this to run programs, install packages, or test code. "
            "Has a 30-second timeout."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
                "cwd": {
                    "type": "string",
                    "description": "Optional: working directory. Defaults to the project directory.",
                },
            },
            "required": ["command"],
        },
        "func": run_command,
    },
]
