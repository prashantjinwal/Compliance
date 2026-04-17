from .llm import get_llm


def summarize_document(text):
    llm = get_llm()

    prompt = f"""
    Summarize this document in simple terms:

    {text[:4000]}
    """

    return llm.predict(prompt)


def chat_with_doc(vectorstore, query):
    retriever = vectorstore.as_retriever()

    docs = retriever.get_relevant_documents(query)

    context = " ".join([doc.page_content for doc in docs])

    llm = get_llm()

    prompt = f"""
    Answer the question based only on the context below:

    Context:
    {context}

    Question:
    {query}
    """

    return llm.predict(prompt)
