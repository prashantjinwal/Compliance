from __future__ import annotations

import logging
import uuid
import atexit

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, Filter, FieldCondition, MatchValue, PointStruct, VectorParams

from ingestion.models import NormalizedRegulation, RagDocument
from rag.chunker import chunk_regulation

logger = logging.getLogger(__name__)

COLLECTION = "regulatory_rag"


class RagIndexer:
    def __init__(self, client: QdrantClient | None = None):
        self.client = client or QdrantClient(path="./qdrant_regulatory_rag")
        self._ensure_collection()
        atexit.register(self.close)

    def reindex(self, regulation: NormalizedRegulation) -> list[RagDocument]:
        self.mark_previous_versions_stale(regulation.regulation_id, regulation.version_id)
        chunks = chunk_regulation(regulation)
        if not chunks:
            return []
        self.client.upsert(
            collection_name=COLLECTION,
            points=[
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.document_id)),
                    vector=self._embed_stub(chunk.text),
                    payload={"text": chunk.text, **chunk.metadata},
                )
                for chunk in chunks
            ],
        )
        logger.info("Indexed %s RAG chunks for %s", len(chunks), regulation.regulation_id)
        return chunks

    def mark_previous_versions_stale(self, regulation_id: str, current_version_id: str) -> None:
        points, _ = self.client.scroll(
            collection_name=COLLECTION,
            scroll_filter=Filter(must=[FieldCondition(key="regulation_id", match=MatchValue(value=regulation_id))]),
            limit=1000,
            with_payload=True,
        )
        stale_points = []
        for point in points:
            payload = dict(point.payload or {})
            if payload.get("version_id") == current_version_id:
                continue
            payload["is_stale"] = True
            stale_points.append(PointStruct(id=point.id, vector=point.vector or self._embed_stub(payload.get("text", "")), payload=payload))
        if stale_points:
            self.client.upsert(collection_name=COLLECTION, points=stale_points)

    def _ensure_collection(self) -> None:
        existing = [collection.name for collection in self.client.get_collections().collections]
        if COLLECTION not in existing:
            self.client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=16, distance=Distance.COSINE),
            )

    def close(self) -> None:
        self.client.close()

    @staticmethod
    def _embed_stub(text: str) -> list[float]:
        """Deterministic placeholder embedding.

        Replace with your local/API embedder. Keeping this model-agnostic lets the
        ingestion flow run in CI and local MVP environments without model downloads.
        """
        buckets = [0.0] * 16
        for index, char in enumerate(text.encode("utf-8")[:2048]):
            buckets[index % 16] += char / 255.0
        norm = sum(value * value for value in buckets) ** 0.5 or 1.0
        return [value / norm for value in buckets]
