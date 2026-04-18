import json
import os
import re

try:
    from groq import Groq
except ImportError:
    Groq = None

from .prompt import build_prompt
from .retriever import retrieve_regulations


_client = None

def get_client():
    global _client
    if _client is None:
        if Groq is None:
            raise RuntimeError("The 'groq' package is not installed.")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        _client = Groq(api_key=api_key)
    return _client


def _parse_json(raw: str) -> dict:
    cleaned = (raw or "").strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        verdict = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        verdict = json.loads(match.group(0))

    return {
        "risk_level": verdict.get("risk_level", "error"),
        "risk_score": verdict.get("risk_score", 0.0),
        "findings": verdict.get("findings", []),
        "compliant_elements": verdict.get("compliant_elements", []),
        "summary": verdict.get("summary", "No summary returned by the model."),
    }

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


def assess_document(chunks: list[dict]) -> list[dict]:
    return [assess_chunk(chunk) for chunk in chunks]
