"""
Framework: Tool Registry
==========================
A registry that manages tool registration, schema generation, and execution.

Built from scratch — this is the engine that powers tool use across all agents.

Features:
    - Register Python functions as tools with JSON schemas
    - Auto-validate tool calls
    - Execute tools by name with arguments
    - Generate OpenAI-compatible tool schemas
"""


class ToolRegistry:
    """
    Manages the registration and execution of tools.

    Each tool is:
        - A Python callable (the function to run)
        - A JSON schema (tells the model what parameters the function accepts)
        - A name and description (helps the model decide when to use it)
    """

    def __init__(self):
        self._tools: dict[str, dict] = {}
        # Each entry: { "func": callable, "schema": dict }

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        func: callable,
    ):
        """
        Register a tool.

        Args:
            name:        Unique tool name (e.g. "read_file")
            description: What the tool does (shown to the model)
            parameters:  JSON Schema for the function parameters
            func:        The Python callable to execute
        """
        self._tools[name] = {
            "func": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            },
        }

    def get_schemas(self) -> list[dict]:
        """Return all tool schemas in OpenAI API format."""
        return [t["schema"] for t in self._tools.values()]

    def get_names(self) -> list[str]:
        """Return all registered tool names."""
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def execute(self, name: str, arguments: dict) -> any:
        """
        Execute a tool by name with the given arguments.

        Args:
            name:      The tool function name.
            arguments: Dict of keyword arguments.

        Returns:
            Whatever the tool function returns.

        Raises:
            ValueError: If the tool is not registered.
        """
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")

        func = self._tools[name]["func"]
        return func(**arguments)

    def __len__(self):
        return len(self._tools)

    def __repr__(self):
        return f"ToolRegistry(tools={self.get_names()})"
