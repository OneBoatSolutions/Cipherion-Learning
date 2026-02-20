"""
Chapter 2: Building a Simple Chatbot
=====================================
A multi-turn conversational chatbot that remembers context.

Key concepts:
    - Maintaining a messages list (conversation history)
    - Appending both user and assistant messages each turn
    - Streaming responses token-by-token for a real-time feel

Usage:
    python main.py
    Type your messages, press Enter. Type 'exit' or 'quit' to stop.
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────────────────────
# System prompt — defines the chatbot's personality
# ──────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a friendly and knowledgeable coding assistant. "
    "You help developers learn about AI agents. "
    "Keep answers concise but thorough."
)

def run_chatbot():
    """Main chatbot loop with streaming."""

    # The conversation history — this is the KEY concept.
    # Every message (user + assistant) is appended here so the model
    # always has the full context of the conversation.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print("=" * 60)
    print("  AI Chatbot  (type 'exit' to quit)")
    print("=" * 60)

    while True:
        # ── Read user input ──────────────────────
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

        # ── Append the user message to history ───
        messages.append({"role": "user", "content": user_input})

        # ── Call the API with streaming ──────────
        print("\nAssistant: ", end="", flush=True)

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            stream=True,                       # Enable streaming!
        )

        # Collect the full response while printing tokens as they arrive
        assistant_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                token = delta.content
                print(token, end="", flush=True)
                assistant_response += token

        print()  # Newline after streaming finishes

        # ── Append the assistant response to history ──
        messages.append({"role": "assistant", "content": assistant_response})


if __name__ == "__main__":
    run_chatbot()
