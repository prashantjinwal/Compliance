def generate_report(verdicts: list, document_name: str) -> str:
    lines = [
        "=" * 60,
        f"COMPLIANCE RISK REPORT: {document_name}",
        "=" * 60,
        ""
    ]
    
    critical = [v for v in verdicts if v.get("risk_level") == "critical"]
    high     = [v for v in verdicts if v.get("risk_level") == "high"]
    
    lines += [
        f"Sections assessed : {len(verdicts)}",
        f"Critical issues   : {len(critical)}",
        f"High issues       : {len(high)}",
        f"Requires review   : {len(critical) + len(high)}",
        ""
    ]
    
    for verdict in verdicts:
        level = verdict.get("risk_level", "unknown").upper()
        score = verdict.get("risk_score", 0.0)
        
        if level in ("COMPLIANT", "LOW"):
            continue  # Only show problems in the report
        
        lines += [
            f"{'─' * 60}",
            f"[{level}]  {verdict.get('section_title', 'Unknown section')}",
            f"Source  : {verdict.get('source', '')}",
            f"Score   : {score:.2f}",
            f"Summary : {verdict.get('summary', '')}",
            ""
        ]
        
        for i, finding in enumerate(verdict.get("findings", []), 1):
            lines += [
                f"  Finding {i}:",
                f"    Issue    : {finding.get('issue', '')}",
                f"    Cited    : {finding.get('cited_regulation', '')} — "
                             f"{finding.get('cited_section', '')}",
                f"    Trigger  : \"{finding.get('problematic_text', '')}\"",
                f"    Why      : {finding.get('why_it_matters', '')}",
                f"    Fix      : {finding.get('fix', '')}",
                ""
            ]
        
        if verdict.get("compliant_elements"):
            lines.append(
                f"  Compliant : "
                f"{', '.join(verdict['compliant_elements'][:3])}"
            )
        lines.append("")
    
    return "\n".join(lines)

def highlight_problems(chunk_text: str, findings: list) -> str:
    """
    Inserts inline severity markers after each problematic phrase
    found in the chunk text.
    """
    annotated = chunk_text
    offset    = 0
    
    for finding in findings:
        trigger = finding.get("problematic_text", "")
        if not trigger or trigger not in annotated:
            continue
        
        level  = finding.get("risk_level", "risk").upper()
        marker = f" ◄ [{level}]"
        pos    = annotated.find(trigger) + len(trigger)
        annotated = annotated[:pos] + marker + annotated[pos:]
    
    return annotated

def build_json_summary(verdicts: list, document_name: str) -> dict:
    return {
        "document":        document_name,
        "total_sections":  len(verdicts),
        "critical":        [v for v in verdicts if v.get("risk_level") == "critical"],
        "high":            [v for v in verdicts if v.get("risk_level") == "high"],
        "medium":          [v for v in verdicts if v.get("risk_level") == "medium"],
        "compliant":       [v for v in verdicts if v.get("risk_level") == "compliant"],
        "top_findings":    verdicts[:3]
    }
