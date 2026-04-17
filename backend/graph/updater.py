from __future__ import annotations

import json
import logging
from pathlib import Path

from graph.entity_extractor import extract_entities
from ingestion.models import GraphEntityPayload, NormalizedRegulation

logger = logging.getLogger(__name__)


class GraphUpdater:
    def __init__(self, snapshot_path: Path | str = "graph_snapshot.jsonl"):
        self.snapshot_path = Path(snapshot_path)

    def update(self, regulation: NormalizedRegulation) -> GraphEntityPayload:
        payload = extract_entities(regulation)
        with self.snapshot_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload.model_dump(mode="json")) + "\n")
        logger.info("Prepared graph update for %s", regulation.regulation_id)
        return payload

