from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ingestion.models import NormalizedRegulation, RegulatoryEvent, SourceConfig, SourceSyncRun


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "compliance_ingestion.db"


class IngestionStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists regulatory_sources (
                    source_id text primary key,
                    payload_json text not null,
                    updated_at text not null
                );
                create table if not exists source_sync_runs (
                    run_id text primary key,
                    source_id text not null,
                    started_at text not null,
                    finished_at text,
                    status text not null,
                    fetched_count integer not null,
                    changed_count integer not null,
                    error_message text,
                    last_seen_cursor text
                );
                create table if not exists raw_regulatory_items (
                    raw_item_id text primary key,
                    source_id text not null,
                    fetched_at text not null,
                    cursor text,
                    payload_json text not null
                );
                create table if not exists normalized_regulations (
                    regulation_id text primary key,
                    source_id text not null,
                    latest_version_id text not null,
                    payload_json text not null,
                    updated_at text not null
                );
                create table if not exists regulation_versions (
                    version_pk text primary key,
                    regulation_id text not null,
                    version_id text not null,
                    document_hash text not null,
                    payload_json text not null,
                    created_at text not null
                );
                create table if not exists routing_events (
                    event_id text primary key,
                    regulation_id text not null,
                    event_type text not null,
                    routes_json text not null,
                    payload_json text not null,
                    created_at text not null
                );
                create table if not exists compliance_assessments (
                    assessment_id text primary key,
                    regulation_id text not null,
                    payload_json text not null,
                    generated_at text not null
                );
                create table if not exists rag_index_jobs (
                    job_id text primary key,
                    regulation_id text not null,
                    version_id text not null,
                    status text not null,
                    payload_json text not null,
                    created_at text not null
                );
                create table if not exists graph_update_jobs (
                    job_id text primary key,
                    regulation_id text not null,
                    version_id text not null,
                    status text not null,
                    payload_json text not null,
                    created_at text not null
                );
                create table if not exists alert_events (
                    alert_id text primary key,
                    regulation_id text not null,
                    title text not null,
                    urgency text not null,
                    payload_json text not null,
                    created_at text not null
                );
                create table if not exists dead_letter_items (
                    dead_letter_id text primary key,
                    source_id text not null,
                    raw_payload_json text not null,
                    error_message text not null,
                    created_at text not null
                );
                """
            )

    def upsert_source(self, source: SourceConfig) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into regulatory_sources(source_id, payload_json, updated_at)
                values (?, ?, ?)
                on conflict(source_id) do update set payload_json=excluded.payload_json, updated_at=excluded.updated_at
                """,
                (source.source_id, source.model_dump_json(), datetime.utcnow().isoformat()),
            )

    def create_sync_run(self, run: SourceSyncRun) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into source_sync_runs values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.source_id,
                    run.started_at.isoformat(),
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.status,
                    run.fetched_count,
                    run.changed_count,
                    run.error_message,
                    run.last_seen_cursor,
                ),
            )

    def finish_sync_run(self, run: SourceSyncRun) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                update source_sync_runs
                set finished_at=?, status=?, fetched_count=?, changed_count=?, error_message=?, last_seen_cursor=?
                where run_id=?
                """,
                (
                    run.finished_at.isoformat() if run.finished_at else datetime.utcnow().isoformat(),
                    run.status,
                    run.fetched_count,
                    run.changed_count,
                    run.error_message,
                    run.last_seen_cursor,
                    run.run_id,
                ),
            )

    def get_last_cursor(self, source_id: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                select last_seen_cursor from source_sync_runs
                where source_id=? and status='success' and last_seen_cursor is not null
                order by finished_at desc limit 1
                """,
                (source_id,),
            ).fetchone()
            return row["last_seen_cursor"] if row else None

    def get_latest_regulation(self, regulation_id: str) -> NormalizedRegulation | None:
        with self._connect() as conn:
            row = conn.execute(
                "select payload_json from normalized_regulations where regulation_id=?",
                (regulation_id,),
            ).fetchone()
            return NormalizedRegulation.model_validate_json(row["payload_json"]) if row else None

    def save_raw_item(self, raw_item: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert or replace into raw_regulatory_items values (?, ?, ?, ?, ?)
                """,
                (
                    raw_item.raw_item_id,
                    raw_item.source_id,
                    raw_item.fetched_at.isoformat(),
                    raw_item.cursor,
                    raw_item.model_dump_json(),
                ),
            )

    def save_regulation_version(self, regulation: NormalizedRegulation) -> None:
        now = datetime.utcnow().isoformat()
        version_pk = f"{regulation.regulation_id}:{regulation.version_id}"
        with self._connect() as conn:
            conn.execute(
                """
                insert or ignore into regulation_versions values (?, ?, ?, ?, ?, ?)
                """,
                (
                    version_pk,
                    regulation.regulation_id,
                    regulation.version_id,
                    regulation.document_hash,
                    regulation.model_dump_json(),
                    now,
                ),
            )
            conn.execute(
                """
                insert into normalized_regulations values (?, ?, ?, ?, ?)
                on conflict(regulation_id) do update set
                    source_id=excluded.source_id,
                    latest_version_id=excluded.latest_version_id,
                    payload_json=excluded.payload_json,
                    updated_at=excluded.updated_at
                """,
                (
                    regulation.regulation_id,
                    regulation.source_id,
                    regulation.version_id,
                    regulation.model_dump_json(),
                    now,
                ),
            )

    def save_event(self, event: RegulatoryEvent) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert or replace into routing_events values (?, ?, ?, ?, ?, ?)",
                (
                    event.event_id,
                    event.normalized.regulation_id,
                    event.event_type,
                    json.dumps([route.value for route in event.routes]),
                    event.model_dump_json(),
                    event.created_at.isoformat(),
                ),
            )

    def enqueue_job(self, table: str, job_id: str, regulation_id: str, version_id: str, payload: dict[str, Any]) -> None:
        if table not in {"rag_index_jobs", "graph_update_jobs"}:
            raise ValueError(f"Unsupported job table: {table}")
        with self._connect() as conn:
            conn.execute(
                f"insert or replace into {table} values (?, ?, ?, ?, ?, ?)",
                (job_id, regulation_id, version_id, "queued", json.dumps(payload), datetime.utcnow().isoformat()),
            )

    def save_assessment(self, assessment_id: str, regulation_id: str, payload: dict[str, Any], generated_at: datetime) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert or replace into compliance_assessments values (?, ?, ?, ?)",
                (assessment_id, regulation_id, json.dumps(payload), generated_at.isoformat()),
            )

    def save_alert(self, alert_id: str, regulation_id: str, title: str, urgency: str, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert or replace into alert_events values (?, ?, ?, ?, ?, ?)",
                (alert_id, regulation_id, title, urgency, json.dumps(payload), datetime.utcnow().isoformat()),
            )

    def save_dead_letter(self, dead_letter_id: str, source_id: str, raw_payload: dict[str, Any], error_message: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert or replace into dead_letter_items values (?, ?, ?, ?, ?)",
                (dead_letter_id, source_id, json.dumps(raw_payload), error_message, datetime.utcnow().isoformat()),
            )

    def list_sources(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            return [json.loads(row["payload_json"]) for row in conn.execute("select payload_json from regulatory_sources")]

    def list_runs(self, source_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select * from source_sync_runs where source_id=? order by started_at desc", (source_id,))
            return [dict(row) for row in rows]

    def list_regulations(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            return [json.loads(row["payload_json"]) for row in conn.execute("select payload_json from normalized_regulations")]

    def get_regulation_payload(self, regulation_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("select payload_json from normalized_regulations where regulation_id=?", (regulation_id,)).fetchone()
            return json.loads(row["payload_json"]) if row else None

    def recent_changes(self, hours: int = 24) -> list[dict[str, Any]]:
        threshold = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        with self._connect() as conn:
            rows = conn.execute("select payload_json from routing_events where created_at >= ? order by created_at desc", (threshold,))
            return [json.loads(row["payload_json"]) for row in rows]

    def list_assessments(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            return [json.loads(row["payload_json"]) for row in conn.execute("select payload_json from compliance_assessments")]

    def daily_digest(self) -> dict[str, Any]:
        changes = self.recent_changes(hours=24)
        with self._connect() as conn:
            alerts = [json.loads(row["payload_json"]) for row in conn.execute("select payload_json from alert_events order by created_at desc limit 25")]
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "change_count": len(changes),
            "high_priority_alerts": alerts,
            "changes": changes,
        }

