"""Per-hole bundled data — associates OSM features with holes."""
from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.db.mongo import bundle_cache, search_cache
from app.services.golf.holes import associate_features
from app.services.golf.osm import fetch_course_map
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/course-holes")
async def get_course_holes(lat: float, lng: float, courseId: str | None = None):
    """Get per-hole feature bundles for a course."""
    collection = bundle_cache()
    cache_key = f"{lat}_{lng}"

    # Check cache
    cached = await collection.find_one({"cache_key": cache_key})
    if cached:
        return {
            "holes": cached["holes"],
            "course_name": cached.get("course_name"),
            "center": cached["center"],
        }

    try:
        # Fetch map data
        map_data = await fetch_course_map(lat, lng)

        # Fetch course data from Golf API if courseId provided
        course_data = None
        if courseId:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(
                        f"{settings.GOLF_API_BASE}/courses/{courseId}",
                        headers={"Authorization": f"Key {settings.GOLF_API_KEY}"},
                    )
                    if response.is_success:
                        course_data = response.json()
                        if "course" in course_data:
                            course_data = course_data["course"]
            except Exception as exc:
                logger.warning("Could not fetch course detail: %s", exc)

        # If no course data, try to find from search cache by lat/lng proximity
        if not course_data:
            sc = search_cache()
            async for doc in sc.find():
                for course in doc.get("data", []):
                    loc = course.get("location", {})
                    if not loc:
                        continue
                    c_lat = loc.get("latitude", 0)
                    c_lng = loc.get("longitude", 0)
                    if abs(c_lat - lat) < 0.001 and abs(c_lng - lng) < 0.001:
                        course_data = course
                        break
                if course_data:
                    break

        # Associate features with holes
        holes = associate_features(map_data["features"], course_data)
        course_name = None
        if course_data:
            course_name = course_data.get("course_name") or course_data.get("club_name")

        from app.services.font_hints import get_font_hint
        font_hint = get_font_hint(course_name) if course_name else None

        result = {
            "holes": holes,
            "course_name": course_name,
            "center": map_data["center"],
            "font_hint": font_hint,
        }

        # Cache if we got holes
        if holes:
            await collection.update_one(
                {"cache_key": cache_key},
                {"$set": {
                    "cache_key": cache_key,
                    "holes": holes,
                    "course_name": course_name,
                    "center": map_data["center"],
                    "cached_at": datetime.now(timezone.utc),
                }},
                upsert=True,
            )

        return result
    except Exception as exc:
        logger.error("Bundle error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to build course hole data")
