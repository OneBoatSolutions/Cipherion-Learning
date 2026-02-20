"""
Chapter 1: Hello, Chat Completion
==================================
Your very first interaction with the OpenAI API.

This script sends a single message to the model and prints the response.
It's the simplest possible program — the "Hello World" of AI development.

Prerequisites:
    pip install openai python-dotenv
    Create a .env file with: OPENAI_API_KEY=sk-your-key-here
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# ──────────────────────────────────────────────
# 1. Load your API key from the .env file
# ──────────────────────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────────────────────
# 2. Make a single chat completion request
# ──────────────────────────────────────────────
response = client.chat.completions.create(
    model="gpt-4o-mini",                       # The model to use
    messages=[
        {
            "role": "system",                  # System message: sets the AI's behaviour
            "content": "You are a helpful assistant that explains things simply.",
        },
        {
            "role": "user",                    # User message: what you're asking
            "content": "What is an AI agent in 3 sentences?",
        },
    ],
    temperature=0.7,                           # Creativity (0 = deterministic, 2 = wild)
    max_tokens=256,                            # Max length of the response
)

# ──────────────────────────────────────────────
# 3. Print the result
# ──────────────────────────────────────────────
message = response.choices[0].message
print(f"Role   : {message.role}")
print(f"Content: {message.content}")

# ──────────────────────────────────────────────
# 4. Inspect usage (tokens consumed)
# ──────────────────────────────────────────────
usage = response.usage
print(f"\n--- Token Usage ---")
print(f"Prompt tokens     : {usage.prompt_tokens}")
print(f"Completion tokens : {usage.completion_tokens}")
print(f"Total tokens      : {usage.total_tokens}")
