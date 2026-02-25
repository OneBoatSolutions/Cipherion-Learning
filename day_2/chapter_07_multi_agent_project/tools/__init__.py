"""
Tools Package Init
"""
from .file_tools import FILE_TOOL_SCHEMAS
from .shell_tools import SHELL_TOOL_SCHEMAS
from .search_tools import SEARCH_TOOL_SCHEMAS
from .sandbox import set_sandbox_root, get_sandbox_root

# All tool schemas combined — easy to register in bulk
ALL_TOOL_SCHEMAS = FILE_TOOL_SCHEMAS + SHELL_TOOL_SCHEMAS + SEARCH_TOOL_SCHEMAS

__all__ = [
    "FILE_TOOL_SCHEMAS",
    "SHELL_TOOL_SCHEMAS",
    "SEARCH_TOOL_SCHEMAS",
    "ALL_TOOL_SCHEMAS",
    "set_sandbox_root",
    "get_sandbox_root",
]
