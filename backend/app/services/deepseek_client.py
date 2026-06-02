from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def ask_deepseek(prompt: str):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are RayHub AI Tutor."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content