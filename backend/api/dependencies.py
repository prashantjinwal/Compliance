from __future__ import annotations

from functools import lru_cache

from ingestion.service import IngestionService


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService()

