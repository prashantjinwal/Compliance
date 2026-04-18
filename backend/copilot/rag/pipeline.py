import json
import re
from datetime import date, timedelta

from .llm import get_llm
from .vector_store import load_vector_store


ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical"}
ALLOWED_ROLES = {"Legal", "IT", "Finance", "HR", "Compliance", "Admin"}
ROLE_LOOKUP = {
    "legal": "Legal",
    "it": "IT",
    "finance": "Finance",
    "hr": "HR",
    "compliance": "Compliance",
    "admin": "Admin",
}


def _call_llm(prompt):
    response = get_llm().invoke(prompt)

    if hasattr(response, "content"):
        return response.content

    return str(response)


def _extract_json(raw_text, fallback):
    cleaned = (raw_text or "").strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
        if not match:
            return fallback

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return fallback


def _normalize_role(role_value):
    if not role_value:
        return "Compliance"

    normalized = ROLE_LOOKUP.get(str(role_value).strip().lower())
    if normalized:
        return normalized

    return "Compliance"


def summarize_document(text):
    prompt = f"""
You are a compliance analyst.
Summarize the following regulation or policy in simple business language.
Focus on what changed, who is affected, and what the organization should do next.

Document:
{text[:4000]}
"""

    return _call_llm(prompt)


def analyze_regulation(raw_text):
    prompt = f"""
You are a compliance analyst.
Read the regulation text and return ONLY valid JSON with this shape:
{{
  "summary": "short executive summary",
  "key_changes": "important changes in 2-4 sentences",
  "obligations": ["obligation 1", "obligation 2"],
  "relevance_score": 0.0
}}

Rules:
- relevance_score must be between 0.0 and 1.0
- obligations must be concrete actions or duties
- return no markdown, no commentary, JSON only

Regulation text:
{raw_text[:7000]}
"""

    fallback = {
        "summary": summarize_document(raw_text),
        "key_changes": "",
        "obligations": [],
        "relevance_score": 0.5,
    }
    parsed = _extract_json(_call_llm(prompt), fallback)

    obligations = parsed.get("obligations", [])
    if not isinstance(obligations, list):
        obligations = [str(obligations)] if obligations else []

    try:
        relevance_score = float(parsed.get("relevance_score", 0.5))
    except (TypeError, ValueError):
        relevance_score = 0.5

    relevance_score = max(0.0, min(1.0, relevance_score))

    return {
        "summary": str(parsed.get("summary") or fallback["summary"]),
        "key_changes": str(parsed.get("key_changes") or ""),
        "obligations": [str(item).strip() for item in obligations if str(item).strip()],
        "relevance_score": relevance_score,
    }


def assess_risk(analysis_data):
    prompt = f"""
You are a compliance risk analyst.
Assess the risk of the following regulation analysis and return ONLY valid JSON:
{{
  "risk_level": "low|medium|high|critical",
  "impacted_area": "short area name",
  "description": "why this is risky",
  "responsible_role": "Legal|IT|Finance|HR|Compliance|Admin"
}}

Analysis summary:
{analysis_data.get("summary", "")}

Key changes:
{analysis_data.get("key_changes", "")}

Obligations:
{json.dumps(analysis_data.get("obligations", []))}
"""

    fallback = {
        "risk_level": "medium",
        "impacted_area": "Compliance Operations",
        "description": "Manual risk review is required.",
        "responsible_role": "Compliance",
    }
    parsed = _extract_json(_call_llm(prompt), fallback)

    risk_level = str(parsed.get("risk_level", fallback["risk_level"])).strip().lower()
    if risk_level not in ALLOWED_RISK_LEVELS:
        risk_level = fallback["risk_level"]

    return {
        "risk_level": risk_level,
        "impacted_area": str(parsed.get("impacted_area") or fallback["impacted_area"]),
        "description": str(parsed.get("description") or fallback["description"]),
        "responsible_role": _normalize_role(parsed.get("responsible_role")),
    }


def generate_tasks(risk_data):
    prompt = f"""
You are a compliance program manager.
Create 3 concrete compliance tasks for the following risk and return ONLY valid JSON array.

Each array item must have:
{{
  "title": "task title",
  "description": "task description",
  "suggested_action": "specific next step",
  "deadline": "YYYY-MM-DD",
  "assigned_role": "Legal|IT|Finance|HR|Compliance|Admin"
}}

Risk data:
{json.dumps(risk_data)}
"""

    fallback = [
        {
            "title": "Review compliance impact",
            "description": "Review the regulation impact and confirm required remediation steps.",
            "suggested_action": "Assign an owner and define the implementation plan.",
            "deadline": (date.today() + timedelta(days=7)).isoformat(),
            "assigned_role": "Compliance",
        }
    ]
    parsed = _extract_json(_call_llm(prompt), fallback)

    if not isinstance(parsed, list):
        parsed = fallback

    normalized_tasks = []
    for index, task in enumerate(parsed):
        if not isinstance(task, dict):
            continue

        title = str(task.get("title") or f"Compliance task {index + 1}").strip()
        description = str(task.get("description") or "").strip()
        suggested_action = str(task.get("suggested_action") or "").strip()
        deadline = str(task.get("deadline") or (date.today() + timedelta(days=7)).isoformat()).strip()

        try:
            date.fromisoformat(deadline)
        except ValueError:
            deadline = (date.today() + timedelta(days=7)).isoformat()

        normalized_tasks.append(
            {
                "title": title,
                "description": description or suggested_action or "Review and remediate this compliance issue.",
                "suggested_action": suggested_action or description or "Review and remediate this compliance issue.",
                "deadline": deadline,
                "assigned_role": _normalize_role(task.get("assigned_role")),
            }
        )

    return normalized_tasks or fallback


def chat_with_doc(document_id, query):
    vectorstore = load_vector_store(document_id)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No matching context found."

    prompt = f"""
You are a compliance assistant.
Answer the question using only the provided document context.
If the answer is not in the context, say that clearly.

Context:
{context[:6000]}

Question:
{query}
"""

    return _call_llm(prompt)
