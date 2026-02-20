"""
Chapter 5: Building a Simple AI Agent — agent.py
==================================================
The Agent class — the foundation of everything that follows.

An Agent is NOT just a chatbot. The key difference:
    - Chatbot: responds to user messages
    - Agent:   receives a TASK, decides what to do, takes ACTIONS, and delivers a RESULT

This Agent class encapsulates:
    1. A name and system prompt (personality/role)
    2. A set of tools it can use
    3. A run() method that executes a single task
"""

import json
from openai import OpenAI


class Agent:
    """
    A simple AI agent that can use tools to accomplish a task.

    This is a single-pass agent: it processes ONE request, makes tool calls
    if needed, and returns the final result.
    """

    def __init__(
        self,
        client: OpenAI,
        name: str,
        system_prompt: str,
        tools: list[dict] | None = None,
        functions: dict | None = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Args:
            client:        OpenAI client instance
            name:          Human-readable name for this agent
            system_prompt: The system message that defines the agent's role
            tools:         List of tool schemas (JSON dicts) for the API
            functions:     Dict mapping function name → callable
            model:         Which model to use
        """
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.functions = functions or {}
        self.model = model

    def run(self, task: str) -> str:
        """
        Execute a task and return the result.

        Args:
            task: The task description / user request.

        Returns:
            The agent's final text response.
        """
        print(f"\n[{self.name}] Received task: {task}")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]

        # Keep calling the model until it responds with text (no more tool calls)
        while True:
            kwargs = {
                "model": self.model,
                "messages": messages,
            }
            if self.tools:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            assistant_message = response.choices[0].message

            # ── Does the model want to call tools? ──
            if assistant_message.tool_calls:
                messages.append(assistant_message)

                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    print(f"  [{self.name}] 🔧 {func_name}({func_args})")

                    # Execute the tool
                    func = self.functions.get(func_name)
                    if func:
                        result = func(**func_args)
                    else:
                        result = {"error": f"Unknown tool: {func_name}"}

                    print(f"  [{self.name}] ✅ Result: {result}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result) if isinstance(result, dict) else str(result),
                    })

                # Continue the loop — model may want to call more tools
                continue

            else:
                # ── No tool calls — we have the final answer ──
                final_answer = assistant_message.content
                print(f"  [{self.name}] 💬 Done.")
                return final_answer
