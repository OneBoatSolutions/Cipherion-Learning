"""
Chapter 4: Chatbot with Tool Use
=================================
Combines the multi-turn chatbot (Ch 2) with tool execution (Ch 3).

The model can have a conversation AND call tools whenever it needs to.
This handles the full tool-calling loop inside a multi-turn chat.

Key advancement over Chapter 3:
    - Multi-turn: the conversation continues after tool use
    - Handles multiple consecutive tool calls in a single turn
    - The tool loop runs automatically (user only sees the final answer)

Usage:
    python main.py
    Type naturally — the bot will call tools when needed.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────────────────────
# Tools — same as Chapter 3, but integrated into a chat loop
# ──────────────────────────────────────────────

def get_weather(city: str) -> dict:
    """Simulate a weather lookup."""
    fake_weather = {
        "new york": {"temp": "22°C", "condition": "Sunny"},
        "london":   {"temp": "15°C", "condition": "Cloudy"},
        "tokyo":    {"temp": "28°C", "condition": "Humid"},
        "paris":    {"temp": "18°C", "condition": "Rainy"},
        "mumbai":   {"temp": "34°C", "condition": "Hot and humid"},
    }
    data = fake_weather.get(city.lower(), {"temp": "20°C", "condition": "Unknown"})
    return {"city": city, **data}


def calculate(expression: str) -> dict:
    """Evaluate a math expression safely."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"expression": expression, "result": str(result)}
    except Exception as e:
        return {"expression": expression, "error": str(e)}


AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate": calculate,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name, e.g. 'New York'"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "A math expression, e.g. '2 + 2 * 3'"}
                },
                "required": ["expression"],
            },
        },
    },
]


# ──────────────────────────────────────────────
# The tool execution loop — this is the core pattern
# ──────────────────────────────────────────────

def process_tool_calls(messages):
    """
    Repeatedly calls the model until it stops requesting tools.
    Returns the final assistant content.

    This is the INNER LOOP that handles:
    1. Model requests tool calls → execute them → send results → repeat
    2. Model responds with text → return it (loop ends)
    """
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # If the model wants to call tools
        if assistant_message.tool_calls:
            # Append the assistant message (contains tool_calls metadata)
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"  🔧 Calling {func_name}({func_args})")

                # Execute the function
                func = AVAILABLE_FUNCTIONS.get(func_name)
                if func:
                    result = func(**func_args)
                else:
                    result = {"error": f"Unknown function: {func_name}"}

                # Append the tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

            # Loop again — model might want to call more tools
            continue

        else:
            # No more tool calls — model is done, return the text
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
            })
            return assistant_message.content


# ──────────────────────────────────────────────
# The chatbot loop (outer loop = conversation turns)
# ──────────────────────────────────────────────

def run_chatbot():
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to tools. "
                "Use the weather tool when asked about weather, "
                "and the calculator when math is involved. "
                "Always respond naturally after using tools."
            ),
        },
    ]

    print("=" * 60)
    print("  Chatbot with Tools  (type 'exit' to quit)")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        print()  # Blank line before tool calls / response
        response_text = process_tool_calls(messages)
        print(f"\nAssistant: {response_text}")


if __name__ == "__main__":
    run_chatbot()
