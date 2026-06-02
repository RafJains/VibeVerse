import httpx

from app.core.config import settings


class TMDbIntegrationError(Exception):
    """Base error for TMDb integration failures."""


class TMDbMissingAPIKeyError(TMDbIntegrationError):
    """Raised when TMDB_API_KEY is not configured."""


def _require_api_key() -> str:
    if not settings.tmdb_api_key:
        raise TMDbMissingAPIKeyError("TMDB_API_KEY is not configured.")
    return settings.tmdb_api_key


def _request(path: str, params: dict[str, object] | None = None) -> dict:
    api_key = _require_api_key()
    url = f"{settings.tmdb_base_url.rstrip('/')}/{path.lstrip('/')}"
    request_params = {"api_key": api_key, **(params or {})}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=request_params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        raise TMDbIntegrationError(
            f"TMDb API request failed with status {status_code}."
        ) from exc
    except httpx.HTTPError as exc:
        raise TMDbIntegrationError("TMDb API request failed.") from exc
    except ValueError as exc:
        raise TMDbIntegrationError("TMDb API returned invalid JSON.") from exc


def fetch_movie(tmdb_id: int) -> dict:
    return _request(f"/movie/{tmdb_id}", {"append_to_response": "videos"})


def fetch_tv_series(tmdb_id: int) -> dict:
    return _request(f"/tv/{tmdb_id}", {"append_to_response": "videos"})


def fetch_person(tmdb_id: int) -> dict:
    return _request(f"/person/{tmdb_id}")


def search_multi(query: str) -> dict:
    return _request("/search/multi", {"query": query})
