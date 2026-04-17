from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_ingestion_service
from ingestion.service import IngestionService

router = APIRouter(prefix="/regulations", tags=["regulations"])


@router.get("")
def list_regulations(service: IngestionService = Depends(get_ingestion_service)):
    return service.store.list_regulations()


@router.get("/changes/recent")
def recent_changes(hours: int = 24, service: IngestionService = Depends(get_ingestion_service)):
    return service.store.recent_changes(hours=hours)


@router.get("/{regulation_id}")
def get_regulation(regulation_id: str, service: IngestionService = Depends(get_ingestion_service)):
    regulation = service.store.get_regulation_payload(regulation_id)
    if not regulation:
        raise HTTPException(status_code=404, detail=f"Unknown regulation_id: {regulation_id}")
    return regulation

