from __future__ import annotations

import re

from ingestion.models import NormalizedRegulation, RagDocument
from rag.metadata_mapper import metadata_for_regulation


def chunk_regulation(regulation: NormalizedRegulation, max_chars: int = 2400, overlap_chars: int = 250) -> list[RagDocument]:
    sections = _section_boundaries(regulation.full_text)
    chunks: list[RagDocument] = []
    base_metadata = metadata_for_regulation(regulation)

    if sections:
        for idx, (title, start) in enumerate(sections):
            end = sections[idx + 1][1] if idx + 1 < len(sections) else len(regulation.full_text)
            section = regulation.full_text[start:end].strip()
            chunks.extend(_split_text(regulation, section, title, base_metadata, len(chunks), max_chars, overlap_chars))
    else:
        chunks.extend(_split_text(regulation, regulation.full_text, "Full text", base_metadata, 0, max_chars, overlap_chars))

    return chunks


def _split_text(
    regulation: NormalizedRegulation,
    text: str,
    title: str,
    base_metadata: dict,
    start_index: int,
    max_chars: int,
    overlap_chars: int,
) -> list[RagDocument]:
    docs = []
    stride = max(1, max_chars - overlap_chars)
    for offset in range(0, max(len(text), 1), stride):
        piece = text[offset: offset + max_chars].strip()
        if not piece:
            continue
        chunk_index = start_index + len(docs)
        metadata = dict(base_metadata)
        metadata.update({"section_title": title, "chunk_index": chunk_index})
        docs.append(
            RagDocument(
                document_id=f"{regulation.regulation_id}:{regulation.version_id}:{chunk_index}",
                text=piece,
                metadata=metadata,
            )
        )
        if offset + max_chars >= len(text):
            break
    return docs


def _section_boundaries(text: str) -> list[tuple[str, int]]:
    patterns = [
        r"(Article\s+\d+[\.\s][^\n]{5,80})",
        r"(Section\s+\d+[\.\d]*\s+[^\n]{5,80})",
        r"(Clause\s+\d+[\.\d]*\s+[^\n]{5,80})",
        r"(Part\s+\d+[\.\s][^\n]{5,80})",
    ]
    return [(match.group(), match.start()) for match in re.finditer("|".join(patterns), text)]

