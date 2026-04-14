"""QR code generation for glass sets."""

from fastapi import APIRouter, HTTPException

from app.schemas.game import GlassSetCreate
from app.services.game import create_glass_set, get_glass_set

router = APIRouter()


@router.post("/glass-sets")
async def create_glass_set_endpoint(data: GlassSetCreate):
    """Create a new glass set with unique QR codes."""
    result = await create_glass_set(data.model_dump())
    return result


@router.get("/glass-sets/{glass_set_id}")
async def get_glass_set_endpoint(glass_set_id: str):
    """Get glass set details including QR codes."""
    result = await get_glass_set(glass_set_id)
    if not result:
        raise HTTPException(status_code=404, detail="Glass set not found")
    return result
