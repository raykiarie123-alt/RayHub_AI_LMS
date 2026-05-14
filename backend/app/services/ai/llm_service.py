import os
import json
import asyncio
from google import genai
from app.core.config import settings

_client = None


def get_llm_client():
    global _client

    if _client is None:
        api_key = os.environ.get(
            "GEMINI_API_KEY",
            getattr(settings, "GEMINI_API_KEY", "")
        )

        _client = genai.Client(api_key=api_key)

    return _client


async def call_llm(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    client = get_llm_client()
    model = model or getattr(settings, "LLM_MODEL", "gemini-2.0-flash-lite")

    prompt = f"""
{system_prompt}

User question:
{user_message}
"""

    def run_sync():
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text

    try:
        return await asyncio.to_thread(run_sync)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            return (
                "AI Tutor is temporarily unavailable because the daily Gemini API quota has been reached. "
                "Please try again later or switch to a lighter model."
            )
        raise


async def call_llm_json(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.3
) -> str:
    client = get_llm_client()
    model = model or getattr(settings, "LLM_MODEL", "gemini-2.0-flash-lite")

    prompt = f"""
{system_prompt}

Return only valid JSON.

User request:
{user_message}
"""

    def run_sync():
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        json.loads(text)
        return text

    try:
        return await asyncio.to_thread(run_sync)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            return '{"error": "AI quota reached. Please try again later."}'
        raise