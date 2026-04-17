from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import uuid4

from ingestion.classifier import classify_ecommerce_relevance, enrich_with_llm_if_configured
from ingestion.models import GraphEntityPayload, NormalizedRegulation, RawRegulatoryItem, SourceConfig


class SourceAdapter(ABC):
    def __init__(self, source: SourceConfig):
        self.source = source

    @abstractmethod
    def fetch_latest(self) -> list[RawRegulatoryItem]:
        raise NotImplementedError

    @abstractmethod
    def fetch_by_cursor(self, cursor: str | None) -> list[RawRegulatoryItem]:
        raise NotImplementedError

    def normalize(self, raw_item: RawRegulatoryItem) -> NormalizedRegulation:
        payload = raw_item.payload
        full_text = str(payload.get("full_text") or payload.get("body") or payload.get("summary") or "")
        title = str(payload.get("title") or "Untitled regulatory item")
        summary = str(payload.get("summary") or full_text[:500])
        document_hash = self._hash_document(title, full_text, payload)
        version_key = self.extract_version_key(payload) or document_hash[:16]
        change_type = str(payload.get("change_type") or "new").lower()
        classification = enrich_with_llm_if_configured(
            classify_ecommerce_relevance(title, summary, full_text, self.source.domain),
            payload,
        )

        return NormalizedRegulation(
            regulation_id=str(payload.get("regulation_id") or payload.get("id") or raw_item.raw_item_id),
            source_id=self.source.source_id,
            title=title,
            summary=summary,
            full_text=full_text,
            jurisdiction=self.source.jurisdiction,
            domain=self.source.domain,
            issuing_authority=str(payload.get("issuing_authority") or self.source.source_name),
            effective_date=self._parse_dt(payload.get("effective_date")),
            publication_date=self._parse_dt(payload.get("publication_date")),
            updated_at_source=self._parse_dt(payload.get("updated_at_source")),
            source_url=payload.get("source_url") or self.source.base_url,
            document_hash=document_hash,
            version_id=str(payload.get("version_id") or version_key),
            change_type=change_type,
            impacted_business_tags=classification.impacted_business_tags,
            likely_owner_role=classification.likely_owner_role,
            severity=classification.severity,
            urgency=classification.urgency,
            raw_metadata=payload,
        )

    def extract_version_key(self, normalized_item: dict[str, Any] | NormalizedRegulation) -> str:
        if isinstance(normalized_item, NormalizedRegulation):
            return normalized_item.version_id
        for key in ("version_id", "updated_at_source", "publication_date", "id"):
            if normalized_item.get(key):
                return str(normalized_item[key])
        return ""

    def detect_change(self, old_item: NormalizedRegulation | None, new_item: NormalizedRegulation) -> str:
        if old_item is None:
            return "NEW_REGULATION"
        if old_item.change_type == "repealed" or new_item.change_type == "repealed":
            return "REPEALED_REGULATION"
        if old_item.document_hash != new_item.document_hash or old_item.version_id != new_item.version_id:
            return "UPDATED_REGULATION"
        return "NO_CHANGE"

    def to_rag_document(self, normalized_item: NormalizedRegulation) -> dict[str, Any]:
        return {
            "document_id": f"{normalized_item.regulation_id}:{normalized_item.version_id}",
            "text": normalized_item.full_text,
            "metadata": normalized_item.model_dump(mode="json", exclude={"full_text", "raw_metadata"}),
        }

    def to_graph_entities(self, normalized_item: NormalizedRegulation) -> GraphEntityPayload:
        nodes = [
            {"type": "Regulation", "id": normalized_item.regulation_id, "properties": normalized_item.model_dump(mode="json", exclude={"full_text"})},
            {"type": "Role", "id": normalized_item.likely_owner_role or "founder", "properties": {"name": normalized_item.likely_owner_role or "founder"}},
        ]
        edges = []
        for tag in normalized_item.impacted_business_tags:
            nodes.append({"type": "BusinessArea", "id": tag, "properties": {"name": tag}})
            edges.append({"type": "REGULATION_APPLIES_TO", "from": normalized_item.regulation_id, "to": tag})
        return GraphEntityPayload(nodes=nodes, edges=edges)

    def _raw_items_from_mock(self) -> list[RawRegulatoryItem]:
        return [
            RawRegulatoryItem(
                raw_item_id=str(item.get("id") or uuid4()),
                source_id=self.source.source_id,
                cursor=str(item.get("updated_at_source") or item.get("publication_date") or ""),
                payload=item,
            )
            for item in self.source.mock_items
        ]

    @staticmethod
    def _hash_document(title: str, full_text: str, payload: dict[str, Any]) -> str:
        stable = json.dumps({"title": title, "full_text": full_text, "source_url": payload.get("source_url")}, sort_keys=True)
        return hashlib.sha256(stable.encode("utf-8")).hexdigest()

    @staticmethod
    def _parse_dt(value: Any) -> datetime | None:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

