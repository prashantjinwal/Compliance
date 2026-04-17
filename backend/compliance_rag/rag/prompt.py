SYSTEM_PROMPT = """You are a senior compliance analyst. You assess document 
sections strictly against the provided regulatory context.

Critical rules:
- Every finding MUST cite a regulation ID and section from the context below.
- If no retrieved regulation supports a finding, do NOT flag it.
- Do not use general knowledge — only the provided regulatory context.
- Output valid JSON only. No preamble, no markdown fences."""

OUTPUT_SCHEMA = """{
  "risk_level": "critical | high | medium | low | compliant",
  "risk_score": <float 0.0-1.0>,
  "findings": [
    {
      "issue": "<one line description>",
      "cited_regulation": "<regulation source name>",
      "cited_section": "<section title from context>",
      "problematic_text": "<exact phrase from the document section>",
      "why_it_matters": "<one sentence explanation>",
      "fix": "<specific actionable remediation>"
    }
  ],
  "compliant_elements": ["<things done correctly>"],
  "summary": "<2-3 sentence plain English verdict>"
}"""

def build_prompt(document_chunk: str, retrieved_regulations: list) -> tuple:
    reg_context = _format_regulations(retrieved_regulations)
    
    user_prompt = f"""Assess this document section for compliance risks.

=== REGULATORY CONTEXT (cite from these only) ===
{reg_context}

=== DOCUMENT SECTION ===
{document_chunk[:1500]}

=== OUTPUT FORMAT ===
{OUTPUT_SCHEMA}"""
    
    return SYSTEM_PROMPT, user_prompt

def _format_regulations(regulations: list) -> str:
    parts = []
    for i, reg in enumerate(regulations, 1):
        parts.append(
            f"[{i}] Source: {reg['source']}\n"
            f"    Section: {reg['section_title']}\n"
            f"    Text: {reg['text'][:400]}"
        )
    return "\n\n".join(parts)