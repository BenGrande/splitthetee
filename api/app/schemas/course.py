"""Course-related Pydantic schemas."""

from pydantic import BaseModel


class TeeHole(BaseModel):
    number: int
    par: int
    yardage: int
    handicap: int


class TeeSet(BaseModel):
    tee_name: str
    gender: str
    par: int
    rating: float
    slope: int
    yardage: int
    holes: list[TeeHole]


class HoleInfo(BaseModel):
    number: int
    par: int
    yardage: int
    handicap: int


class CourseSearchResult(BaseModel):
    id: int
    name: str
    club_name: str
    location: dict  # city, state, country
    lat: float
    lng: float
    tees: list[TeeSet] = []
    holes: list[HoleInfo] = []
