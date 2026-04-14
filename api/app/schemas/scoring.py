"""Scoring zone Pydantic schemas."""

from pydantic import BaseModel


class ScoringZone(BaseModel):
    score: int  # -1, 0, 1, 2, 3, 4, 5
    y_top: float
    y_bottom: float
    label: str
    position: str  # "above" | "green" | "below"


class ScoringZoneResult(BaseModel):
    hole_ref: int
    zones: list[ScoringZone]
    green_y_top: float
    green_y_bottom: float
