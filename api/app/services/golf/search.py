"""Golf course search service — proxy to Golf Course API with MongoDB caching."""

import re
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.db.mongo import search_cache


def _sanitize_query(q: str) -> str:
    """Normalize and sanitize the search query for cache keying."""
    return re.sub(r"[^a-z0-9 ]", "", q.strip().lower()).strip()


async def search_courses(query: str) -> list[dict]:
    """Search for golf courses, with MongoDB caching.

    Returns a list of course dicts from the Golf Course API.
    """
    if not query or not query.strip():
        return []

    sanitized = _sanitize_query(query)
    if not sanitized:
        return []

    collection = search_cache()

    # Check cache
    cached = await collection.find_one({"query": sanitized})
    if cached:
        return cached["data"]

    # Call Golf Course API
    url = f"{settings.GOLF_API_BASE}/search"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={"search_query": query},
            headers={"Authorization": f"Key {settings.GOLF_API_KEY}"},
            timeout=15.0,
        )
        response.raise_for_status()

    data = response.json()
    courses = data.get("courses", [])

    # Cache the result
    await collection.update_one(
        {"query": sanitized},
        {"$set": {"query": sanitized, "data": courses, "cached_at": datetime.now(timezone.utc)}},
        upsert=True,
    )

    return courses
