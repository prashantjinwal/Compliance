from __future__ import annotations

from ingestion.models import NormalizedRegulation


def metadata_for_regulation(regulation: NormalizedRegulation) -> dict:
    return {
        "regulation_id": regulation.regulation_id,
        "version_id": regulation.version_id,
        "source_id": regulation.source_id,
        "jurisdiction": regulation.jurisdiction,
        "domain": regulation.domain,
        "issuing_authority": regulation.issuing_authority,
        "publication_date": regulation.publication_date.isoformat() if regulation.publication_date else None,
        "effective_date": regulation.effective_date.isoformat() if regulation.effective_date else None,
        "impacted_business_tags": ",".join(regulation.impacted_business_tags),
        "source_url": regulation.source_url,
        "is_stale": False,
    }

