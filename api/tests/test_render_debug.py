"""Smoke test for the /render/debug diagnostic endpoint."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def _get_client():
    from app.main import app
    return TestClient(app)


@patch("app.api.v1.render.fetch_course_map", new_callable=AsyncMock)
@patch("app.api.v1.render.get_course_holes", new_callable=AsyncMock)
def test_debug_returns_course_holes_layout_and_stats(mock_holes, mock_osm):
    mock_holes.return_value = {
        "course_name": "Augusta National",
        "center": [33.5021, -82.0226],
        "holes": [
            {
                "ref": i,
                "number": i,
                "par": 4,
                "yardage": 400,
                "handicap": i,
                "features": [{"category": "fairway", "coords": []}],
            }
            for i in range(1, 19)
        ],
    }
    mock_osm.return_value = {
        "features": [
            {"category": "fairway"},
            {"category": "green"},
            {"category": "bunker"},
        ],
        "center": [33.5021, -82.0226],
    }

    resp = _get_client().get(
        "/api/v1/render/debug?courseId=7118&lat=33.5021&lng=-82.0226&glass_count=2",
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["course"]["course_name"] == "Augusta National"
    assert data["course"]["hole_count"] == 18
    assert len(data["holes"]) == 18
    assert data["split"]["glass_count"] == 2
    assert data["split"]["selected_count"] == 9
    assert data["hole_stats_keys"] == list(range(1, 10))
    assert data["osm_feature_count"] == 3
    assert data["osm_categories"] == {"fairway": 1, "green": 1, "bunker": 1}
    assert len(data["layout_summary"]) == 9
    assert data["layout_summary"][0]["ref"] == 1


@patch("app.api.v1.render.get_course_holes", new_callable=AsyncMock)
def test_debug_without_lat_lng_skips_osm(mock_holes):
    mock_holes.return_value = {
        "course_name": "Test",
        "center": None,
        "holes": [
            {"ref": 1, "number": 1, "par": 4, "yardage": 400, "handicap": 1, "features": []},
        ],
    }

    resp = _get_client().get("/api/v1/render/debug?courseId=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["osm_feature_count"] == 0
    assert data["osm_error"] is None
    assert data["hole_stats_keys"] == [1]
