from __future__ import annotations

import os
import tempfile
from collections import Counter
from pathlib import Path

SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "compliant": 0,
    "unverified": 0,
    "error": 0,
}


def _load_rag_modules():
    from compliance_rag.highlight.report import build_json_summary, generate_report
    from compliance_rag.ingestion.chunker import chunk_document
    from compliance_rag.ingestion.parser import parse_document
    from compliance_rag.rag.assessor import assess_document, get_client
    from compliance_rag.rag.retriever import retrieve_regulations
    from compliance_rag.vectorstore.qdrant import setup_collection

    return {
        "build_json_summary": build_json_summary,
        "generate_report": generate_report,
        "chunk_document": chunk_document,
        "parse_document": parse_document,
        "assess_document": assess_document,
        "get_client": get_client,
        "retrieve_regulations": retrieve_regulations,
        "setup_collection": setup_collection,
    }


def _ensure_vector_collection(modules) -> None:
    modules["setup_collection"]()


def _build_analysis_response(verdicts: list[dict], document_name: str, modules) -> dict:
    summary_payload = modules["build_json_summary"](verdicts, document_name)
    report = modules["generate_report"](verdicts, document_name)
    levels = [verdict.get("risk_level", "error") for verdict in verdicts]
    counts = Counter(levels)
    average_score = 0

    if verdicts:
        average_score = round(
            sum(float(verdict.get("risk_score", 0.0)) for verdict in verdicts)
            / len(verdicts)
            * 100
        )

    highest_level = "compliant"
    for level in levels:
        if SEVERITY_ORDER.get(level, 0) > SEVERITY_ORDER.get(highest_level, 0):
            highest_level = level

    findings = []
    actions = []
    citations = []

    for verdict in verdicts:
        for finding in verdict.get("findings", []):
            findings.append(
                {
                    "issue": finding.get("issue", ""),
                    "cited_regulation": finding.get("cited_regulation", ""),
                    "cited_section": finding.get("cited_section", ""),
                    "problematic_text": finding.get("problematic_text", ""),
                    "why_it_matters": finding.get("why_it_matters", ""),
                    "fix": finding.get("fix", ""),
                    "section_title": verdict.get("section_title", ""),
                }
            )

            if finding.get("fix"):
                actions.append(
                    {
                        "title": finding.get("issue", "Recommended action"),
                        "description": finding.get("fix"),
                    }
                )

            if finding.get("cited_regulation") or finding.get("cited_section"):
                citations.append(
                    {
                        "regulation": finding.get("cited_regulation", ""),
                        "section": finding.get("cited_section", ""),
                    }
                )

    deduped_actions = []
    seen_actions = set()
    for action in actions:
        key = (action["title"], action["description"])
        if key in seen_actions:
            continue
        seen_actions.add(key)
        deduped_actions.append(action)

    deduped_citations = []
    seen_citations = set()
    for citation in citations:
        key = (citation["regulation"], citation["section"])
        if key in seen_citations:
            continue
        seen_citations.add(key)
        deduped_citations.append(citation)

    operational_impact = min(
        100,
        counts["critical"] * 30 + counts["high"] * 20 + counts["medium"] * 10,
    )
    technical_impact = min(100, len(findings) * 15)
    financial_impact = min(
        100,
        counts["critical"] * 25 + counts["high"] * 15 + counts["medium"] * 8,
    )

    overview = (
        summary_payload.get("top_findings", [{}])[0].get("summary")
        if summary_payload.get("top_findings")
        else "Assessment completed."
    )

    return {
        "document": document_name,
        "total_sections": summary_payload.get("total_sections", len(verdicts)),
        "risk_score": average_score,
        "risk_label": highest_level.replace("_", " ").title(),
        "summary": overview,
        "note": (
            f"{counts['critical']} critical, {counts['high']} high, and "
            f"{counts['medium']} medium-risk sections were identified."
        ),
        "operational_impact": operational_impact,
        "technical_impact": technical_impact,
        "financial_impact": financial_impact,
        "actions": deduped_actions[:6],
        "top_findings": findings[:6],
        "citations": deduped_citations[:10],
        "report": report,
        "verdicts": verdicts,
    }


def analyze_text(text: str, source_name: str = "ad-hoc-input.txt") -> dict:
    modules = _load_rag_modules()
    _ensure_vector_collection(modules)
    parsed = {
        "text": text,
        "pages": [],
        "source": source_name,
    }
    chunks = modules["chunk_document"](parsed)
    verdicts = modules["assess_document"](chunks)
    return _build_analysis_response(verdicts, source_name, modules)


def analyze_uploaded_file(uploaded_file) -> dict:
    modules = _load_rag_modules()
    _ensure_vector_collection(modules)
    suffix = Path(uploaded_file.name).suffix or ".txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        parsed = modules["parse_document"](tmp_path)
        parsed["source"] = uploaded_file.name
        chunks = modules["chunk_document"](parsed)
        verdicts = modules["assess_document"](chunks)
        return _build_analysis_response(verdicts, uploaded_file.name, modules)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def answer_query(message: str) -> dict:
    modules = _load_rag_modules()
    _ensure_vector_collection(modules)
    retrieved = modules["retrieve_regulations"](message, top_k=5)

    if not retrieved:
        return {
            "message": "No matching regulations were found in the current knowledge base.",
            "citations": [],
        }

    context = "\n\n".join(
        [
            (
                f"Source: {item['source']}\n"
                f"Section: {item['section_title']}\n"
                f"Text: {item['text'][:600]}"
            )
            for item in retrieved
        ]
    )

    response = modules["get_client"]().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a compliance assistant. Answer strictly from the "
                    "retrieved regulatory context. If the context is insufficient, "
                    "say so clearly."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{message}\n\n"
                    f"Regulatory context:\n{context}\n\n"
                    "Provide a concise answer and mention the most relevant source."
                ),
            },
        ],
        temperature=0.1,
        max_tokens=700,
    )

    return {
        "message": response.choices[0].message.content,
        "citations": [
            {
                "source": item["source"],
                "section_title": item["section_title"],
                "score": item.get("score"),
            }
            for item in retrieved
        ],
    }
