from __future__ import annotations

from pathlib import Path

import yaml

from ingestion.models import SourceConfig


DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "config" / "source_registry.yaml"


class SourceRegistry:
    def __init__(self, path: Path | str = DEFAULT_REGISTRY_PATH):
        self.path = Path(path)
        self._sources = self._load()

    def _load(self) -> dict[str, SourceConfig]:
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        return {
            item["source_id"]: SourceConfig.model_validate(item)
            for item in data.get("sources", [])
        }

    def list_sources(self, active_only: bool = False) -> list[SourceConfig]:
        sources = list(self._sources.values())
        if active_only:
            return [source for source in sources if source.is_active]
        return sources

    def get(self, source_id: str) -> SourceConfig:
        return self._sources[source_id]

    def upsert(self, source: SourceConfig) -> SourceConfig:
        self._sources[source.source_id] = source
        self._persist()
        return source

    def _persist(self) -> None:
        payload = {"sources": [source.model_dump(mode="json") for source in self._sources.values()]}
        self.path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

