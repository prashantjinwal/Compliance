from __future__ import annotations

from dataclasses import dataclass


TAG_KEYWORDS: dict[str, list[str]] = {
    "GST / VAT / sales tax": ["gst", "vat", "sales tax", "tax invoice", "tax filing"],
    "consumer protection": ["consumer", "unfair", "warranty", "complaint", "dispute"],
    "return/refund policies": ["refund", "return", "cancellation", "chargeback"],
    "marketplace seller obligations": ["marketplace", "seller", "platform", "merchant"],
    "invoicing and bookkeeping": ["invoice", "bookkeeping", "accounting", "books", "records"],
    "data privacy": ["privacy", "personal data", "customer data", "processor", "controller", "retention"],
    "payment compliance": ["payment", "checkout", "card", "fee", "e-money"],
    "KYC / AML": ["kyc", "aml", "anti-money laundering", "beneficial owner"],
    "advertising/claims compliance": ["advertising", "claims", "greenwashing", "endorsement"],
    "corporate filings": ["filing", "annual return", "disclosure", "company registry"],
    "shipping/logistics documentation": ["shipping", "logistics", "customs", "delivery", "fulfillment"],
}

OWNER_BY_TAG = {
    "GST / VAT / sales tax": "finance",
    "consumer protection": "legal",
    "return/refund policies": "operations",
    "marketplace seller obligations": "operations",
    "invoicing and bookkeeping": "finance",
    "data privacy": "data/privacy",
    "payment compliance": "finance",
    "KYC / AML": "legal",
    "advertising/claims compliance": "growth",
    "corporate filings": "founder",
    "shipping/logistics documentation": "operations",
}


@dataclass(frozen=True)
class ClassificationResult:
    impacted_business_tags: list[str]
    likely_owner_role: str
    severity: str
    urgency: str


def classify_ecommerce_relevance(title: str, summary: str, full_text: str, domain: str) -> ClassificationResult:
    text = f"{title} {summary} {full_text} {domain}".lower()
    tags = [
        tag for tag, keywords in TAG_KEYWORDS.items()
        if any(keyword in text for keyword in keywords)
    ]

    if not tags and domain in {"privacy", "tax", "payments", "finance"}:
        tags = {
            "privacy": ["data privacy"],
            "tax": ["GST / VAT / sales tax"],
            "payments": ["payment compliance"],
            "finance": ["invoicing and bookkeeping"],
        }[domain]

    owner = OWNER_BY_TAG.get(tags[0], "founder") if tags else "founder"
    high_terms = ["deadline", "must", "penalty", "enforcement", "effective", "required"]
    severity = "high" if any(term in text for term in high_terms) else "medium"
    urgency = "high" if "effective" in text or "deadline" in text else "medium"

    return ClassificationResult(
        impacted_business_tags=tags,
        likely_owner_role=owner,
        severity=severity,
        urgency=urgency,
    )


def enrich_with_llm_if_configured(result: ClassificationResult, _: dict) -> ClassificationResult:
    """Optional LLM enrichment hook.

    Plug an OpenAI/local model call here when you want richer tagging. The ingestion
    pipeline remains model-agnostic by keeping the hook side-effect free.
    """
    return result

