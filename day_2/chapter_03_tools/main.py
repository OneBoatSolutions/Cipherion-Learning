"""
Chapter 3: Chat Completion with Tool Execution
================================================
Teaching the model to call YOUR Python functions.

This is the breakthrough concept — the model doesn't just generate text,
it can decide to call tools (functions) you define and use the results.

Flow:
    1. You define tools as JSON schemas
    2. You send them with the API call
    3. The model responds with tool_calls (instead of text)
    4. You execute the function locally
    5. You send the result back as a "tool" role message
    6. The model uses the result to form its final answer

Usage:
    python main.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════
# STEP 1: Define your Python functions (the actual tools)
# ══════════════════════════════════════════════

def get_weather(city: str) -> dict:
    """Simulate a weather lookup. In production, call a real API."""
    fake_weather = {
        "new york": {"temp": "22°C", "condition": "Sunny"},
        "london":   {"temp": "15°C", "condition": "Cloudy"},
        "tokyo":    {"temp": "28°C", "condition": "Humid"},
    }
    data = fake_weather.get(city.lower(), {"temp": "20°C", "condition": "Unknown"})
    return {"city": city, **data}


def calculate(expression: str) -> dict:
    """Evaluate a math expression safely."""
    try:
        # WARNING: In production, use a proper sandbox. This is for learning only.
        result = eval(expression, {"__builtins__": {}})
        return {"expression": expression, "result": str(result)}
    except Exception as e:
        return {"expression": expression, "error": str(e)}


# ══════════════════════════════════════════════
# STEP 2: Map function names → actual functions
# ══════════════════════════════════════════════

AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate": calculate,
}


# ══════════════════════════════════════════════
# STEP 3: Define the tool schemas (JSON descriptions)
#   This tells the model WHAT tools exist, their parameters,
#   and their descriptions. The model uses this to decide
#   when and how to call them.
# ══════════════════════════════════════════════

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. 'New York'",
                    }
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
                    "expression": {
                        "type": "string",
                        "description": "A math expression to evaluate, e.g. '2 + 2 * 3'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


# ══════════════════════════════════════════════
# STEP 4: The main flow — call API, detect tool calls, execute, return results
# ══════════════════════════════════════════════

def run():
    user_question = "What's the weather in Tokyo, and what is 145 * 37?"

    print(f"User: {user_question}\n")

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the provided tools when needed."},
        {"role": "user", "content": user_question},
    ]

    # ── First API call: the model decides what tools to call ──
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",         # Let the model decide
    )

    assistant_message = response.choices[0].message
    print(f"[Model Decision] finish_reason = {response.choices[0].finish_reason}")

    # ── Check if the model wants to call tools ──
    if assistant_message.tool_calls:
        print(f"[Model wants to call {len(assistant_message.tool_calls)} tool(s)]\n")

        # IMPORTANT: append the assistant's message (with tool_calls) to history
        messages.append(assistant_message)

        # ── Execute each tool call ──
        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  Calling: {func_name}({func_args})")

            # Look up and execute the function
            func = AVAILABLE_FUNCTIONS[func_name]
            result = func(**func_args)

            print(f"  Result : {result}\n")

            # IMPORTANT: send the result back as a "tool" role message
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,        # Must match the tool_call's id
                "content": json.dumps(result),
            })

        # ── Second API call: the model uses tool results to form its answer ──
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
        )

        final_answer = final_response.choices[0].message.content
        print(f"Assistant: {final_answer}")

    else:
        # Model didn't need tools — it answered directly
        print(f"Assistant: {assistant_message.content}")


if __name__ == "__main__":
    run()
