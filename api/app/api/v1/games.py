"""Game sessions, players, and score tracking."""

from fastapi import APIRouter, HTTPException

from app.schemas.game import JoinGameRequest, ScoreSubmit
from app.services.game import (
    find_or_create_session,
    add_player,
    get_session,
    submit_score,
    get_leaderboard,
    get_player_scores,
)

router = APIRouter()


@router.post("/games/join")
async def join_game(data: JoinGameRequest):
    """Join a game session via QR code scan."""
    try:
        session = await find_or_create_session(data.glass_set_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    player = await add_player(session["id"], data.player_name)

    return {
        "session_id": session["id"],
        "player_id": player["player_id"],
        "player_name": player["player_name"],
        "session": {
            "players": (await get_session(session["id"])).get("players", []),
            "course_name": session.get("course_name", ""),
            "glass_count": session.get("glass_count", 3),
            "holes_per_glass": session.get("holes_per_glass", 6),
        },
    }


@router.get("/games/{session_id}")
async def get_game_session(session_id: str):
    """Get full session with players list and course config."""
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/games/{session_id}/score")
async def submit_game_score(session_id: str, data: ScoreSubmit):
    """Submit a score for a hole."""
    if data.score < -1 or data.score > 8:
        raise HTTPException(status_code=400, detail="Score must be between -1 and 8")

    record = await submit_score(
        session_id, data.player_id, data.hole_number, data.glass_number, data.score
    )
    return {"ok": True, "score_record": record}


@router.get("/games/{session_id}/leaderboard")
async def get_game_leaderboard(session_id: str):
    """Get cumulative leaderboard for a game session."""
    try:
        result = await get_leaderboard(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/games/{session_id}/scores/{player_id}")
async def get_player_game_scores(session_id: str, player_id: str):
    """Get all scores for a specific player."""
    result = await get_player_scores(session_id, player_id)
    return {"scores": result}
