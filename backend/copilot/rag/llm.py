from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from .config import get_gemini_api_key
from .errors import (
    CopilotRateLimitError,
    extract_retry_seconds_from_exception,
    is_quota_error,
)

def get_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
        api_key=get_gemini_api_key(),
        max_retries=1,
    )
    return llm


def invoke_llm(prompt):
    try:
        response = get_llm().invoke(prompt)
    except ChatGoogleGenerativeAIError as exc:
        if is_quota_error(exc):
            raise CopilotRateLimitError(
                "Gemini API quota exceeded. Please try again later or upgrade the API plan.",
                retry_seconds=extract_retry_seconds_from_exception(exc),
            ) from exc
        raise
    except Exception as exc:
        if is_quota_error(exc):
            raise CopilotRateLimitError(
                "Gemini API quota exceeded. Please try again later or upgrade the API plan.",
                retry_seconds=extract_retry_seconds_from_exception(exc),
            ) from exc
        raise

    if hasattr(response, "content"):
        return response.content

    return str(response)
