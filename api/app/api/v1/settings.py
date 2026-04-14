"""Save/load glass design settings."""

import re
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.db.mongo import design_settings

router = APIRouter()


def _safe_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


@router.post("/settings")
async def save_settings(data: dict):
    """Save glass design configuration."""
    course_name = data.get("course_name") or data.get("courseName")
    if not course_name:
        raise HTTPException(status_code=400, detail="course_name required")

    settings_data = data.get("settings", data)
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat().replace(":", "-").replace(".", "-")
    doc_id = f"{_safe_key(course_name)}_{timestamp}"

    collection = design_settings()
    await collection.insert_one({
        "_id": doc_id,
        "course_name": course_name,
        "settings": settings_data,
        "saved_at": now.isoformat(),
        "created_at": now,
    })

    return {"ok": True, "id": doc_id}


@router.get("/settings")
async def list_settings():
    """List saved design configurations."""
    collection = design_settings()
    cursor = collection.find({}, {"_id": 1, "course_name": 1, "saved_at": 1}).sort("created_at", -1)

    results = []
    async for doc in cursor:
        results.append({
            "id": str(doc["_id"]),
            "course_name": doc.get("course_name", ""),
            "saved_at": doc.get("saved_at", ""),
        })
    return results


@router.get("/settings/{setting_id}")
async def get_setting(setting_id: str):
    """Load a specific design configuration."""
    collection = design_settings()
    doc = await collection.find_one({"_id": setting_id})
    if not doc:
        raise HTTPException(status_code=404, detail="not found")

    doc["id"] = str(doc.pop("_id"))
    return doc
