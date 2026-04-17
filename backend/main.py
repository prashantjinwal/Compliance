from __future__ import annotations

import logging
import os

from fastapi import FastAPI

from api.assessments import router as assessments_router
from api.dashboard import router as dashboard_router
from api.regulations import router as regulations_router
from api.sources import router as sources_router
from ingestion.scheduler import PollingScheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Compliance Platform API", version="0.1.0")
app.include_router(sources_router)
app.include_router(regulations_router)
app.include_router(assessments_router)
app.include_router(dashboard_router)

_scheduler: PollingScheduler | None = None


@app.on_event("startup")
def startup() -> None:
    global _scheduler
    if os.getenv("ENABLE_INGESTION_SCHEDULER", "false").lower() == "true":
        _scheduler = PollingScheduler()
        _scheduler.start()


@app.on_event("shutdown")
def shutdown() -> None:
    if _scheduler:
        _scheduler.shutdown()


@app.get("/health")
def health():
    return {"status": "ok"}

