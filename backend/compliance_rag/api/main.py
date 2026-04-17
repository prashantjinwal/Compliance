from fastapi import FastAPI
from api.routes import router
from vectorstore.qdrant import setup_collection
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Compliance RAG MVP")

@app.on_event("startup")
async def startup():
    setup_collection()
    if os.getenv("QDRANT_MODE", "memory") == "memory":
        _auto_seed()


def _auto_seed():
    import os
    from ingestion.parser import parse_document
    from ingestion.chunker import chunk_document
    from vectorstore.qdrant import upsert_chunks

    sample_dir = "demo/sample_docs"
    if not os.path.exists(sample_dir):
        return

    for filename in os.listdir(sample_dir):
        if not filename.endswith((".pdf", ".txt")):
            continue
        path = os.path.join(sample_dir, filename)
        try:
            print(f"Auto-seeding: {filename}")
            parsed = parse_document(path)
            parsed["source"] = filename
            chunks = chunk_document(parsed)
            upsert_chunks(chunks)
        except Exception as e:
            print(f"  Failed to seed {filename}: {e}")

app.include_router(router)
