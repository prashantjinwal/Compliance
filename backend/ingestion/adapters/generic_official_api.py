from __future__ import annotations

import logging
import os
from typing import Any
from uuid import uuid4

import httpx

from ingestion.adapters.base import SourceAdapter
from ingestion.models import RawRegulatoryItem

logger = logging.getLogger(__name__)


class GenericOfficialApiAdapter(SourceAdapter):
    """Official API adapter with mock fallback for MVP demos.

    Configure real regulator credentials through SourceConfig.credential_env and
    headers/params in source_registry.yaml. The adapter expects either a JSON list
    or a JSON object with an "items" field.
    """

    def fetch_latest(self) -> list[RawRegulatoryItem]:
        return self.fetch_by_cursor(None)

    def fetch_by_cursor(self, cursor: str | None) -> list[RawRegulatoryItem]:
        headers = dict(self.source.headers)
        if self.source.credential_env and os.getenv(self.source.credential_env):
            headers["Authorization"] = f"Bearer {os.getenv(self.source.credential_env)}"

        params: dict[str, Any] = dict(self.source.params)
        if cursor:
            params["cursor"] = cursor

        try:
            response = httpx.get(self.source.base_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", data) if isinstance(data, dict) else data
            return [
                RawRegulatoryItem(
                    raw_item_id=str(item.get("id") or item.get("url") or uuid4()),
                    source_id=self.source.source_id,
                    cursor=str(item.get("updated_at_source") or item.get("updated") or ""),
                    payload=item,
                )
                for item in items
            ]
        except Exception as exc:
            logger.warning("Using mock fallback for %s after fetch failure: %s", self.source.source_id, exc)
            return self._raw_items_from_mock()

