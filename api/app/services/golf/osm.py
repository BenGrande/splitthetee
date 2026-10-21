"""OpenStreetMap / Overpass API service — fetch and parse course features."""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# Per-request timeout, overall deadline, and how long to wait before hedging
# with the next mirror. The Lambda / API Gateway budget is ~29s, so the whole
# Overpass phase must finish well inside that even when a mirror hangs.
OVERPASS_REQUEST_TIMEOUT = 20.0
OVERPASS_TOTAL_DEADLINE = 24.0
OVERPASS_STAGGER = 4.0
OVERPASS_USER_AGENT = "splitthetee/1.0 (+https://www.splitthetee.com)"


async def _post_overpass(client: httpx.AsyncClient, endpoint: str, query: str) -> dict | None:
    """POST a query to one Overpass mirror. Returns parsed JSON or None on any failure."""
    try:
        response = await client.post(
            endpoint,
            data={"data": query},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    except Exception as exc:
        logger.warning("Overpass %s failed: %s", endpoint, exc)
        return None

    if not response.is_success:
        logger.warning("Overpass %s returned HTTP %s", endpoint, response.status_code)
        return None

    if response.text.lstrip().startswith("<"):
        logger.warning("Overpass %s returned HTML (busy)", endpoint)
        return None

    try:
        return response.json()
    except ValueError as exc:
        logger.warning("Overpass %s returned invalid JSON: %s", endpoint, exc)
        return None


async def query_overpass(query: str) -> dict | None:
    """Query Overpass, hedging across mirrors.

    The first mirror is tried immediately; if it has not answered within
    OVERPASS_STAGGER seconds the next mirror is started as well, and so on.
    The first successful JSON response wins and the rest are cancelled. The
    whole operation gives up after OVERPASS_TOTAL_DEADLINE seconds so a hung
    mirror can never stall the API past the gateway timeout.
    """
    endpoints = list(settings.OVERPASS_ENDPOINTS)
    if not endpoints:
        return None

    loop = asyncio.get_running_loop()
    deadline = loop.time() + OVERPASS_TOTAL_DEADLINE
    tasks: set[asyncio.Task] = set()
    next_idx = 0

    async with httpx.AsyncClient(
        timeout=OVERPASS_REQUEST_TIMEOUT,
        headers={"User-Agent": OVERPASS_USER_AGENT},
    ) as client:
        try:
            while True:
                if next_idx < len(endpoints):
                    endpoint = endpoints[next_idx]
                    next_idx += 1
                    tasks.add(asyncio.create_task(_post_overpass(client, endpoint, query)))

                if not tasks:
                    return None

                remaining = deadline - loop.time()
                if remaining <= 0:
                    logger.warning("Overpass: deadline reached with no successful mirror")
                    return None

                more_mirrors = next_idx < len(endpoints)
                wait_for = min(OVERPASS_STAGGER, remaining) if more_mirrors else remaining
                done, _ = await asyncio.wait(tasks, timeout=wait_for, return_when=asyncio.FIRST_COMPLETED)

                for task in done:
                    tasks.discard(task)
                    result = task.result()
                    if result is not None:
                        return result
                # Either the stagger elapsed or a mirror failed; loop to start the next one.
        finally:
            for task in tasks:
                task.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)


def _determine_category(tags: dict) -> str | None:
    """Map OSM tags to a feature category."""
    golf = tags.get("golf")
    leisure = tags.get("leisure")
    natural = tags.get("natural")
    water = tags.get("water")

    if golf == "fairway":
        return "fairway"
    if golf == "green":
        return "green"
    if golf == "tee":
        return "tee"
    if golf == "bunker":
        return "bunker"
    if golf == "rough":
        return "rough"
    if golf == "hole":
        return "hole"
    if golf in ("cartpath", "path"):
        return "path"
    if golf == "driving_range":
        return "fairway"
    if natural == "water" or water:
        return "water"
    if leisure == "golf_course":
        return "course_boundary"
    return None


def parse_overpass_features(raw: dict) -> list[dict]:
    """Convert raw Overpass response elements into feature dicts."""
    nodes: dict[int, list[float]] = {}
    for el in raw.get("elements", []):
        if el.get("type") == "node":
            nodes[el["id"]] = [el["lat"], el["lon"]]

    features = []
    for el in raw.get("elements", []):
        if el.get("type") != "way" or not el.get("tags"):
            continue

        coords = [nodes[nid] for nid in el.get("nodes", []) if nid in nodes]
        if len(coords) < 2:
            continue

        category = _determine_category(el["tags"])
        if category is None:
            continue

        par_str = el["tags"].get("par")
        features.append({
            "id": str(el["id"]),
            "category": category,
            "ref": el["tags"].get("ref"),
            "par": int(par_str) if par_str else None,
            "name": el["tags"].get("name"),
            "coords": coords,
        })

    return features


async def fetch_course_map(lat: float, lng: float, radius: int = 2000) -> dict:
    """Fetch course map features from OSM.

    Returns dict with 'features' and 'center' keys.
    """
    radius = min(radius, 3000)

    query = f"""[out:json][timeout:20];
(
  way["golf"](around:{radius},{lat},{lng});
  relation["golf"](around:{radius},{lat},{lng});
  way["natural"="water"](around:{radius},{lat},{lng});
  relation["natural"="water"](around:{radius},{lat},{lng});
  way["water"](around:{radius},{lat},{lng});
  relation["water"](around:{radius},{lat},{lng});
  way["leisure"="golf_course"](around:{radius},{lat},{lng});
  relation["leisure"="golf_course"](around:{radius},{lat},{lng});
);
out body;
>;
out skel qt;"""

    raw = await query_overpass(query)
    if raw is None:
        return {"features": [], "center": [lat, lng]}

    features = parse_overpass_features(raw)
    return {"features": features, "center": [lat, lng]}
