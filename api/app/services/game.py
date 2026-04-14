"""Game service — glass sets, sessions, players, and scoring."""
from __future__ import annotations

import io
import secrets
import string
from datetime import datetime, timezone

import qrcode
import qrcode.image.svg

from app.core.config import settings
from app.db.mongo import glass_sets, game_sessions, players, scores


def _generate_id(length: int = 8) -> str:
    """Generate a short, URL-safe alphanumeric ID."""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_qr_svg(url: str) -> str:
    """Generate a QR code as an SVG string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    factory = qrcode.image.svg.SvgPathImage
    img = qr.make_image(image_factory=factory)

    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode("utf-8")


async def create_glass_set(data: dict) -> dict:
    """Create a new glass set with QR codes."""
    glass_set_id = _generate_id()
    now = datetime.now(timezone.utc)

    qr_codes = []
    for i in range(1, data["glass_count"] + 1):
        url = f"{settings.FRONTEND_URL}/play/{glass_set_id}?glass={i}"
        qr_svg = generate_qr_svg(url)
        qr_codes.append({
            "glass_number": i,
            "url": url,
            "qr_svg": qr_svg,
        })

    doc = {
        "_id": glass_set_id,
        "course_id": data["course_id"],
        "course_name": data["course_name"],
        "glass_count": data["glass_count"],
        "holes_per_glass": data["holes_per_glass"],
        "created_at": now.isoformat(),
        "qr_codes": qr_codes,
    }

    collection = glass_sets()
    await collection.insert_one(doc)

    return {
        "id": glass_set_id,
        "course_id": data["course_id"],
        "course_name": data["course_name"],
        "glass_count": data["glass_count"],
        "holes_per_glass": data["holes_per_glass"],
        "created_at": now.isoformat(),
        "qr_codes": qr_codes,
    }


async def get_glass_set(glass_set_id: str) -> dict | None:
    """Retrieve a glass set by ID."""
    collection = glass_sets()
    doc = await collection.find_one({"_id": glass_set_id})
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


async def find_or_create_session(glass_set_id: str) -> dict:
    """Find an active session for a glass set, or create one."""
    collection = game_sessions()

    # Look for active session
    session = await collection.find_one({
        "glass_set_id": glass_set_id,
        "active": True,
    })

    if session:
        session["id"] = str(session.pop("_id"))
        return session

    # Get glass set info
    gs = await glass_sets().find_one({"_id": glass_set_id})
    if not gs:
        raise ValueError(f"Glass set {glass_set_id} not found")

    # Create new session
    session_id = _generate_id(10)
    now = datetime.now(timezone.utc)
    doc = {
        "_id": session_id,
        "glass_set_id": glass_set_id,
        "course_name": gs.get("course_name", ""),
        "glass_count": gs.get("glass_count", 3),
        "holes_per_glass": gs.get("holes_per_glass", 6),
        "active": True,
        "created_at": now.isoformat(),
    }
    await collection.insert_one(doc)
    doc["id"] = doc.pop("_id")
    return doc


async def add_player(session_id: str, player_name: str) -> dict:
    """Register a player in a session."""
    player_id = _generate_id(8)
    now = datetime.now(timezone.utc)

    doc = {
        "_id": player_id,
        "session_id": session_id,
        "player_name": player_name,
        "joined_at": now.isoformat(),
    }
    collection = players()
    await collection.insert_one(doc)

    return {
        "player_id": player_id,
        "player_name": player_name,
        "session_id": session_id,
    }


async def get_session(session_id: str) -> dict | None:
    """Get session details with players."""
    collection = game_sessions()
    session = await collection.find_one({"_id": session_id})
    if not session:
        return None

    session["id"] = str(session.pop("_id"))

    # Get players
    player_list = []
    async for p in players().find({"session_id": session_id}):
        player_list.append({
            "player_id": str(p["_id"]),
            "player_name": p["player_name"],
            "joined_at": p.get("joined_at", ""),
        })
    session["players"] = player_list
    return session


async def submit_score(session_id: str, player_id: str,
                       hole_number: int, glass_number: int, score: int) -> dict:
    """Submit or update a score for a hole."""
    collection = scores()
    now = datetime.now(timezone.utc)

    filter_doc = {
        "session_id": session_id,
        "player_id": player_id,
        "hole_number": hole_number,
    }
    update_doc = {
        "$set": {
            "session_id": session_id,
            "player_id": player_id,
            "hole_number": hole_number,
            "glass_number": glass_number,
            "score": score,
            "updated_at": now.isoformat(),
        }
    }

    await collection.update_one(filter_doc, update_doc, upsert=True)

    return {
        "session_id": session_id,
        "player_id": player_id,
        "hole_number": hole_number,
        "glass_number": glass_number,
        "score": score,
    }


async def get_leaderboard(session_id: str) -> dict:
    """Aggregate scores per player and return sorted leaderboard."""
    session = await get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    player_list = session.get("players", [])
    player_map = {p["player_id"]: p["player_name"] for p in player_list}

    # Get all scores for this session
    score_collection = scores()
    all_scores: dict[str, list[dict]] = {}
    async for s in score_collection.find({"session_id": session_id}):
        pid = s["player_id"]
        if pid not in all_scores:
            all_scores[pid] = []
        all_scores[pid].append({
            "hole_number": s["hole_number"],
            "glass_number": s["glass_number"],
            "score": s["score"],
        })

    # Build leaderboard
    entries = []
    for pid, player_scores in all_scores.items():
        total = sum(s["score"] for s in player_scores)
        sorted_scores = sorted(player_scores, key=lambda s: s["hole_number"])
        entries.append({
            "player_id": pid,
            "player_name": player_map.get(pid, "Unknown"),
            "total_score": total,
            "holes_played": len(player_scores),
            "scores_by_hole": sorted_scores,
        })

    # Also include players with no scores
    for pid, name in player_map.items():
        if pid not in all_scores:
            entries.append({
                "player_id": pid,
                "player_name": name,
                "total_score": 0,
                "holes_played": 0,
                "scores_by_hole": [],
            })

    entries.sort(key=lambda e: e["total_score"])

    total_holes = session.get("glass_count", 3) * session.get("holes_per_glass", 6)

    return {
        "leaderboard": entries,
        "course_name": session.get("course_name", ""),
        "total_holes": total_holes,
    }


async def get_player_scores(session_id: str, player_id: str) -> list[dict]:
    """Get all scores for a specific player, organized by glass and hole."""
    score_collection = scores()
    result = []
    async for s in score_collection.find({
        "session_id": session_id,
        "player_id": player_id,
    }).sort("hole_number", 1):
        result.append({
            "hole_number": s["hole_number"],
            "glass_number": s["glass_number"],
            "score": s["score"],
        })
    return result
