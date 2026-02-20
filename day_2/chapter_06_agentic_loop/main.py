"""
Chapter 6: The Agentic Loop — main.py
=======================================
Demonstrates the AgenticAgent with a multi-step research task.

The agent will:
    1. Research multiple data points using tools
    2. Perform calculations
    3. Call 'task_complete' when it has the final answer
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from agent import AgenticAgent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────

def get_stock_price(symbol: str) -> dict:
    """Simulated stock price lookup."""
    prices = {
        "AAPL": 182.52, "GOOGL": 141.80, "MSFT": 378.91,
        "AMZN": 178.25, "TSLA": 248.42, "META": 390.10,
    }
    price = prices.get(symbol.upper())
    if price:
        return {"symbol": symbol.upper(), "price": price, "currency": "USD"}
    return {"symbol": symbol, "error": "Symbol not found"}


def get_company_info(name: str) -> dict:
    """Simulated company info lookup."""
    info = {
        "apple":    {"name": "Apple Inc.",      "ticker": "AAPL",  "sector": "Technology", "employees": "164,000"},
        "google":   {"name": "Alphabet Inc.",   "ticker": "GOOGL", "sector": "Technology", "employees": "182,000"},
        "microsoft":{"name": "Microsoft Corp.", "ticker": "MSFT",  "sector": "Technology", "employees": "221,000"},
    }
    return info.get(name.lower(), {"name": name, "error": "Company not found"})


def calculate(expression: str) -> dict:
    """Evaluate a math expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"expression": expression, "result": str(result)}
    except Exception as e:
        return {"expression": expression, "error": str(e)}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker symbol, e.g. 'AAPL'"}
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": "Get information about a company (ticker, sector, employee count).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Company name, e.g. 'Apple'"}
                },
                "required": ["name"],
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
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"],
            },
        },
    },
]

FUNCTIONS = {
    "get_stock_price": get_stock_price,
    "get_company_info": get_company_info,
    "calculate": calculate,
}

# ──────────────────────────────────────────────
# Create the agent and run a complex task
# ──────────────────────────────────────────────

analyst = AgenticAgent(
    client=client,
    name="Market Analyst",
    system_prompt=(
        "You are a market research analyst. "
        "Use your tools to gather data, perform calculations, and produce insights. "
        "When you have a complete analysis, call the task_complete tool with your findings."
    ),
    tools=TOOLS,
    functions=FUNCTIONS,
    max_iterations=10,
)

# This task requires multiple tool calls across multiple iterations
result = analyst.run(
    "Compare Apple and Microsoft: look up both companies' info and stock prices, "
    "then calculate which stock is cheaper per 1,000 employees. "
    "Present a brief analysis."
)

print("\n" + "=" * 60)
print("FINAL ANALYSIS:")
print("=" * 60)
print(result)
