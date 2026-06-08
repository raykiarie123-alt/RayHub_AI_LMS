from google import genai
import os

_client = None


def get_gemini_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        _client = genai.Client(api_key=api_key)
    return _client


def ask_gemini(prompt: str, model: str = "gemini-2.0-flash-lite") -> str:
    client = get_gemini_client()
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
