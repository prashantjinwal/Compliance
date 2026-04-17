from __future__ import annotations

from ingestion.models import GraphEntityPayload, NormalizedRegulation


def extract_entities(regulation: NormalizedRegulation) -> GraphEntityPayload:
    nodes = [
        {"type": "Regulation", "id": regulation.regulation_id, "properties": {"title": regulation.title, "version_id": regulation.version_id}},
        {"type": "Role", "id": regulation.likely_owner_role or "founder", "properties": {"name": regulation.likely_owner_role or "founder"}},
    ]
    edges = []

    for tag in regulation.impacted_business_tags:
        nodes.append({"type": "BusinessArea", "id": tag, "properties": {"name": tag}})
        nodes.append({"type": "Obligation", "id": f"{regulation.regulation_id}:{tag}:review", "properties": {"name": f"Review {tag} obligations"}})
        nodes.append({"type": "Risk", "id": f"{regulation.regulation_id}:{tag}:risk", "properties": {"level": regulation.severity}})
        edges.extend(
            [
                {"type": "REGULATION_APPLIES_TO", "from": regulation.regulation_id, "to": tag},
                {"type": "REGULATION_INTRODUCES", "from": regulation.regulation_id, "to": f"{regulation.regulation_id}:{tag}:review"},
                {"type": "OBLIGATION_CREATES", "from": f"{regulation.regulation_id}:{tag}:review", "to": f"{regulation.regulation_id}:{tag}:risk"},
                {"type": "RISK_OWNED_BY", "from": f"{regulation.regulation_id}:{tag}:risk", "to": regulation.likely_owner_role or "founder"},
            ]
        )

    if regulation.effective_date:
        deadline_id = f"{regulation.regulation_id}:effective_date"
        nodes.append({"type": "FilingDeadline", "id": deadline_id, "properties": {"date": regulation.effective_date.isoformat()}})
        edges.append({"type": "REGULATION_HAS_DEADLINE", "from": regulation.regulation_id, "to": deadline_id})

    return GraphEntityPayload(nodes=nodes, edges=edges)

