"""
Chapter 6: The Agentic Loop — agent.py
========================================
The AGENTIC LOOP is what separates a tool-using chatbot from a true agent.

Key improvements over Chapter 5's Agent:
    1. MAX ITERATIONS — prevents infinite loops
    2. "DONE" TOOL — the agent explicitly signals when it's finished
    3. THOUGHT TRACKING — records the agent's reasoning chain
    4. ERROR RECOVERY — catches and reports tool execution errors
    5. ITERATION LOGGING — shows progress through the loop

The loop:
    ┌──────────────────────────────────────────┐
    │  while iterations < max_iterations:      │
    │      1. THINK  → call the model          │
    │      2. DECIDE → tool calls or text?     │
    │      3. ACT    → execute tools           │
    │      4. OBSERVE → feed results back      │
    │      5. CHECK  → did agent call "done"?  │
    │          YES → return result             │
    │          NO  → loop again               │
    └──────────────────────────────────────────┘
"""

import json
from openai import OpenAI


class AgenticAgent:
    """
    An agent with a proper agentic loop.

    The agent keeps running autonomously until:
        1. It calls the 'task_complete' tool (explicit completion)
        2. It reaches the max iteration limit (safety valve)
        3. It responds with text and no tool calls (implicit completion)
    """

    def __init__(
        self,
        client: OpenAI,
        name: str,
        system_prompt: str,
        tools: list[dict] | None = None,
        functions: dict | None = None,
        model: str = "gpt-4o-mini",
        max_iterations: int = 10,
    ):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.max_iterations = max_iterations

        # Start with user-provided tools/functions
        self.functions = dict(functions or {})
        self.tools = list(tools or [])

        # ── Inject the built-in "task_complete" tool ──
        # This lets the agent explicitly signal "I'm done" and provide the final result.
        self.tools.append({
            "type": "function",
            "function": {
                "name": "task_complete",
                "description": (
                    "Call this when you have completed the task. "
                    "Provide the final result as a string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "string",
                            "description": "The final result/answer for the task.",
                        }
                    },
                    "required": ["result"],
                },
            },
        })
        # The actual handler: returns a special sentinel
        self.functions["task_complete"] = lambda result: {"__done__": True, "result": result}

    def run(self, task: str) -> str:
        """
        Execute a task using the agentic loop.

        Args:
            task: The task description.

        Returns:
            The agent's final result.
        """
        print(f"\n{'='*60}")
        print(f"  [{self.name}] Starting task")
        print(f"  Task: {task}")
        print(f"{'='*60}")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]

        iteration = 0

        # ══════════════════════════════════════
        # THE AGENTIC LOOP
        # ══════════════════════════════════════
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration}/{self.max_iterations} ---")

            # ── THINK: Call the model ──
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
            )

            assistant_message = response.choices[0].message

            # ── DECIDE: Does the model want to call tools? ──
            if not assistant_message.tool_calls:
                # No tool calls — implicit completion
                print(f"  [{self.name}] No tool calls — completing with text response.")
                return assistant_message.content or "(No response)"

            # ── ACT: Execute each tool call ──
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"  [{self.name}] 🔧 {func_name}({json.dumps(func_args, indent=2)})")

                # Execute with error handling
                try:
                    func = self.functions.get(func_name)
                    if not func:
                        raise ValueError(f"Unknown tool: {func_name}")

                    result = func(**func_args)
                except Exception as e:
                    result = {"error": str(e)}
                    print(f"  [{self.name}] ❌ Error: {e}")

                # ── CHECK: Did the agent signal completion? ──
                if isinstance(result, dict) and result.get("__done__"):
                    final_result = result["result"]
                    print(f"\n  [{self.name}] ✅ Task complete!")
                    return final_result

                # ── OBSERVE: Feed the result back ──
                result_str = json.dumps(result) if isinstance(result, dict) else str(result)
                print(f"  [{self.name}] 📋 Result: {result_str[:200]}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })

            # Loop continues → next iteration

        # ── Safety valve: max iterations reached ──
        print(f"\n  [{self.name}] ⚠️  Max iterations ({self.max_iterations}) reached!")
        return f"[Agent stopped: reached {self.max_iterations} iteration limit]"
