from app.services.ai.llm_service import call_llm
from app.services.youtube.transcript_service import get_youtube_transcript


async def summarize_youtube_video(url: str, title: str = None) -> str:
    """
    Fetch transcript and generate an AI summary.
    Returns the summary text.
    """
    transcript = get_youtube_transcript(url)

    # Truncate transcript if too long
    max_chars = 12000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "..."

    system_prompt = """You are an expert CPA tutor summarizing educational content for CPA students.
Create a clear, structured summary of the video content that highlights:
1. Key concepts and definitions
2. Important rules and principles
3. Examples and applications
4. Exam-relevant points

Format the summary with clear headings and bullet points."""

    user_message = f"""Please summarize this YouTube video transcript for CPA students:

Title: {title or 'CPA Study Video'}

Transcript:
{transcript}"""

    summary = await call_llm(system_prompt=system_prompt, user_message=user_message)
    return summary
