from app.services.gemini_client import ask_gemini
from app.services.deepseek_client import ask_deepseek

class AIError(Exception):
    pass


def generate_ai_response(prompt: str):
    try:
        print("Trying Gemini...")
        return ask_gemini(prompt)

    except Exception as e:
        print("Gemini failed → switching to DeepSeek:", e)

        try:
            print("Trying DeepSeek...")
            return ask_deepseek(prompt)

        except Exception as e2:
            print("Both failed:", e2)
            raise AIError("All AI providers are unavailable.")