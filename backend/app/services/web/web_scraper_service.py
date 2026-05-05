import httpx
from bs4 import BeautifulSoup
from typing import Tuple
from app.services.ai.llm_service import call_llm


async def scrape_webpage(url: str) -> Tuple[str, str]:
    """
    Scrape a webpage and extract its main text content.
    Returns (title, content) tuple.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RayHubBot/1.0)"
    }
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title = ""
    if soup.title:
        title = soup.title.string or ""

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Extract main content
    main_content = soup.find("main") or soup.find("article") or soup.find("body")
    if main_content:
        text = main_content.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)

    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    content = "\n".join(lines)

    return title.strip(), content


async def summarize_webpage(url: str, title: str = None) -> str:
    """Scrape and summarize a webpage for CPA students."""
    page_title, content = await scrape_webpage(url)
    display_title = title or page_title or url

    # Truncate if too long
    if len(content) > 12000:
        content = content[:12000] + "..."

    system_prompt = """You are an expert CPA tutor summarizing web content for CPA students.
Create a clear, structured summary highlighting key accounting, audit, tax, or finance concepts."""

    user_message = f"""Summarize this web page content for CPA students:

Title: {display_title}
URL: {url}

Content:
{content}"""

    return await call_llm(system_prompt=system_prompt, user_message=user_message)