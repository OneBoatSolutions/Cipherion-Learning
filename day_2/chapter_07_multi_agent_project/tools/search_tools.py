"""
Tools: Search & Grep
=====================
Tools for searching files by name and searching content within files.

All paths are automatically resolved to the sandbox directory.
"""

import os
import re
from .sandbox import resolve_path, get_sandbox_root


def search_files(directory: str = ".", pattern: str = "") -> dict:
    """
    Search for files matching a pattern in a directory.
    Defaults to the sandbox root.

    Args:
        directory: The directory to search in (resolved to sandbox).
        pattern:   A substring to match against file names (case-insensitive).

    Returns:
        Dict with 'matches' (list of file paths).
    """
    try:
        abs_dir = resolve_path(directory)
        if not os.path.isdir(abs_dir):
            return {"directory": directory, "error": f"Not a directory: {abs_dir}"}

        matches = []
        pattern_lower = pattern.lower()

        for root, dirs, files in os.walk(abs_dir):
            # Skip hidden directories and common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', '__pycache__', 'venv', '.git')]

            for f in files:
                if pattern_lower in f.lower():
                    matches.append(os.path.join(root, f))

                if len(matches) >= 50:   # Cap results
                    break
            if len(matches) >= 50:
                break

        return {
            "directory": abs_dir,
            "pattern": pattern,
            "matches": matches,
            "count": len(matches),
        }
    except Exception as e:
        return {"directory": directory, "error": str(e)}


def grep_in_file(file_path: str, search_term: str) -> dict:
    """
    Search for a term within a file and return matching lines.

    Args:
        file_path:   Path to the file to search (resolved to sandbox).
        search_term: The string or regex to search for.

    Returns:
        Dict with 'matches' (list of {line_number, line_content}).
    """
    try:
        abs_path = resolve_path(file_path)
        if not os.path.isfile(abs_path):
            return {"path": file_path, "error": f"File not found: {abs_path}"}

        matches = []
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                if re.search(search_term, line, re.IGNORECASE):
                    matches.append({
                        "line_number": line_num,
                        "content": line.rstrip(),
                    })
                if len(matches) >= 50:
                    break

        return {
            "path": abs_path,
            "search_term": search_term,
            "matches": matches,
            "count": len(matches),
        }
    except Exception as e:
        return {"path": file_path, "error": str(e)}


# ──────────────────────────────────────────────
# Tool schemas
# ──────────────────────────────────────────────

SEARCH_TOOL_SCHEMAS = [
    {
        "name": "search_files",
        "description": "Search for files by name pattern in the project (recursive). Use '.' to search the whole project.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to search in, or '.' for project root."},
                "pattern":   {"type": "string", "description": "Filename substring to match (case-insensitive)."},
            },
            "required": ["directory", "pattern"],
        },
        "func": search_files,
    },
    {
        "name": "grep_in_file",
        "description": "Search for a text pattern inside a file. Returns matching line numbers and content.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path":   {"type": "string", "description": "Filename or relative path to search in."},
                "search_term": {"type": "string", "description": "Text or regex pattern to search for."},
            },
            "required": ["file_path", "search_term"],
        },
        "func": grep_in_file,
    },
]
