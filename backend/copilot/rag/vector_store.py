import os
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .embeddings import get_embeddings

CHROMA_DIR = "chroma_db"


def create_vector_store(document_id, text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(text)

    embeddings = get_embeddings()

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=os.path.join(CHROMA_DIR, str(document_id))
    )

    vectordb.persist()

    return vectordb


def load_vector_store(document_id):
    embeddings = get_embeddings()

    return Chroma(
        persist_directory=os.path.join(CHROMA_DIR, str(document_id)),
        embedding_function=embeddings
    )
