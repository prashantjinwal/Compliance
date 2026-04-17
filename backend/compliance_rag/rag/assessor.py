import json, re, os
from groq import Groq
from rag.retriever import retrieve_regulations
from rag.prompt import build_prompt


_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def assess_chunk(chunk: dict) -> dict:
    retrieved = retrieve_regulations(chunk["text"], top_k=5)

    if not retrieved:
        return {
            "section_title": chunk["section_title"],
            "source":        chunk["source"],
            "risk_level":    "unverified",
            "risk_score":    0.0,
            "findings":      [],
            "summary":       "No matching regulations found in knowledge base.",
            "retrieved":     []
        }

    system_prompt, user_prompt = build_prompt(chunk["text"], retrieved)

    try:
        response = get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.1,   # low temp for consistent JSON
            max_tokens=1000
        )
        raw     = response.choices[0].message.content
        verdict = _parse_json(raw)
    except Exception as e:
        verdict = {
            "risk_level": "error",
            "risk_score":  0.0,
            "findings":    [],
            "summary":     f"Assessment error: {str(e)}"
        }

    verdict["section_title"] = chunk["section_title"]
    verdict["source"]        = chunk["source"]
    verdict["retrieved"]     = retrieved
    return verdict