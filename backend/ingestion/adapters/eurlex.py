from ingestion.adapters.generic_document_feed import GenericDocumentFeedAdapter


class EurLexAdapter(GenericDocumentFeedAdapter):
    """EUR-Lex adapter placeholder.

    TODO: Configure CELEX queries or EUR-Lex webservice credentials when available.
    The generic document fallback keeps the pipeline usable until exact official
    query mappings are finalized.
    """

