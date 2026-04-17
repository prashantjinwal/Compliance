import os
from dotenv import load_dotenv
load_dotenv()

from ingestion.parser import parse_document
from ingestion.chunker import chunk_document
from vectorstore.qdrant import setup_collection, upsert_chunks

SAMPLE_DOCS = [
    "demo/sample_docs/sec_10k_sample.pdf",
    "demo/sample_docs/gdpr_policy_sample.pdf"
]

if __name__ == "__main__":
    setup_collection()
    for path in SAMPLE_DOCS:
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue
        print(f"Seeding: {path}")
        parsed = parse_document(path)
        parsed["source"] = os.path.basename(path)
        chunks = chunk_document(parsed)
        upsert_chunks(chunks)
        print(f"  Done — {len(chunks)} chunks indexed")
    print("Seed complete.")