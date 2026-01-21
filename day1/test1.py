from openai import OpenAI
import os 
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# implement user based query or get the query from user
print("Enter input query")
user_input = input()
response = client.chat.completions.create(
    model= os.getenv("OPENAI_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ]
)

print(response.choices[0].message.content)