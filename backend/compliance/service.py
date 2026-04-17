from __future__ import annotations

from compliance.models import ComplianceAssessment
from ingestion.models import NormalizedRegulation


DOCUMENTS_BY_TAG = {
    "data privacy": ["Privacy Policy", "Cookie Policy", "Data Processing Addendum"],
    "GST / VAT / sales tax": ["Tax invoices", "Bookkeeping records", "VAT/GST returns"],
    "payment compliance": ["Checkout disclosures", "Payment provider agreement", "Refund policy"],
    "consumer protection": ["Terms of Service", "Warranty policy", "Complaint handling SOP"],
    "return/refund policies": ["Refund Policy", "Returns SOP"],
    "marketplace seller obligations": ["Marketplace seller terms", "Operations SOP"],
    "advertising/claims compliance": ["Ad copy review checklist", "Claims substantiation file"],
    "corporate filings": ["Corporate minute book", "Annual filing calendar"],
}


class ComplianceAssessmentService:
    def assess(self, regulation: NormalizedRegulation) -> ComplianceAssessment:
        documents = sorted({
            doc
            for tag in regulation.impacted_business_tags
            for doc in DOCUMENTS_BY_TAG.get(tag, ["Founder compliance checklist"])
        })
        risk_level = "high" if regulation.severity == "high" or regulation.urgency == "high" else "medium"
        relevance_score = min(1.0, 0.35 + 0.15 * len(regulation.impacted_business_tags) + (0.2 if risk_level == "high" else 0))
        actions = [
            f"Assign review to {regulation.likely_owner_role or 'founder'}",
            "Compare current policies against the updated regulatory text",
            "Record decision and implementation status in the compliance tracker",
        ]
        if regulation.effective_date:
            actions.append(f"Complete review before {regulation.effective_date.date().isoformat()}")

        return ComplianceAssessment(
            regulation_id=regulation.regulation_id,
            relevance_score=round(relevance_score, 2),
            impacted_business_tags=regulation.impacted_business_tags,
            impacted_documents=documents,
            risk_level=risk_level,
            recommended_actions=actions,
            owner_role=regulation.likely_owner_role or "founder",
        )

