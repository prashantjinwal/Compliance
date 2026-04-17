

import re
from vectorstore.qdrant import search

import re
from vectorstore.qdrant import search

RISK_SIGNALS = [
    "material", "disclosure", "shall", "must", "required",
    "personal data", "consent", "restatement", "internal control",
    "going concern", "forward-looking", "safe harbor"
]

def retrieve_regulations(chunk_text: str, top_k: int = 5) -> list:
    # Detect which risk signals appear in this chunk
    signals = [s for s in RISK_SIGNALS if s.lower() in chunk_text.lower()]
    
    # Enrich query with detected signals for better retrieval targeting
    enriched_query = chunk_text[:500]
    if signals:
        enriched_query += " " + " ".join(signals)
    
    results = search(query=enriched_query, top_k=top_k)
    return results



