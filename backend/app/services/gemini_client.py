import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt: str):
    model = genai.GenerativeModel("LLM_MODEL")
    response = model.generate_content(prompt)   
    return response.text
