"""Tests for course-map and course-holes endpoints."""

from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient


class TestCourseMapEndpoint:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    @patch("app.api.v1.course_map.fetch_course_map", new_callable=AsyncMock)
    def test_returns_features(self, mock_fetch):
        mock_fetch.return_value = {
            "features": [{"id": "1", "category": "fairway", "coords": [[36.0, -121.0]]}],
            "center": [36.0, -121.0],
        }
        client = self._get_client()
        response = client.get("/api/v1/course-map?lat=36.0&lng=-121.0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]) == 1
        mock_fetch.assert_called_once_with(36.0, -121.0, 2000)

    @patch("app.api.v1.course_map.fetch_course_map", new_callable=AsyncMock)
    def test_custom_radius(self, mock_fetch):
        mock_fetch.return_value = {"features": [], "center": [36.0, -121.0]}
        client = self._get_client()
        response = client.get("/api/v1/course-map?lat=36.0&lng=-121.0&radius=1500")
        assert response.status_code == 200
        mock_fetch.assert_called_once_with(36.0, -121.0, 1500)

    def test_missing_lat(self):
        client = self._get_client()
        response = client.get("/api/v1/course-map?lng=-121.0")
        assert response.status_code == 422


class TestCourseHolesEndpoint:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    @patch("app.api.v1.holes.bundle_cache")
    @patch("app.api.v1.holes.fetch_course_map", new_callable=AsyncMock)
    def test_returns_holes(self, mock_fetch, mock_bc):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = None
        mock_bc.return_value = mock_collection

        mock_fetch.return_value = {"features": [], "center": [36.0, -121.0]}

        with patch("app.api.v1.holes.search_cache") as mock_sc:
            mock_sc_collection = MagicMock()
            mock_sc_collection.find.return_value = AsyncIterator([])
            mock_sc.return_value = mock_sc_collection

            client = self._get_client()
            response = client.get("/api/v1/course-holes?lat=36.0&lng=-121.0")

        assert response.status_code == 200
        data = response.json()
        assert "holes" in data
        assert "center" in data

    @patch("app.api.v1.holes.bundle_cache")
    def test_cache_hit(self, mock_bc):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = {
            "cache_key": "36.0_-121.0",
            "holes": [{"ref": 1}],
            "course_name": "Test Course",
            "center": [36.0, -121.0],
        }
        mock_bc.return_value = mock_collection

        client = self._get_client()
        response = client.get("/api/v1/course-holes?lat=36.0&lng=-121.0")
        assert response.status_code == 200
        data = response.json()
        assert data["course_name"] == "Test Course"

    def test_missing_params(self):
        client = self._get_client()
        response = client.get("/api/v1/course-holes")
        assert response.status_code == 422


class AsyncIterator:
    """Helper to mock async iteration over MongoDB cursor."""
    def __init__(self, items):
        self.items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration
