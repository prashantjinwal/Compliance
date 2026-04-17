from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_ingestion_service
from ingestion.service import IngestionService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("")
def list_assessments(service: IngestionService = Depends(get_ingestion_service)):
    return service.store.list_assessments()

