from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"), 
)


messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("Type 'exit' to quit.\n")

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
