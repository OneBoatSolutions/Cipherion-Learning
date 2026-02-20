from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
def start_chat(username):
        
    # -----------------------------
    # OpenAI client
    # -----------------------------
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),  
    )

    # -----------------------------
    # Conversation storage setup
    # -----------------------------


    CHAT_DIR = "chats"
     

    os.makedirs(CHAT_DIR, exist_ok=True)

    safe_username = username.replace("@", "_").replace(".", "_")
    USER_CHAT_DIR = os.path.join(CHAT_DIR, safe_username)

    os.makedirs(USER_CHAT_DIR, exist_ok=True)


    # Determine next file number (1.json, 2.json, ...)
    existing_files = [
        f for f in os.listdir(USER_CHAT_DIR)
        if f.endswith(".json") and f.split(".")[0].isdigit()
    ]

    next_index = max([int(f.split(".")[0]) for f in existing_files], default=0) + 1
    chat_file_path = os.path.join(USER_CHAT_DIR, f"{next_index}.json")
    print("Saving chats in:", USER_CHAT_DIR)
    # -----------------------------
    # Conversation state
    # -----------------------------
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    print(f"Chat session saved to: {chat_file_path}")
    print("Type 'exit' to quit.\n")

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

        # Persist conversation after each turn
        with open(chat_file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

    print("Conversation saved.")
