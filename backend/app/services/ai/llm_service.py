import os
from openai import AsyncOpenAI
from app.core.config import settings

# Use the pre-configured OpenAI client (API key and base URL from environment)
_client: AsyncOpenAI = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        )
    return _client


async def call_llm(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """
    Call the LLM with a system prompt and user message.
    Returns the assistant's response text.
    """
    client = get_llm_client()
    model = model or settings.LLM_MODEL

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


async def call_llm_json(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.3
) -> str:
    """
    Call the LLM expecting JSON output.
    Returns the raw JSON string from the assistant.
    """
    client = get_llm_client()
    model = model or settings.LLM_MODEL

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=temperature,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content