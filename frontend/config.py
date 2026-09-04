import os
from urllib.parse import urlparse


APP_NAME = "OMR-Scanify"
DEFAULT_API_HOST = "127.0.0.1"
DEFAULT_API_PORT = 8080
DEFAULT_API_SCHEME = "http"
API_PREFIX = "/api/v1"


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def api_url():
    configured_url = os.environ.get("OMR_SCANIFY_API_URL")
    if configured_url:
        parsed = urlparse(configured_url)
        if parsed.scheme and parsed.netloc:
            return configured_url.rstrip("/")

    host = os.environ.get("OMR_SCANIFY_HOST", DEFAULT_API_HOST)
    port = _positive_int(os.environ.get("OMR_SCANIFY_PORT"), DEFAULT_API_PORT)
    return f"{DEFAULT_API_SCHEME}://{host}:{port}{API_PREFIX}"


API_URL = api_url()