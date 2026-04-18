import re


class CopilotRateLimitError(RuntimeError):
    """Raised when the Gemini API rejects a request due to quota or rate limits."""

    def __init__(self, message=None, retry_seconds=None):
        self.error_code = "QUOTA_EXCEEDED"
        self.retry_seconds = retry_seconds
        super().__init__(
            message
            or "Gemini API quota exceeded. Please try again later or upgrade the API plan."
        )


def extract_retry_seconds_from_value(value):
    if value is None:
        return None

    if isinstance(value, dict):
        for key in ("retry_delay", "retryDelay"):
            delay = value.get(key)
            seconds = extract_retry_seconds_from_value(delay)
            if seconds is not None:
                return seconds

        seconds_value = value.get("seconds")
        if isinstance(seconds_value, (int, float)):
            return max(1, int(seconds_value))

        for nested_value in value.values():
            seconds = extract_retry_seconds_from_value(nested_value)
            if seconds is not None:
                return seconds

        return None

    if isinstance(value, list):
        for item in value:
            seconds = extract_retry_seconds_from_value(item)
            if seconds is not None:
                return seconds

        return None

    if isinstance(value, str):
        patterns = [
            r"retry_delay\s*\{\s*seconds:\s*(\d+)",
            r'"retryDelay"\s*:\s*"(\d+)s"',
            r'"seconds"\s*:\s*(\d+)',
            r"retry in about (\d+) seconds",
        ]

        for pattern in patterns:
            match = re.search(pattern, value, flags=re.IGNORECASE)
            if match:
                return max(1, int(match.group(1)))

    return None


def extract_retry_seconds_from_exception(exc):
    cause = getattr(exc, "__cause__", None)

    for value in (
        getattr(cause, "details", None),
        getattr(cause, "message", None),
        str(cause) if cause else None,
        str(exc),
    ):
        seconds = extract_retry_seconds_from_value(value)
        if seconds is not None:
            return seconds

    return None


def is_quota_error(exc):
    cause = getattr(exc, "__cause__", None)
    status = str(getattr(cause, "status", "") or "").upper()
    code = getattr(cause, "code", None)
    message = " ".join(
        part
        for part in (
            getattr(cause, "message", None),
            str(getattr(cause, "details", "") or ""),
            str(exc),
        )
        if part
    ).upper()

    if code == 429:
        return True

    if status == "RESOURCE_EXHAUSTED":
        return True

    return "RESOURCE_EXHAUSTED" in message or "429" in message

