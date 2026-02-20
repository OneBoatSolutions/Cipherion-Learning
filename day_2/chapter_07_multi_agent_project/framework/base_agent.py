"""
Framework: Base Agent
======================
The abstract base class for ALL agents in the system.

Built from scratch — no external agent frameworks.

Features:
    - Agentic loop with configurable max iterations
    - Automatic tool registration and execution
    - Built-in 'task_complete' tool for explicit completion
    - Conversation memory within a run
    - Coloured console logging for each agent
"""

import json
import os
from openai import OpenAI
from .tool_registry import ToolRegistry


class BaseAgent:
    """
    Base class for all agents in the multi-agent system.

    Subclasses should:
        1. Set self.name and self.system_prompt in __init__
        2. Register tools via self.tool_registry.register(...)
        3. Optionally override pre_run() and post_run() hooks
    """

    # ANSI colour codes for distinguishable agent logs
    COLORS = {
        "blue":    "\033[94m",
        "green":   "\033[92m",
        "yellow":  "\033[93m",
        "magenta": "\033[95m",
        "cyan":    "\033[96m",
        "red":     "\033[91m",
        "reset":   "\033[0m",
        "bold":    "\033[1m",
        "dim":     "\033[2m",
    }

    def __init__(
        self,
        client: OpenAI,
        name: str = "Agent",
        system_prompt: str = "You are a helpful assistant.",
        model: str = os.getenv("OPENAI_MODEL"),
        max_iterations: int = 15,
        color: str = "cyan",
    ):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.max_iterations = max_iterations
        self.color = color
        self.tool_registry = ToolRegistry()

        # Register the built-in task_complete tool
        self.tool_registry.register(
            name="task_complete",
            description=(
                "Call this tool when you have fully completed the assigned task. "
                "Provide the final result as a detailed string."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": "The complete final result/deliverable for the task.",
                    }
                },
                "required": ["result"],
            },
            func=self._handle_task_complete,
        )

    # ──────────────────────────────────────────
    # Logging helpers
    # ──────────────────────────────────────────

    def log(self, message: str, style: str = ""):
        """Print a coloured, agent-prefixed log message."""
        c = self.COLORS.get(self.color, "")
        r = self.COLORS["reset"]
        s = self.COLORS.get(style, "")
        print(f"{c}[{self.name}]{r} {s}{message}{r}")

    # ──────────────────────────────────────────
    # Hooks (override in subclasses)
    # ──────────────────────────────────────────

    def pre_run(self, task: str) -> str:
        """Called before the agentic loop. Can modify the task."""
        return task

    def post_run(self, result: str) -> str:
        """Called after the agentic loop. Can modify the result."""
        return result

    # ──────────────────────────────────────────
    # The Agentic Loop
    # ──────────────────────────────────────────

    def run(self, task: str) -> str:
        """
        Execute a task using the agentic loop.

        Args:
            task: The task description.

        Returns:
            The agent's final result string.
        """
        # Pre-run hook
        task = self.pre_run(task)

        self.log(f"📋 Task received", "bold")
        self.log(f"   {task[:120]}{'...' if len(task) > 120 else ''}", "dim")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]

        tool_schemas = self.tool_registry.get_schemas()

        for iteration in range(1, self.max_iterations + 1):
            self.log(f"🔄 Iteration {iteration}/{self.max_iterations}", "dim")

            # ── THINK ──
            kwargs = {
                "model": self.model,
                "messages": messages,
            }
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            assistant_message = response.choices[0].message

            # ── DECIDE ──
            if not assistant_message.tool_calls:
                # Implicit completion via text
                result = assistant_message.content or "(empty response)"
                self.log("💬 Completed (text response)")
                return self.post_run(result)

            # ── ACT ──
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                self.log(f"🔧 {func_name}({self._summarize_args(func_args)})")

                # Execute via the tool registry
                try:
                    result = self.tool_registry.execute(func_name, func_args)
                except Exception as e:
                    result = {"error": str(e)}
                    self.log(f"❌ Error: {e}", "red")

                # ── CHECK: explicit completion? ──
                if isinstance(result, dict) and result.get("__done__"):
                    final = result["result"]
                    self.log("✅ Task complete!", "bold")
                    return self.post_run(final)

                # ── OBSERVE ──
                result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })

        # Safety: max iterations reached
        self.log(f"⚠️  Max iterations ({self.max_iterations}) reached!", "yellow")
        return self.post_run(f"[Agent stopped after {self.max_iterations} iterations]")

    # ──────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────

    def _handle_task_complete(self, result: str) -> dict:
        """Handler for the built-in task_complete tool."""
        return {"__done__": True, "result": result}

    def _summarize_args(self, args: dict) -> str:
        """Create a short summary of function args for logging."""
        parts = []
        for k, v in args.items():
            val_str = str(v)
            if len(val_str) > 60:
                val_str = val_str[:57] + "..."
            parts.append(f"{k}={val_str!r}")
        return ", ".join(parts)
