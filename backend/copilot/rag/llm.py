from langchain_google_genai import ChatGoogleGenerativeAI

from .config import get_gemini_api_key

def get_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
        api_key=get_gemini_api_key(),
    )
    return llm
