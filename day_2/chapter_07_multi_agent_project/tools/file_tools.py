"""
Tools: File Operations
========================
Tools for reading, writing, listing, and creating files.

These are real tools that the Coder agent uses to create actual code files.
Built from scratch — no external tool libraries.
"""

import os


def read_file(file_path: str) -> dict:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read.

    Returns:
        Dict with 'path' and 'content', or 'error'.
    """
    try:
        abs_path = os.path.abspath(file_path)
        if not os.path.isfile(abs_path):
            return {"path": file_path, "error": f"File not found: {abs_path}"}

        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "path": abs_path,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
        }
    except Exception as e:
        return {"path": file_path, "error": str(e)}


def write_file(file_path: str, content: str) -> dict:
    """
    Write content to a file. Creates parent directories if needed.

    Args:
        file_path: Path to the file.
        content:   The content to write.

    Returns:
        Dict with 'path', 'status', and 'size_bytes'.
    """
    try:
        abs_path = os.path.abspath(file_path)

        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(abs_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "path": abs_path,
            "status": "written",
            "size_bytes": len(content.encode("utf-8")),
        }
    except Exception as e:
        return {"path": file_path, "error": str(e)}


def list_directory(directory_path: str) -> dict:
    """
    List files and directories in a given path.

    Args:
        directory_path: Path to the directory to list.

    Returns:
        Dict with 'path' and 'entries' (list of entry dicts).
    """
    try:
        abs_path = os.path.abspath(directory_path)
        if not os.path.isdir(abs_path):
            return {"path": directory_path, "error": f"Not a directory: {abs_path}"}

        entries = []
        for item in sorted(os.listdir(abs_path)):
            full_path = os.path.join(abs_path, item)
            entry = {
                "name": item,
                "type": "directory" if os.path.isdir(full_path) else "file",
            }
            if os.path.isfile(full_path):
                entry["size_bytes"] = os.path.getsize(full_path)
            entries.append(entry)

        return {"path": abs_path, "entries": entries, "count": len(entries)}
    except Exception as e:
        return {"path": directory_path, "error": str(e)}


def create_directory(directory_path: str) -> dict:
    """
    Create a directory (and any parent directories).

    Args:
        directory_path: Path to the directory to create.

    Returns:
        Dict with 'path' and 'status'.
    """
    try:
        abs_path = os.path.abspath(directory_path)
        os.makedirs(abs_path, exist_ok=True)
        return {"path": abs_path, "status": "created"}
    except Exception as e:
        return {"path": directory_path, "error": str(e)}


# ──────────────────────────────────────────────
# Tool schemas for the OpenAI API
# ──────────────────────────────────────────────

FILE_TOOL_SCHEMAS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to read."}
            },
            "required": ["file_path"],
        },
        "func": read_file,
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates parent directories automatically.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to write."},
                "content":   {"type": "string", "description": "The content to write to the file."},
            },
            "required": ["file_path", "content"],
        },
        "func": write_file,
    },
    {
        "name": "list_directory",
        "description": "List all files and subdirectories in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Path to the directory to list."}
            },
            "required": ["directory_path"],
        },
        "func": list_directory,
    },
    {
        "name": "create_directory",
        "description": "Create a directory (including parent directories if needed).",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Path to the directory to create."}
            },
            "required": ["directory_path"],
        },
        "func": create_directory,
    },
]
