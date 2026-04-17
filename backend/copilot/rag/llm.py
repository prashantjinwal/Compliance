from langchain_google_genai import  ChatGoogleGenerativeAI
from decouple import config

def get_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite" ,temperature=0.2,api_key=config("GEMINI_API_KEY"))
    return llm

