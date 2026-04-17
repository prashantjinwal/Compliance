from langchain_google_genai import GoogleGenerativeAIEmbeddings
from decouple import config


def get_embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            api_key=config("GEMINI_API_KEY"),
        )
    return embeddings
