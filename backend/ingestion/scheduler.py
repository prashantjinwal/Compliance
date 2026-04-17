from __future__ import annotations

import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from ingestion.service import IngestionService

logger = logging.getLogger(__name__)


class PollingScheduler:
    def __init__(self, service: IngestionService | None = None):
        self.service = service or IngestionService()
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        for source in self.service.registry.list_sources(active_only=True):
            self.scheduler.add_job(
                self._sync_with_retry,
                "interval",
                minutes=source.polling_interval_minutes,
                args=[source.source_id],
                id=f"sync:{source.source_id}",
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
        self.scheduler.start()
        logger.info("Started polling scheduler with %s jobs", len(self.scheduler.get_jobs()))

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def _sync_with_retry(self, source_id: str) -> None:
        delay_seconds = 1
        for attempt in range(1, 4):
            result = self.service.sync_source(source_id)
            if result.get("status") == "success":
                return
            logger.warning("Sync attempt %s failed for %s; retrying in %ss", attempt, source_id, delay_seconds)
            self.scheduler.add_job(
                self._sync_with_retry,
                "date",
                run_date=datetime.utcnow() + timedelta(seconds=delay_seconds),
                args=[source_id],
                id=f"retry:{source_id}:{attempt}",
                replace_existing=True,
            )
            delay_seconds *= 2
            return
