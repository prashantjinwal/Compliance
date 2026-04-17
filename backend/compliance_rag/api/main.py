from fastapi import FastAPI
from api.routes import router
from vectorstore.qdrant import setup_collection
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Compliance RAG MVP")

@app.on_event("startup")
async def startup():
    setup_collection()

app.include_router(router)