"""Tests for search service and endpoint."""

from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

import pytest
import httpx
from fastapi.testclient import TestClient

from app.services.golf.search import search_courses, _sanitize_query


class TestSanitizeQuery:
    def test_basic(self):
        assert _sanitize_query("Pebble Beach") == "pebble beach"

    def test_special_chars(self):
        assert _sanitize_query("pebble-beach!") == "pebblebeach"

    def test_whitespace(self):
        assert _sanitize_query("  pebble  beach  ") == "pebble  beach"

    def test_empty(self):
        assert _sanitize_query("") == ""


class TestSearchService:
    @pytest.mark.asyncio
    async def test_empty_query_returns_empty(self):
        result = await search_courses("")
        assert result == []

    @pytest.mark.asyncio
    async def test_whitespace_query_returns_empty(self):
        result = await search_courses("   ")
        assert result == []

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = {
            "query": "pebble beach",
            "data": [{"id": 1, "name": "Pebble Beach"}],
            "cached_at": datetime.now(timezone.utc),
        }

        with patch("app.services.golf.search.search_cache", return_value=mock_collection):
            result = await search_courses("Pebble Beach")

        assert len(result) == 1
        assert result[0]["name"] == "Pebble Beach"
        mock_collection.find_one.assert_called_once_with({"query": "pebble beach"})

    @pytest.mark.asyncio
    async def test_cache_miss_calls_api(self):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = None

        api_response = {"courses": [{"id": 2, "name": "Augusta"}]}
        mock_response = MagicMock()
        mock_response.json.return_value = api_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("app.services.golf.search.search_cache", return_value=mock_collection),
            patch("app.services.golf.search.httpx.AsyncClient", return_value=mock_client),
        ):
            result = await search_courses("Augusta")

        assert len(result) == 1
        assert result[0]["name"] == "Augusta"
        mock_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_error_propagates(self):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("app.services.golf.search.search_cache", return_value=mock_collection),
            patch("app.services.golf.search.httpx.AsyncClient", return_value=mock_client),
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await search_courses("bad query")


class TestSearchEndpoint:
    def _get_client(self):
        from app.main import app
        return TestClient(app)

    @patch("app.api.v1.search.search_courses", new_callable=AsyncMock)
    def test_empty_query(self, mock_search):
        client = self._get_client()
        response = client.get("/api/v1/search")
        assert response.status_code == 200
        assert response.json() == {"courses": []}
        mock_search.assert_not_called()

    @patch("app.api.v1.search.search_courses", new_callable=AsyncMock)
    def test_search_returns_courses(self, mock_search):
        mock_search.return_value = [{"id": 1, "name": "Pebble Beach"}]
        client = self._get_client()
        response = client.get("/api/v1/search?q=pebble")
        assert response.status_code == 200
        data = response.json()
        assert len(data["courses"]) == 1
        mock_search.assert_called_once_with("pebble")

    @patch("app.api.v1.search.search_courses", new_callable=AsyncMock)
    def test_api_error_returns_502(self, mock_search):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_search.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )
        client = self._get_client()
        response = client.get("/api/v1/search?q=bad")
        assert response.status_code == 502
