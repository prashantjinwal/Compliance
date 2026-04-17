from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_ingestion_service
from ingestion.service import IngestionService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/digest")
def digest(service: IngestionService = Depends(get_ingestion_service)):
    return service.store.daily_digest()

