"""OSM/map feature Pydantic schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MapFeature(BaseModel):
    id: str
    category: str  # fairway, green, tee, bunker, rough, hole, water, path, course_boundary
    ref: Optional[str] = None
    par: Optional[int] = None
    name: Optional[str] = None
    coords: list[list[float]]


class CourseMapResponse(BaseModel):
    features: list[MapFeature]
    center: list[float]
