# Qdrant operations in one file: create collection, upsert chunks, and hybrid search.

import atexit
import os
import uuid

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue
)

load_dotenv()

_client = None

COLLECTION = os.getenv("COLLECTION_NAME", "regulations")
QDRANT_MODE = os.getenv("QDRANT_MODE", "server").strip().lower()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333").strip()
QDRANT_LOCAL_PATH = os.getenv("QDRANT_LOCAL_PATH", "./qdrant_local_db").strip()

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        if QDRANT_MODE == "local":
            _client = QdrantClient(path=QDRANT_LOCAL_PATH)
        elif QDRANT_MODE == "memory":
            _client = QdrantClient(":memory:")
        else:
            _client = QdrantClient(url=QDRANT_URL)
    return _client

def close_client():
    global _client
    if _client is not None:
        _client.close()
        _client = None

atexit.register(close_client)

def setup_collection():
    client = get_client()
    try:
        existing = [c.name for c in client.get_collections().collections]
    except ResponseHandlingException as exc:
        raise RuntimeError(
            "Could not connect to Qdrant. "
            f"QDRANT_MODE={QDRANT_MODE!r}, QDRANT_URL={QDRANT_URL!r}. "
            "If you want embedded local storage, set QDRANT_MODE=local in .env. "
            "If you want server mode, start Qdrant on localhost:6333."
        ) from exc

    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION}")
    else:
        print(f"Collection already exists: {COLLECTION}")

def upsert_chunks(chunks: list):
    from vectorstore.embedder import encode_batch

    client  = get_client()
    texts   = [c["text"] for c in chunks]
    vectors = encode_batch(texts)
    
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "text":          chunk["text"],
                "section_title": chunk["section_title"],
                "source":        chunk["source"],
                "chunk_index":   chunk["chunk_index"]
            }
        )
        for chunk, vec in zip(chunks, vectors)
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"Upserted {len(points)} chunks into '{COLLECTION}'")

def search(query: str, top_k: int = 5, source_filter: str = None) -> list:
    from vectorstore.embedder import encode

    client     = get_client()
    query_vec  = encode(query)
    
    filt = None
    if source_filter:
        filt = Filter(must=[
            FieldCondition(key="source", match=MatchValue(value=source_filter))
        ])
    
    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vec,
        limit=top_k,
        query_filter=filt,
        with_payload=True
    )
    
    return [
        {
            "text":          r.payload["text"],
            "section_title": r.payload["section_title"],
            "source":        r.payload["source"],
            "score":         round(r.score, 3)
        }
        for r in results
    ]

