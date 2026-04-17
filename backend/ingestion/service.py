from __future__ import annotations

import logging
from datetime import datetime
from uuid import uuid4

from compliance.service import ComplianceAssessmentService
from graph.updater import GraphUpdater
from ingestion.adapters.factory import build_adapter
from ingestion.models import RegulatoryEvent, RegulatoryEventType, RouteTarget, SourceConfig, SourceSyncRun
from ingestion.registry import SourceRegistry
from ingestion.router import RoutingEngine
from ingestion.store import IngestionStore
from rag.indexer import RagIndexer

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        registry: SourceRegistry | None = None,
        store: IngestionStore | None = None,
        router: RoutingEngine | None = None,
        rag_indexer: RagIndexer | None = None,
        graph_updater: GraphUpdater | None = None,
        assessment_service: ComplianceAssessmentService | None = None,
    ):
        self.registry = registry or SourceRegistry()
        self.store = store or IngestionStore()
        self.router = router or RoutingEngine()
        self.rag_indexer = rag_indexer
        self.graph_updater = graph_updater or GraphUpdater()
        self.assessment_service = assessment_service or ComplianceAssessmentService()
        for source in self.registry.list_sources():
            self.store.upsert_source(source)

    def list_sources(self) -> list[dict]:
        return [source.model_dump(mode="json") for source in self.registry.list_sources()]

    def upsert_source(self, source: SourceConfig) -> SourceConfig:
        saved = self.registry.upsert(source)
        self.store.upsert_source(saved)
        return saved

    def sync_source(self, source_id: str) -> dict:
        source = self.registry.get(source_id)
        run = SourceSyncRun(run_id=str(uuid4()), source_id=source.source_id)
        self.store.create_sync_run(run)
        adapter = build_adapter(source)
        changed_count = 0
        last_cursor = self.store.get_last_cursor(source.source_id)

        try:
            raw_items = adapter.fetch_by_cursor(last_cursor)
            run.fetched_count = len(raw_items)
            for raw_item in raw_items:
                run.last_seen_cursor = raw_item.cursor or run.last_seen_cursor
                self.store.save_raw_item(raw_item)
                try:
                    normalized = adapter.normalize(raw_item)
                    previous = self.store.get_latest_regulation(normalized.regulation_id)
                    event_type = RegulatoryEventType(adapter.detect_change(previous, normalized))
                    if event_type != RegulatoryEventType.NO_CHANGE:
                        changed_count += 1
                        self.store.save_regulation_version(normalized)

                    event = RegulatoryEvent(
                        event_id=str(uuid4()),
                        event_type=event_type,
                        source=source,
                        normalized=normalized,
                        previous_version_id=previous.version_id if previous else None,
                    )
                    event.routes = self.router.route(event)
                    self.store.save_event(event)
                    self._dispatch(event)
                except Exception as exc:
                    logger.exception("Failed to parse raw item %s from %s", raw_item.raw_item_id, source.source_id)
                    self.store.save_dead_letter(str(uuid4()), source.source_id, raw_item.payload, str(exc))

            run.changed_count = changed_count
            run.status = "success"
            run.finished_at = datetime.utcnow()
            self.store.finish_sync_run(run)
            return {
                "run": run.model_dump(mode="json"),
                "status": "success",
                "fetched_count": run.fetched_count,
                "changed_count": changed_count,
            }
        except Exception as exc:
            logger.exception("Sync failed for source %s", source.source_id)
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.utcnow()
            self.store.finish_sync_run(run)
            return {"run": run.model_dump(mode="json"), "status": "failed", "error": str(exc)}

    def sync_all_active(self) -> list[dict]:
        results = []
        for source in self.registry.list_sources(active_only=True):
            results.append(self.sync_source(source.source_id))
        return results

    def _dispatch(self, event: RegulatoryEvent) -> None:
        regulation = event.normalized
        if RouteTarget.RAG_INDEXER in event.routes:
            self.store.enqueue_job(
                "rag_index_jobs",
                f"rag:{regulation.regulation_id}:{regulation.version_id}",
                regulation.regulation_id,
                regulation.version_id,
                event.model_dump(mode="json"),
            )
            indexer = self._rag_indexer()
            indexer.reindex(regulation)

        if RouteTarget.GRAPH_UPDATER in event.routes:
            self.store.enqueue_job(
                "graph_update_jobs",
                f"graph:{regulation.regulation_id}:{regulation.version_id}",
                regulation.regulation_id,
                regulation.version_id,
                event.model_dump(mode="json"),
            )
            self.graph_updater.update(regulation)

        if RouteTarget.COMPLIANCE_ASSESSMENT_QUEUE in event.routes:
            assessment = self.assessment_service.assess(regulation)
            self.store.save_assessment(
                assessment.assessment_id,
                assessment.regulation_id,
                assessment.model_dump(mode="json"),
                assessment.generated_at,
            )

        if RouteTarget.ALERTING_QUEUE in event.routes:
            self.store.save_alert(
                f"alert:{event.event_id}",
                regulation.regulation_id,
                regulation.title,
                regulation.urgency,
                {
                    "event_id": event.event_id,
                    "title": regulation.title,
                    "change_type": event.event_type.value,
                    "effective_date": regulation.effective_date.isoformat() if regulation.effective_date else None,
                    "owner_role": regulation.likely_owner_role,
                    "impacted_business_tags": regulation.impacted_business_tags,
                },
            )

    def _rag_indexer(self) -> RagIndexer:
        if self.rag_indexer is None:
            self.rag_indexer = RagIndexer()
        return self.rag_indexer
