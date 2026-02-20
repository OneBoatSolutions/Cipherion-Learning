"""
Tools: Shell Commands
======================
Tool for executing shell commands with safety guards and timeout.

Built from scratch — provides the Coder agent with the ability to
run commands like 'pip install', 'python script.py', etc.
"""

import subprocess
import os


def run_command(command: str, cwd: str = ".") -> dict:
    """
    Execute a shell command and return the output.

    Safety measures:
        - Timeout of 30 seconds
        - Captures both stdout and stderr
        - Returns exit code

    Args:
        command: The shell command to execute.
        cwd:     Working directory (defaults to current).

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
        abs_cwd = os.path.abspath(cwd)
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
                    "description": "Working directory for the command. Defaults to current directory.",
                },
            },
            "required": ["command"],
        },
        "func": run_command,
    },
]
