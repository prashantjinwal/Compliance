from langchain_google_genai import GoogleGenerativeAIEmbeddings

from .config import get_gemini_api_key

def get_embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            api_key=get_gemini_api_key(),
        )
    return embeddings
