"""
Chapter 5: Building a Simple AI Agent — main.py
=================================================
Demonstrates the Agent class from agent.py.

We create a research agent that can look up information and do calculations,
give it a task, and let it work autonomously.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from agent import Agent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────────────────────
# Define tools for the agent
# ──────────────────────────────────────────────

def look_up_population(country: str) -> dict:
    """Simulated database of country populations."""
    data = {
        "india":   {"country": "India",   "population": "1.44 billion"},
        "china":   {"country": "China",   "population": "1.43 billion"},
        "usa":     {"country": "USA",     "population": "334 million"},
        "japan":   {"country": "Japan",   "population": "125 million"},
        "germany": {"country": "Germany", "population": "84 million"},
    }
    return data.get(country.lower(), {"country": country, "population": "Unknown"})


def calculate(expression: str) -> dict:
    """Evaluate a math expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"expression": expression, "result": str(result)}
    except Exception as e:
        return {"expression": expression, "error": str(e)}


# Tool schemas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "look_up_population",
            "description": "Look up the population of a country.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string", "description": "Country name"}
                },
                "required": ["country"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression to evaluate"}
                },
                "required": ["expression"],
            },
        },
    },
]

# Function map
FUNCTIONS = {
    "look_up_population": look_up_population,
    "calculate": calculate,
}

# ──────────────────────────────────────────────
# Create the agent and give it a task
# ──────────────────────────────────────────────

research_agent = Agent(
    client=client,
    name="Research Agent",
    system_prompt=(
        "You are a research agent. When given a question, "
        "use your tools to look up data and perform calculations. "
        "Always show your work and provide a clear final answer."
    ),
    tools=TOOLS,
    functions=FUNCTIONS,
)

# Give the agent a task — it runs autonomously
result = research_agent.run(
    "What is the combined population of India and Japan? "
    "Show the individual numbers and the total."
)

print("\n" + "=" * 60)
print("FINAL RESULT:")
print("=" * 60)
print(result)
