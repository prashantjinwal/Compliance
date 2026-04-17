from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


class SourceType(StrEnum):
    API = "api"
    RSS = "rss"
    WEBSERVICE = "webservice"
    DOCUMENT_FEED = "document_feed"
    SCRAPER_FALLBACK = "scraper_fallback"


class AuthType(StrEnum):
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class ChangeType(StrEnum):
    NEW = "new"
    AMENDED = "amended"
    REPEALED = "repealed"
    CORRECTED = "corrected"
    NO_CHANGE = "no_change"


class RegulatoryEventType(StrEnum):
    NEW_REGULATION = "NEW_REGULATION"
    UPDATED_REGULATION = "UPDATED_REGULATION"
    REPEALED_REGULATION = "REPEALED_REGULATION"
    NO_CHANGE = "NO_CHANGE"


class RouteTarget(StrEnum):
    RAG_INDEXER = "rag_indexer"
    GRAPH_UPDATER = "graph_updater"
    COMPLIANCE_ASSESSMENT_QUEUE = "compliance_assessment_queue"
    ALERTING_QUEUE = "alerting_queue"
    STORE_ONLY = "store_only"


class SourceConfig(BaseModel):
    source_id: str
    source_name: str
    jurisdiction: str
    domain: str
    source_type: SourceType
    base_url: str
    auth_type: AuthType = AuthType.NONE
    polling_interval_minutes: int = Field(default=1440, ge=1)
    parser_type: str = "generic_official_api"
    is_active: bool = True
    trust_level: Literal["high", "medium", "low"] = "high"
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    credential_env: str | None = None
    mock_items: list[dict[str, Any]] = Field(default_factory=list)


class RawRegulatoryItem(BaseModel):
    raw_item_id: str
    source_id: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    cursor: str | None = None
    payload: dict[str, Any]


class NormalizedRegulation(BaseModel):
    regulation_id: str
    source_id: str
    title: str
    summary: str = ""
    full_text: str
    jurisdiction: str
    domain: str
    issuing_authority: str
    effective_date: datetime | None = None
    publication_date: datetime | None = None
    updated_at_source: datetime | None = None
    source_url: str | None = None
    document_hash: str
    version_id: str
    change_type: ChangeType = ChangeType.NEW
    impacted_business_tags: list[str] = Field(default_factory=list)
    likely_owner_role: str | None = None
    severity: Literal["low", "medium", "high"] = "medium"
    urgency: Literal["low", "medium", "high"] = "medium"
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class RegulatoryEvent(BaseModel):
    event_id: str
    event_type: RegulatoryEventType
    source: SourceConfig
    normalized: NormalizedRegulation
    previous_version_id: str | None = None
    routes: list[RouteTarget] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SourceSyncRun(BaseModel):
    run_id: str
    source_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    status: Literal["running", "success", "failed"] = "running"
    fetched_count: int = 0
    changed_count: int = 0
    error_message: str | None = None
    last_seen_cursor: str | None = None


class RagDocument(BaseModel):
    document_id: str
    text: str
    metadata: dict[str, Any]


class GraphEntityPayload(BaseModel):
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)

