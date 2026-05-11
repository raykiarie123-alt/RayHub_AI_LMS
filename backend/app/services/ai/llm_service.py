import os
import json
import asyncio
from google import genai
from app.core.config import settings

_client = None


def get_llm_client():
    global _client

    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", getattr(settings, "GEMINI_API_KEY", ""))

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
    model = model or getattr(settings, "LLM_MODEL", "gemini-2.5-flash")

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

    return await asyncio.to_thread(run_sync)


async def call_llm_json(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.3
) -> str:
    client = get_llm_client()
    model = model or getattr(settings, "LLM_MODEL", "gemini-2.5-flash")

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

    return await asyncio.to_thread(run_sync)