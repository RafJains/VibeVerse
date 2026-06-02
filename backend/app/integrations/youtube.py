import httpx

from app.core.config import settings


class YouTubeIntegrationError(Exception):
    """Base error for YouTube integration failures."""


class YouTubeMissingAPIKeyError(YouTubeIntegrationError):
    """Raised when YOUTUBE_API_KEY is not configured."""


def _require_api_key() -> str:
    if not settings.youtube_api_key:
        raise YouTubeMissingAPIKeyError("YOUTUBE_API_KEY is not configured.")
    return settings.youtube_api_key


def search_entity_videos(query: str, max_results: int = 5) -> dict:
    api_key = _require_api_key()
    url = f"{settings.youtube_base_url.rstrip('/')}/search"

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url,
                params={
                    "key": api_key,
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": max_results,
                },
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        raise YouTubeIntegrationError(
            f"YouTube API request failed with status {status_code}."
        ) from exc
    except httpx.HTTPError as exc:
        raise YouTubeIntegrationError("YouTube API request failed.") from exc
    except ValueError as exc:
        raise YouTubeIntegrationError("YouTube API returned invalid JSON.") from exc
