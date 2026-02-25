"""
Tools: Sandbox Path Management
================================
Global sandbox path for all file/shell/search tools.

When set, ALL tool paths are resolved relative to the sandbox root.
The LLM/agent just says "index.html" and tools auto-resolve it to
"output/sandbox_xxx/code/index.html".
"""

import os

# Module-level sandbox root — set by the orchestrator before running agents
_sandbox_root: str | None = None


def set_sandbox_root(path: str):
    """Set the global sandbox root directory for all tools."""
    global _sandbox_root
    _sandbox_root = os.path.abspath(path)
    os.makedirs(_sandbox_root, exist_ok=True)


def get_sandbox_root() -> str | None:
    """Get the current sandbox root directory."""
    return _sandbox_root


def resolve_path(user_path: str) -> str:
    """
    Resolve a user-provided path to an absolute path within the sandbox.

    If a sandbox root is set, relative paths are resolved inside it.
    Absolute paths that are already inside the sandbox are kept as-is.
    If no sandbox is set, falls back to os.path.abspath() (original behavior).

    Args:
        user_path: The path provided by the LLM/agent.

    Returns:
        Absolute path, constrained to the sandbox when possible.
    """
    if _sandbox_root is None:
        return os.path.abspath(user_path)

    # If it's already an absolute path inside the sandbox, keep it
    abs_path = os.path.abspath(user_path)
    if abs_path.startswith(_sandbox_root):
        return abs_path

    # Otherwise, treat it as relative to the sandbox
    resolved = os.path.normpath(os.path.join(_sandbox_root, user_path))

    # Safety: prevent path traversal outside sandbox
    if not resolved.startswith(_sandbox_root):
        resolved = os.path.join(_sandbox_root, os.path.basename(user_path))

    return resolved
