from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_ingestion_service
from ingestion.models import SourceConfig
from ingestion.service import IngestionService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
def list_sources(service: IngestionService = Depends(get_ingestion_service)):
    return service.list_sources()


@router.post("")
def create_or_update_source(source: SourceConfig, service: IngestionService = Depends(get_ingestion_service)):
    return service.upsert_source(source).model_dump(mode="json")


@router.post("/{source_id}/sync")
def sync_source(source_id: str, service: IngestionService = Depends(get_ingestion_service)):
    try:
        return service.sync_source(source_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {source_id}") from exc


@router.get("/{source_id}/runs")
def source_runs(source_id: str, service: IngestionService = Depends(get_ingestion_service)):
    return service.store.list_runs(source_id)

