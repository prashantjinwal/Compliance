#turn text into dense vector 

from sentence_transformers import SentenceTranformer 

_model = None

def get_embedder() -> SentenceTranformer:
    global _model
    if _model is None:
        _model = SentenceTranformer("BAAI/bge-large-en-v1.5")
    return _model

def encode(text: str) -> list:
    return get_embedder().encode(text, normalize_embeddings= True).tolist()

def encode_batch(texts: list) -> list:
    return get_embedder().encode(
        texts, normalize_embeddings=True, batch_size=16
    ).tolist()



