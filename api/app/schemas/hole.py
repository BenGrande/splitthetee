"""Hole bundle Pydantic schemas."""

from pydantic import BaseModel

from app.schemas.map import MapFeature


class HoleBundle(BaseModel):
    ref: int
    par: int
    yardage: int
    handicap: int
    difficulty: float
    route_coords: list[list[float]]
    features: list[MapFeature]


class CourseHolesResponse(BaseModel):
    holes: list[HoleBundle]
    center: list[float]
    course_name: str
