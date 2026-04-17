from .vector_store import load_vector_store


def retrieve_chunks(document_id, query, k=5):
    vectordb = load_vector_store(document_id)

    docs = vectordb.similarity_search(query, k=k)

    return [doc.page_content for doc in docs]
