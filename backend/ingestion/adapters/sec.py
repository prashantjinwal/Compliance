from ingestion.adapters.generic_official_api import GenericOfficialApiAdapter


class SecAdapter(GenericOfficialApiAdapter):
    """SEC adapter placeholder.

    TODO: Route to specific SEC endpoints and provide a compliant User-Agent in
    source_registry.yaml before production polling.
    """

