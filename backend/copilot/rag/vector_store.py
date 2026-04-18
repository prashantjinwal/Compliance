import os
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .embeddings import get_embeddings
from .errors import (
    CopilotRateLimitError,
    extract_retry_seconds_from_exception,
    is_quota_error,
)

CHROMA_DIR = "chroma_db"


def create_vector_store(document_id, text):
    if not text or not text.strip():
        raise ValueError("No text could be extracted from the uploaded document.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(text)

    if not chunks:
        raise ValueError("No valid chunks could be created from the uploaded document.")

    embeddings = get_embeddings()

    try:
        vectordb = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory=os.path.join(CHROMA_DIR, str(document_id))
        )
    except Exception as exc:
        if is_quota_error(exc):
            raise CopilotRateLimitError(
                "Gemini API quota exceeded while creating embeddings. Please try again later.",
                retry_seconds=extract_retry_seconds_from_exception(exc),
            ) from exc
        raise

    return vectordb


def load_vector_store(document_id):
    embeddings = get_embeddings()

    try:
        return Chroma(
            persist_directory=os.path.join(CHROMA_DIR, str(document_id)),
            embedding_function=embeddings
        )
    except Exception as exc:
        if is_quota_error(exc):
            raise CopilotRateLimitError(
                "Gemini API quota exceeded while loading document embeddings. Please try again later.",
                retry_seconds=extract_retry_seconds_from_exception(exc),
            ) from exc
        raise
