"""Golf course search — proxies to Golf Course API with MongoDB caching."""

from fastapi import APIRouter, HTTPException
import httpx

from app.services.golf.search import search_courses

router = APIRouter()


@router.get("/search")
async def search(q: str = ""):
    """Search for golf courses by name/location."""
    if not q or not q.strip():
        return {"courses": []}

    try:
        courses = await search_courses(q)
        return {"courses": courses}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Golf API returned {exc.response.status_code}",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach Golf API: {exc}",
        )
