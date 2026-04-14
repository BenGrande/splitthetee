"""Tests for render and settings endpoints."""

from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient


class TestRenderEndpoint:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    def test_render_empty_holes(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={"holes": [], "options": {}})
        assert response.status_code == 200
        data = response.json()
        assert "svg" in data
        assert data["svg"].startswith("<svg")

    def test_render_with_holes(self):
        holes = [
            {
                "ref": 1,
                "par": 4,
                "yardage": 400,
                "difficulty": 5.0,
                "handicap": None,
                "route_coords": [[36.0, -121.0], [36.001, -121.001]],
                "features": [
                    {"id": "1", "category": "fairway", "ref": None, "par": None, "name": None,
                     "coords": [[36.0, -121.0], [36.0005, -121.0005]]},
                ],
            }
        ]
        client = self._get_client()
        response = client.post("/api/v1/render", json={"holes": holes, "options": {}})
        assert response.status_code == 200
        data = response.json()
        assert "<svg" in data["svg"]

    def test_render_glass_mode(self):
        holes = [
            {
                "ref": 1,
                "par": 4,
                "yardage": 400,
                "difficulty": 5.0,
                "handicap": None,
                "route_coords": [[36.0, -121.0], [36.001, -121.001]],
                "features": [
                    {"id": "1", "category": "fairway", "ref": None, "par": None, "name": None,
                     "coords": [[36.0, -121.0], [36.0005, -121.0005]]},
                ],
            }
        ]
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": holes,
            "options": {"mode": "glass"},
        })
        assert response.status_code == 200
        data = response.json()
        assert "glassClip" in data["svg"]
        assert "#1a1a1a" in data["svg"]  # glass mode uses vinyl preview with solid dark bg

    def test_render_includes_zones(self):
        holes = [
            {
                "ref": 1,
                "par": 4,
                "yardage": 400,
                "difficulty": 5.0,
                "handicap": None,
                "route_coords": [[36.0, -121.0], [36.001, -121.001]],
                "features": [
                    {"id": "1", "category": "green", "ref": None, "par": None, "name": None,
                     "coords": [[36.001, -121.001], [36.0011, -121.0011]]},
                ],
            }
        ]
        client = self._get_client()
        response = client.post("/api/v1/render", json={"holes": holes, "options": {}})
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert len(data["zones"]) == 1
        assert data["zones"][0]["hole_ref"] == 1

    def test_render_scoring_preview_mode(self):
        holes = [
            {
                "ref": 1,
                "par": 4,
                "yardage": 400,
                "difficulty": 5.0,
                "handicap": None,
                "route_coords": [[36.0, -121.0], [36.001, -121.001]],
                "features": [
                    {"id": "1", "category": "green", "ref": None, "par": None, "name": None,
                     "coords": [[36.001, -121.001], [36.0011, -121.0011]]},
                ],
            }
        ]
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": holes,
            "options": {"mode": "scoring-preview"},
        })
        assert response.status_code == 200
        data = response.json()
        assert "scoring_preview" in data["svg"]


class TestRenderValidation:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    def test_render_missing_holes(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={"options": {}})
        assert response.status_code == 422

    def test_render_holes_not_array(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={"holes": "not_an_array"})
        assert response.status_code == 422

    def test_render_valid_returns_svg(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": [{
                "ref": 1, "par": 4, "yardage": 400, "difficulty": 5.0, "handicap": None,
                "route_coords": [[36.0, -121.0], [36.001, -121.001]],
                "features": [
                    {"id": "1", "category": "fairway", "ref": None, "par": None, "name": None,
                     "coords": [[36.0, -121.0], [36.0005, -121.0005]]},
                ],
            }],
            "options": {},
        })
        assert response.status_code == 200
        data = response.json()
        assert "svg" in data
        assert data["svg"].startswith("<svg")
        assert len(data["svg"]) > 0

    def test_cricut_missing_holes(self):
        client = self._get_client()
        response = client.post("/api/v1/render/cricut", json={"options": {}})
        assert response.status_code == 422

    def test_cricut_empty_holes(self):
        client = self._get_client()
        response = client.post("/api/v1/render/cricut", json={"holes": [], "options": {}})
        assert response.status_code == 400

    def test_cricut_returns_all_layers(self):
        client = self._get_client()
        holes = [{
            "ref": 1, "par": 4, "yardage": 400, "difficulty": 5.0, "handicap": 5,
            "route_coords": [[36.0, -121.0], [36.001, -121.001]],
            "features": [
                {"id": "f1", "category": "fairway", "ref": None, "par": None, "name": None,
                 "coords": [[36.0, -121.0], [36.0005, -121.0005]]},
                {"id": "g1", "category": "green", "ref": None, "par": None, "name": None,
                 "coords": [[36.001, -121.001], [36.0011, -121.0011], [36.0012, -121.001]]},
            ],
        }]
        response = client.post("/api/v1/render/cricut", json={"holes": holes, "options": {}})
        assert response.status_code == 200
        data = response.json()
        for key in ("white", "green", "tan", "blue", "guide"):
            assert key in data, f"Missing layer: {key}"
            assert isinstance(data[key], str), f"Layer {key} should be a string"
            assert len(data[key]) > 0, f"Layer {key} should not be empty"
            assert "<svg" in data[key], f"Layer {key} should contain SVG"


class TestCricutEndpoints:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    def _sample_holes(self):
        return [
            {
                "ref": 1, "par": 4, "yardage": 400, "difficulty": 5.0, "handicap": 5,
                "route_coords": [[36.0, -121.0], [36.001, -121.001]],
                "features": [
                    {"id": "f1", "category": "fairway", "ref": None, "par": None, "name": None,
                     "coords": [[36.0, -121.0], [36.0005, -121.0005]]},
                    {"id": "g1", "category": "green", "ref": None, "par": None, "name": None,
                     "coords": [[36.001, -121.001], [36.0011, -121.0011], [36.0012, -121.001]]},
                    {"id": "t1", "category": "tee", "ref": None, "par": None, "name": None,
                     "coords": [[36.0, -121.0], [36.0001, -121.0001], [36.0001, -121.0]]},
                    {"id": "b1", "category": "bunker", "ref": None, "par": None, "name": None,
                     "coords": [[36.0008, -121.0008], [36.0009, -121.0009], [36.0009, -121.0008]]},
                    {"id": "w1", "category": "water", "ref": None, "par": None, "name": None,
                     "coords": [[36.0006, -121.0006], [36.0007, -121.0007], [36.0007, -121.0006]]},
                ],
            }
        ]

    def test_cricut_blue_mode(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": self._sample_holes(),
            "options": {"mode": "cricut-blue"},
        })
        assert response.status_code == 200
        data = response.json()
        assert "<svg" in data["svg"]
        assert "#3b82f6" in data["svg"]

    def test_cricut_white_mode(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": self._sample_holes(),
            "options": {"mode": "cricut-white"},
        })
        assert response.status_code == 200
        data = response.json()
        assert 'fill="none"' in data["svg"]
        assert 'stroke="white"' in data["svg"]

    def test_cricut_green_mode(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": self._sample_holes(),
            "options": {"mode": "cricut-green"},
        })
        assert response.status_code == 200
        assert '#4ade80' in response.json()["svg"]

    def test_cricut_tan_mode(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": self._sample_holes(),
            "options": {"mode": "cricut-tan"},
        })
        assert response.status_code == 200
        assert "<svg" in response.json()["svg"]

    def test_cricut_all_mode(self):
        client = self._get_client()
        response = client.post("/api/v1/render", json={
            "holes": self._sample_holes(),
            "options": {"mode": "cricut-all"},
        })
        assert response.status_code == 200
        data = response.json()
        assert "white" in data
        assert "green" in data
        assert "tan" in data
        assert "blue" in data
        assert "guide" in data

    def test_cricut_dedicated_endpoint(self):
        client = self._get_client()
        response = client.post("/api/v1/render/cricut", json={
            "holes": self._sample_holes(),
            "options": {},
        })
        assert response.status_code == 200
        data = response.json()
        assert "white" in data
        assert "green" in data
        assert "tan" in data
        assert "blue" in data
        assert "guide" in data
        assert "<svg" in data["white"]
        assert "<svg" in data["blue"]


class TestCricutMultiGlass:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    def _sample_holes(self, count=4):
        holes = []
        for i in range(count):
            lat = 36.0 + i * 0.002
            holes.append({
                "ref": i + 1, "par": 4, "yardage": 400, "difficulty": 5.0, "handicap": i + 1,
                "route_coords": [[lat, -121.0], [lat + 0.001, -121.001]],
                "features": [
                    {"id": f"f{i}", "category": "fairway", "ref": None, "par": None, "name": None,
                     "coords": [[lat, -121.0], [lat + 0.0005, -121.0005]]},
                    {"id": f"g{i}", "category": "green", "ref": None, "par": None, "name": None,
                     "coords": [[lat + 0.001, -121.001], [lat + 0.0011, -121.0011], [lat + 0.0012, -121.001]]},
                ],
            })
        return holes

    def test_single_glass_response_shape(self):
        client = self._get_client()
        response = client.post("/api/v1/render/cricut", json={
            "holes": self._sample_holes(2),
            "options": {"glass_count": 1},
        })
        assert response.status_code == 200
        data = response.json()
        # Single glass: flat response with layer keys
        for key in ("white", "green", "tan", "blue", "guide"):
            assert key in data, f"Missing layer: {key}"
            assert "<svg" in data[key], f"Layer {key} missing SVG"
        assert "glasses" not in data

    def test_multi_glass_response_shape(self):
        client = self._get_client()
        response = client.post("/api/v1/render/cricut", json={
            "holes": self._sample_holes(4),
            "options": {"glass_count": 2},
        })
        assert response.status_code == 200
        data = response.json()
        # Multi-glass: wrapped in "glasses" array
        assert "glasses" in data
        assert len(data["glasses"]) == 2
        for gi, glass in enumerate(data["glasses"]):
            for key in ("white", "green", "tan", "blue", "guide"):
                assert key in glass, f"Glass {gi} missing layer: {key}"
                assert isinstance(glass[key], str), f"Glass {gi} layer {key} not a string"
                assert "<svg" in glass[key], f"Glass {gi} layer {key} missing SVG"

    def test_multi_glass_all_layers_non_empty(self):
        client = self._get_client()
        response = client.post("/api/v1/render/cricut", json={
            "holes": self._sample_holes(4),
            "options": {"glass_count": 2},
        })
        assert response.status_code == 200
        data = response.json()
        for glass in data["glasses"]:
            for key in ("white", "green", "tan", "blue", "guide"):
                assert len(glass[key]) > 50, f"Layer {key} suspiciously short"


class TestGlassTemplateEndpoint:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    def test_default_template(self):
        client = self._get_client()
        response = client.post("/api/v1/render/glass-template", json={})
        assert response.status_code == 200
        data = response.json()
        assert "template" in data
        assert "path" in data
        assert data["template"]["glass_height"] == 146

    def test_custom_template(self):
        client = self._get_client()
        response = client.post("/api/v1/render/glass-template", json={
            "glass_height": 100,
            "top_radius": 40,
            "bottom_radius": 25,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["template"]["glass_height"] == 100


class TestSettingsEndpoints:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    @patch("app.api.v1.settings.design_settings")
    def test_save_settings(self, mock_ds):
        mock_collection = AsyncMock()
        mock_collection.insert_one.return_value = MagicMock(inserted_id="test_id")
        mock_ds.return_value = mock_collection

        client = self._get_client()
        response = client.post("/api/v1/settings", json={
            "course_name": "Pebble Beach",
            "settings": {"color": "blue"},
        })
        assert response.status_code == 200
        assert response.json()["ok"] is True
        assert "id" in response.json()

    def test_save_settings_no_name(self):
        client = self._get_client()
        response = client.post("/api/v1/settings", json={"settings": {}})
        assert response.status_code == 400

    @patch("app.api.v1.settings.design_settings")
    def test_list_settings(self, mock_ds):
        mock_collection = MagicMock()

        class MockCursor:
            def __init__(self):
                self.items = [
                    {"_id": "test_1", "course_name": "Pebble", "saved_at": "2025-01-01"},
                ]
            def sort(self, *args, **kwargs):
                return self
            def __aiter__(self):
                return self
            async def __anext__(self):
                if self.items:
                    return self.items.pop(0)
                raise StopAsyncIteration

        mock_collection.find.return_value = MockCursor()
        mock_ds.return_value = mock_collection

        client = self._get_client()
        response = client.get("/api/v1/settings")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["course_name"] == "Pebble"

    @patch("app.api.v1.settings.design_settings")
    def test_get_setting(self, mock_ds):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = {
            "_id": "test_1",
            "course_name": "Pebble",
            "settings": {"color": "green"},
        }
        mock_ds.return_value = mock_collection

        client = self._get_client()
        response = client.get("/api/v1/settings/test_1")
        assert response.status_code == 200
        assert response.json()["course_name"] == "Pebble"

    @patch("app.api.v1.settings.design_settings")
    def test_get_setting_not_found(self, mock_ds):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = None
        mock_ds.return_value = mock_collection

        client = self._get_client()
        response = client.get("/api/v1/settings/nonexistent")
        assert response.status_code == 404
