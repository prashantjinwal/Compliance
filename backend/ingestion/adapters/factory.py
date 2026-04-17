from __future__ import annotations

from ingestion.adapters.base import SourceAdapter
from ingestion.adapters.eurlex import EurLexAdapter
from ingestion.adapters.fca import FcaAdapter
from ingestion.adapters.generic_document_feed import GenericDocumentFeedAdapter
from ingestion.adapters.generic_official_api import GenericOfficialApiAdapter
from ingestion.adapters.sec import SecAdapter
from ingestion.models import SourceConfig


ADAPTERS: dict[str, type[SourceAdapter]] = {
    "eurlex": EurLexAdapter,
    "sec": SecAdapter,
    "fca": FcaAdapter,
    "generic_official_api": GenericOfficialApiAdapter,
    "generic_document_feed": GenericDocumentFeedAdapter,
}


def build_adapter(source: SourceConfig) -> SourceAdapter:
    adapter_cls = ADAPTERS.get(source.parser_type, GenericOfficialApiAdapter)
    return adapter_cls(source)

