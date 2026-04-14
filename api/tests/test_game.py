"""Tests for game service, schemas, and endpoints."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.schemas.game import (
    GlassSetCreate, QRCode, GlassSetResponse,
    JoinGameRequest, JoinGameResponse,
    ScoreSubmit, LeaderboardEntry, LeaderboardResponse,
)
from app.services.game import (
    _generate_id,
    generate_qr_svg,
    create_glass_set,
    get_glass_set,
    find_or_create_session,
    add_player,
    submit_score,
    get_leaderboard,
    get_player_scores,
)


class TestGenerateId:
    def test_default_length(self):
        id_ = _generate_id()
        assert len(id_) == 8

    def test_custom_length(self):
        id_ = _generate_id(12)
        assert len(id_) == 12

    def test_alphanumeric(self):
        id_ = _generate_id(100)
        assert id_.isalnum()

    def test_unique(self):
        ids = {_generate_id() for _ in range(100)}
        assert len(ids) == 100  # all unique


class TestGenerateQrSvg:
    def test_produces_svg(self):
        svg = generate_qr_svg("https://example.com/play/abc123")
        assert "<svg" in svg.lower() or "<?xml" in svg.lower()

    def test_different_urls_produce_different_svgs(self):
        svg1 = generate_qr_svg("https://example.com/a")
        svg2 = generate_qr_svg("https://example.com/b")
        assert svg1 != svg2


class TestGameSchemas:
    def test_glass_set_create(self):
        data = GlassSetCreate(course_id="123", course_name="Pebble Beach")
        assert data.glass_count == 3
        assert data.holes_per_glass == 6

    def test_qr_code(self):
        qr = QRCode(glass_number=1, url="https://example.com", qr_svg="<svg/>")
        assert qr.glass_number == 1

    def test_glass_set_response(self):
        r = GlassSetResponse(
            id="abc", course_id="123", course_name="Test",
            glass_count=3, holes_per_glass=6, created_at="2025-01-01",
            qr_codes=[QRCode(glass_number=1, url="url", qr_svg="<svg/>")],
        )
        assert r.id == "abc"

    def test_join_game_request(self):
        r = JoinGameRequest(glass_set_id="abc", player_name="Alice")
        assert r.player_name == "Alice"

    def test_score_submit_valid(self):
        s = ScoreSubmit(player_id="p1", hole_number=1, glass_number=1, score=3)
        assert s.score == 3

    def test_score_submit_min(self):
        s = ScoreSubmit(player_id="p1", hole_number=1, glass_number=1, score=-1)
        assert s.score == -1

    def test_score_submit_max(self):
        s = ScoreSubmit(player_id="p1", hole_number=1, glass_number=1, score=8)
        assert s.score == 8

    def test_score_submit_too_low(self):
        with pytest.raises(Exception):
            ScoreSubmit(player_id="p1", hole_number=1, glass_number=1, score=-2)

    def test_score_submit_too_high(self):
        with pytest.raises(Exception):
            ScoreSubmit(player_id="p1", hole_number=1, glass_number=1, score=9)

    def test_leaderboard_entry(self):
        e = LeaderboardEntry(
            player_id="p1", player_name="Alice",
            total_score=12, holes_played=6, scores_by_hole=[],
        )
        assert e.total_score == 12

    def test_leaderboard_response(self):
        r = LeaderboardResponse(
            leaderboard=[], course_name="Test", total_holes=18,
        )
        assert r.total_holes == 18


class TestCreateGlassSet:
    @pytest.mark.asyncio
    async def test_creates_with_qr_codes(self):
        mock_collection = AsyncMock()
        with patch("app.services.game.glass_sets", return_value=mock_collection):
            result = await create_glass_set({
                "course_id": "123",
                "course_name": "Pebble Beach",
                "glass_count": 3,
                "holes_per_glass": 6,
            })

        assert result["course_name"] == "Pebble Beach"
        assert len(result["qr_codes"]) == 3
        assert result["qr_codes"][0]["glass_number"] == 1
        assert "/play/" in result["qr_codes"][0]["url"]
        assert "<" in result["qr_codes"][0]["qr_svg"]  # SVG content
        mock_collection.insert_one.assert_called_once()


class TestGetGlassSet:
    @pytest.mark.asyncio
    async def test_found(self):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = {
            "_id": "abc123",
            "course_name": "Pebble Beach",
            "qr_codes": [],
        }
        with patch("app.services.game.glass_sets", return_value=mock_collection):
            result = await get_glass_set("abc123")
        assert result["id"] == "abc123"
        assert result["course_name"] == "Pebble Beach"

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = None
        with patch("app.services.game.glass_sets", return_value=mock_collection):
            result = await get_glass_set("nonexistent")
        assert result is None


class TestFindOrCreateSession:
    @pytest.mark.asyncio
    async def test_finds_existing(self):
        mock_sessions = AsyncMock()
        mock_sessions.find_one.return_value = {
            "_id": "session1",
            "glass_set_id": "gs1",
            "active": True,
            "course_name": "Test",
        }
        with patch("app.services.game.game_sessions", return_value=mock_sessions):
            result = await find_or_create_session("gs1")
        assert result["id"] == "session1"

    @pytest.mark.asyncio
    async def test_creates_new(self):
        mock_sessions = AsyncMock()
        mock_sessions.find_one.return_value = None
        mock_gs = AsyncMock()
        mock_gs.find_one.return_value = {
            "_id": "gs1",
            "course_name": "Pebble",
            "glass_count": 3,
            "holes_per_glass": 6,
        }
        with (
            patch("app.services.game.game_sessions", return_value=mock_sessions),
            patch("app.services.game.glass_sets", return_value=mock_gs),
        ):
            result = await find_or_create_session("gs1")
        assert result["course_name"] == "Pebble"
        mock_sessions.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_glass_set_not_found(self):
        mock_sessions = AsyncMock()
        mock_sessions.find_one.return_value = None
        mock_gs = AsyncMock()
        mock_gs.find_one.return_value = None
        with (
            patch("app.services.game.game_sessions", return_value=mock_sessions),
            patch("app.services.game.glass_sets", return_value=mock_gs),
        ):
            with pytest.raises(ValueError, match="not found"):
                await find_or_create_session("bad_id")


class TestSubmitScore:
    @pytest.mark.asyncio
    async def test_upserts_score(self):
        mock_collection = AsyncMock()
        with patch("app.services.game.scores", return_value=mock_collection):
            result = await submit_score("s1", "p1", 5, 1, 3)
        assert result["score"] == 3
        assert result["hole_number"] == 5
        mock_collection.update_one.assert_called_once()


class AsyncIterator:
    def __init__(self, items):
        self.items = iter(items)
    def __aiter__(self):
        return self
    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration
    def sort(self, *args, **kwargs):
        return self


class TestGetLeaderboard:
    @pytest.mark.asyncio
    async def test_aggregates_scores(self):
        mock_sessions = AsyncMock()
        mock_sessions.find_one.return_value = {
            "_id": "s1",
            "course_name": "Test",
            "glass_count": 3,
            "holes_per_glass": 6,
        }
        mock_players = MagicMock()
        mock_players.find.return_value = AsyncIterator([
            {"_id": "p1", "player_name": "Alice", "session_id": "s1"},
            {"_id": "p2", "player_name": "Bob", "session_id": "s1"},
        ])
        mock_scores = MagicMock()
        mock_scores.find.return_value = AsyncIterator([
            {"player_id": "p1", "hole_number": 1, "glass_number": 1, "score": 2},
            {"player_id": "p1", "hole_number": 2, "glass_number": 1, "score": 5},
            {"player_id": "p2", "hole_number": 1, "glass_number": 1, "score": 1},
        ])

        with (
            patch("app.services.game.game_sessions", return_value=mock_sessions),
            patch("app.services.game.players", return_value=mock_players),
            patch("app.services.game.scores", return_value=mock_scores),
        ):
            result = await get_leaderboard("s1")

        assert result["course_name"] == "Test"
        assert result["total_holes"] == 18
        assert len(result["leaderboard"]) == 2
        # Bob (1) should be first, Alice (7) second (lowest first)
        assert result["leaderboard"][0]["player_name"] == "Bob"
        assert result["leaderboard"][0]["total_score"] == 1
        assert result["leaderboard"][1]["total_score"] == 7


class TestEndpoints:
    def _get_client(self):
        from app.main import app
        from fastapi.testclient import TestClient
        return TestClient(app)

    @patch("app.api.v1.qr.create_glass_set", new_callable=AsyncMock)
    def test_create_glass_set(self, mock_create):
        mock_create.return_value = {
            "id": "abc123",
            "course_id": "c1",
            "course_name": "Pebble",
            "glass_count": 3,
            "holes_per_glass": 6,
            "created_at": "2025-01-01",
            "qr_codes": [],
        }
        client = self._get_client()
        response = client.post("/api/v1/glass-sets", json={
            "course_id": "c1",
            "course_name": "Pebble",
        })
        assert response.status_code == 200
        assert response.json()["id"] == "abc123"

    @patch("app.api.v1.qr.get_glass_set", new_callable=AsyncMock)
    def test_get_glass_set(self, mock_get):
        mock_get.return_value = {"id": "abc", "course_name": "Test"}
        client = self._get_client()
        response = client.get("/api/v1/glass-sets/abc")
        assert response.status_code == 200

    @patch("app.api.v1.qr.get_glass_set", new_callable=AsyncMock)
    def test_get_glass_set_not_found(self, mock_get):
        mock_get.return_value = None
        client = self._get_client()
        response = client.get("/api/v1/glass-sets/nonexistent")
        assert response.status_code == 404

    @patch("app.api.v1.games.get_session", new_callable=AsyncMock)
    @patch("app.api.v1.games.add_player", new_callable=AsyncMock)
    @patch("app.api.v1.games.find_or_create_session", new_callable=AsyncMock)
    def test_join_game(self, mock_session, mock_add, mock_get):
        mock_session.return_value = {
            "id": "s1", "course_name": "Test",
            "glass_count": 3, "holes_per_glass": 6,
        }
        mock_add.return_value = {
            "player_id": "p1", "player_name": "Alice", "session_id": "s1",
        }
        mock_get.return_value = {
            "id": "s1", "players": [{"player_id": "p1", "player_name": "Alice"}],
        }
        client = self._get_client()
        response = client.post("/api/v1/games/join", json={
            "glass_set_id": "gs1",
            "player_name": "Alice",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["player_name"] == "Alice"

    @patch("app.api.v1.games.submit_score", new_callable=AsyncMock)
    def test_submit_score(self, mock_submit):
        mock_submit.return_value = {
            "session_id": "s1", "player_id": "p1",
            "hole_number": 1, "glass_number": 1, "score": 3,
        }
        client = self._get_client()
        response = client.post("/api/v1/games/s1/score", json={
            "player_id": "p1",
            "hole_number": 1,
            "glass_number": 1,
            "score": 3,
        })
        assert response.status_code == 200
        assert response.json()["ok"] is True

    def test_submit_score_validation(self):
        client = self._get_client()
        response = client.post("/api/v1/games/s1/score", json={
            "player_id": "p1",
            "hole_number": 1,
            "glass_number": 1,
            "score": 10,  # too high
        })
        assert response.status_code == 422  # validation error

    @patch("app.api.v1.games.get_leaderboard", new_callable=AsyncMock)
    def test_get_leaderboard(self, mock_lb):
        mock_lb.return_value = {
            "leaderboard": [
                {"player_id": "p1", "player_name": "Alice",
                 "total_score": 5, "holes_played": 3, "scores_by_hole": []},
            ],
            "course_name": "Test",
            "total_holes": 18,
        }
        client = self._get_client()
        response = client.get("/api/v1/games/s1/leaderboard")
        assert response.status_code == 200
        assert len(response.json()["leaderboard"]) == 1

    @patch("app.api.v1.games.get_player_scores", new_callable=AsyncMock)
    def test_get_player_scores(self, mock_scores):
        mock_scores.return_value = [
            {"hole_number": 1, "glass_number": 1, "score": 2},
        ]
        client = self._get_client()
        response = client.get("/api/v1/games/s1/scores/p1")
        assert response.status_code == 200
        assert len(response.json()["scores"]) == 1
