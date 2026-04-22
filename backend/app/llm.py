import hashlib
import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class LLMUnavailable(Exception):
    """Raised when the configured LLM backend cannot serve a request."""


@dataclass
class InsightResult:
    text: str
    llm_model: str
    cached: bool


def generate_insight(
    *,
    prompt: str,
    subject: str,
    cache_ttl: int = 24 * 3600,
) -> InsightResult:
    """Generate an LLM insight with content-hash caching.

    ``subject`` is a short string that scopes the cache key
    (e.g. ``"model:7"`` or ``"compare:3:9"``). The prompt's hash is
    included in the key so edits to the prompt template invalidate
    stale entries automatically.
    """
    if not settings.OLLAMA_URL:
        raise LLMUnavailable("OLLAMA_URL is not configured")

    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    key = f"insight:{subject}:{prompt_hash}"

    cached_entry = cache.get(key)
    if cached_entry:
        return InsightResult(
            text=cached_entry["text"],
            llm_model=cached_entry["llm_model"],
            cached=True,
        )

    text = _call_ollama(prompt)
    cache.set(
        key,
        {"text": text, "llm_model": settings.OLLAMA_MODEL},
        timeout=cache_ttl,
    )
    return InsightResult(
        text=text, llm_model=settings.OLLAMA_MODEL, cached=False
    )


def _call_ollama(prompt: str) -> str:
    url = f"{settings.OLLAMA_URL}/api/generate"
    payload = json.dumps(
        {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(
            request, timeout=settings.OLLAMA_TIMEOUT_SECONDS
        ) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Ollama call failed: %s", exc)
        raise LLMUnavailable(f"Ollama request failed: {exc}") from exc

    text = (body.get("response") or "").strip()
    if not text:
        raise LLMUnavailable("Ollama returned an empty response")
    return text
