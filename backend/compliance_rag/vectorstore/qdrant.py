#Qdrant operations in one file: create collection, upsert chunks, and hybrid search. 

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue
)
import os, uuid
from vectorstore.embedder import encode, encode_batch

_client = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
    return _client

COLLECTION = os.getenv("COLLECTION_NAME", "regulations")

def setup_collection():
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION}")
    else:
        print(f"Collection already exists: {COLLECTION}")

def upsert_chunks(chunks: list):
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

