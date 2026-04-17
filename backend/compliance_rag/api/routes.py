from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
import tempfile, os

from ingestion.parser import parse_document
from ingestion.chunker import chunk_document
from vectorstore.qdrant import upsert_chunks
from rag.assessor import assess_document
from highlight.report import generate_report, build_json_summary

router = APIRouter()

# In-memory store for demo — swap for Redis or DB in v2
_assessment_cache: dict = {}

@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """
    Upload a PDF or text file. Parses, chunks, embeds,
    and stores in Qdrant. Returns chunk count.
    """
    suffix = os.path.splitext(file.filename)[1]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        parsed = parse_document(tmp_path)
        parsed["source"] = file.filename  # use original filename as source ID
        chunks = chunk_document(parsed)
        upsert_chunks(chunks)
    finally:
        os.unlink(tmp_path)
    
    return {"status": "ingested", "file": file.filename, "chunks": len(chunks)}

@router.post("/assess")
async def assess(document_name: str, top_chunks: int = 20):
    """
    Run full RAG risk assessment on an already-ingested document.
    Searches Qdrant for chunks from this document and assesses each.
    """
    from vectorstore.qdrant import get_client, COLLECTION
    
    client = get_client()
    results = client.scroll(
        collection_name=COLLECTION,
        scroll_filter={
            "must": [{"key": "source", "match": {"value": document_name}}]
        },
        limit=top_chunks,
        with_payload=True
    )[0]
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found for '{document_name}'. Ingest it first."
        )
    
    chunks = [
        {
            "text":          r.payload["text"],
            "section_title": r.payload["section_title"],
            "source":        r.payload["source"],
            "chunk_index":   r.payload["chunk_index"]
        }
        for r in results
    ]
    
    print(f"Assessing {len(chunks)} chunks from '{document_name}'...")
    verdicts = assess_document(chunks)
    
    # Cache for report endpoint
    _assessment_cache[document_name] = verdicts
    summary = build_json_summary(verdicts, document_name)
    
    return summary

@router.get("/report/{document_name}", response_class=PlainTextResponse)
async def report(document_name: str):
    """
    Returns the plain-text annotated compliance report
    for the most recent assessment of this document.
    """
    if document_name not in _assessment_cache:
        raise HTTPException(
            status_code=404,
            detail=f"No assessment found for '{document_name}'. Run /assess first."
        )
    
    verdicts = _assessment_cache[document_name]
    return generate_report(verdicts, document_name)