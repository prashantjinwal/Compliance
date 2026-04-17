from __future__ import annotations

import logging
from uuid import uuid4

import httpx

from ingestion.adapters.base import SourceAdapter
from ingestion.models import RawRegulatoryItem

logger = logging.getLogger(__name__)


class GenericDocumentFeedAdapter(SourceAdapter):
    """Official document/feed adapter.

    MVP behavior: try to fetch text from the configured official URL. If the
    regulator page requires custom parsing, add parser-specific logic here or in a
    source-specific adapter. Mock items keep local tests deterministic.
    """

    def fetch_latest(self) -> list[RawRegulatoryItem]:
        return self.fetch_by_cursor(None)

    def fetch_by_cursor(self, cursor: str | None) -> list[RawRegulatoryItem]:
        if self.source.mock_items:
            return self._raw_items_from_mock()

        try:
            response = httpx.get(self.source.base_url, headers=self.source.headers, timeout=15)
            response.raise_for_status()
            payload = {
                "id": str(uuid4()),
                "title": self.source.source_name,
                "summary": "Fetched official document feed content.",
                "full_text": response.text,
                "source_url": self.source.base_url,
            }
            return [RawRegulatoryItem(raw_item_id=payload["id"], source_id=self.source.source_id, cursor=cursor, payload=payload)]
        except Exception as exc:
            logger.warning("Document feed fetch failed for %s: %s", self.source.source_id, exc)
            return self._raw_items_from_mock()

