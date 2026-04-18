from pathlib import Path

from decouple import AutoConfig


class CopilotConfigurationError(RuntimeError):
    """Raised when required AI configuration is missing."""


_backend_dir = Path(__file__).resolve().parents[2]
_config = AutoConfig(search_path=str(_backend_dir))


def get_gemini_api_key():
    api_key = _config("GEMINI_API_KEY", default="").strip()

    if not api_key:
        raise CopilotConfigurationError(
            "Backend AI configuration is missing. Please set GEMINI_API_KEY in backend/.env or as an environment variable."
        )

    return api_key
