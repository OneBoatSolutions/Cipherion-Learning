from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# OpenAI client
# -----------------------------
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),  
)

# -----------------------------
# Chat storage
# -----------------------------
CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    print("No chat sessions found.")
    exit(1)

chat_files = sorted(
    f for f in os.listdir(CHAT_DIR)
    if f.endswith(".json") and f.split(".")[0].isdigit()
)

if not chat_files:
    print("No chat sessions found.")
    exit(1)

# -----------------------------
# List sessions
# -----------------------------
print("Available chat sessions:\n")
for f in chat_files:
    print(f"  {f}")

# -----------------------------
# User selects session
# -----------------------------
while True:
    choice = input("\nEnter session number to continue (e.g. 1): ").strip()

    if choice.isdigit() and f"{choice}.json" in chat_files:
        chat_file_path = os.path.join(CHAT_DIR, f"{choice}.json")
        break

    print("Invalid selection. Try again.")

# -----------------------------
# Load conversation
# -----------------------------
with open(chat_file_path, "r", encoding="utf-8") as f:
    messages = json.load(f)

print(f"\nLoaded session {choice}. Type 'exit' to quit.\n")

# -----------------------------
# Chat loop
# -----------------------------
while True:
    user_input = input("You: ")

    if user_input.lower() in {"exit", "quit"}:
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=messages,
    )

    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})

    print(f"Assistant: {assistant_message}\n")

    # Persist updates
    with open(chat_file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

print("Session saved.")
