"""Course map — fetches OSM data via Overpass API with MongoDB caching."""

from fastapi import APIRouter, HTTPException

from app.services.golf.osm import fetch_course_map

router = APIRouter()


@router.get("/course-map")
async def get_course_map(lat: float, lng: float, radius: int = 2000):
    """Fetch golf course features from OpenStreetMap."""
    try:
        result = await fetch_course_map(lat, lng, radius)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch course map data: {exc}")
