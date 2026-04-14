"""Tests for Pydantic schema models."""

from app.schemas.course import CourseSearchResult, TeeSet, TeeHole, HoleInfo
from app.schemas.map import MapFeature, CourseMapResponse
from app.schemas.hole import HoleBundle, CourseHolesResponse
from app.schemas.settings import SaveSettingsRequest, SettingsListItem


class TestCourseSchemas:
    def test_tee_hole(self):
        th = TeeHole(number=1, par=4, yardage=350, handicap=5)
        assert th.number == 1
        assert th.par == 4

    def test_tee_set(self):
        ts = TeeSet(
            tee_name="Blue",
            gender="male",
            par=72,
            rating=71.5,
            slope=130,
            yardage=6500,
            holes=[TeeHole(number=1, par=4, yardage=350, handicap=5)],
        )
        assert ts.tee_name == "Blue"
        assert len(ts.holes) == 1

    def test_hole_info(self):
        hi = HoleInfo(number=3, par=3, yardage=180, handicap=15)
        assert hi.number == 3

    def test_course_search_result(self):
        c = CourseSearchResult(
            id=123,
            name="Pebble Beach",
            club_name="Pebble Beach Resorts",
            location={"city": "Pebble Beach", "state": "CA", "country": "US"},
            lat=36.5668,
            lng=-121.9499,
        )
        assert c.name == "Pebble Beach"
        assert c.tees == []
        assert c.holes == []

    def test_course_search_result_with_tees_and_holes(self):
        c = CourseSearchResult(
            id=123,
            name="Test Course",
            club_name="Test Club",
            location={"city": "Test"},
            lat=0.0,
            lng=0.0,
            tees=[
                TeeSet(
                    tee_name="White",
                    gender="male",
                    par=72,
                    rating=70.0,
                    slope=125,
                    yardage=6200,
                    holes=[],
                )
            ],
            holes=[HoleInfo(number=1, par=4, yardage=400, handicap=1)],
        )
        assert len(c.tees) == 1
        assert len(c.holes) == 1


class TestMapSchemas:
    def test_map_feature(self):
        f = MapFeature(
            id="way/123",
            category="fairway",
            coords=[[1.0, 2.0], [3.0, 4.0]],
        )
        assert f.id == "way/123"
        assert f.ref is None
        assert f.par is None

    def test_map_feature_with_optionals(self):
        f = MapFeature(
            id="way/456",
            category="green",
            ref="1",
            par=4,
            name="Hole 1 Green",
            coords=[[1.0, 2.0]],
        )
        assert f.ref == "1"
        assert f.par == 4

    def test_course_map_response(self):
        r = CourseMapResponse(
            features=[
                MapFeature(id="1", category="tee", coords=[[0.0, 0.0]])
            ],
            center=[36.0, -121.0],
        )
        assert len(r.features) == 1
        assert r.center == [36.0, -121.0]


class TestHoleSchemas:
    def test_hole_bundle(self):
        b = HoleBundle(
            ref=1,
            par=4,
            yardage=400,
            handicap=3,
            difficulty=0.75,
            route_coords=[[1.0, 2.0], [3.0, 4.0]],
            features=[
                MapFeature(id="1", category="fairway", coords=[[0.0, 0.0]])
            ],
        )
        assert b.ref == 1
        assert b.difficulty == 0.75

    def test_course_holes_response(self):
        r = CourseHolesResponse(
            holes=[],
            center=[36.0, -121.0],
            course_name="Test Course",
        )
        assert r.course_name == "Test Course"


class TestSettingsSchemas:
    def test_save_settings_request(self):
        r = SaveSettingsRequest(
            course_name="Pebble Beach",
            settings={"color": "blue", "layout": "grid"},
        )
        assert r.course_name == "Pebble Beach"
        assert r.settings["color"] == "blue"

    def test_settings_list_item(self):
        item = SettingsListItem(
            filename="pebble.json",
            course_name="Pebble Beach",
            saved_at="2025-01-01T00:00:00Z",
        )
        assert item.filename == "pebble.json"
