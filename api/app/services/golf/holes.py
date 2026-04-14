"""Hole association service — spatial matching of OSM features to holes."""
from __future__ import annotations

import math


def _dist_sq(a: list[float], b: list[float]) -> float:
    dlat = a[0] - b[0]
    dlon = a[1] - b[1]
    return dlat * dlat + dlon * dlon


def _min_dist_between(coords1: list[list[float]], coords2: list[list[float]]) -> float:
    """Minimum distance between any pair of points from two coordinate lists."""
    best = math.inf
    for a in coords1:
        for b in coords2:
            d = _dist_sq(a, b)
            if d < best:
                best = d
    return math.sqrt(best)


def _bbox(coords: list[list[float]], pad: float = 0.0) -> dict:
    """Compute bounding box for a set of coordinates with optional padding."""
    min_lat = min_lon = math.inf
    max_lat = max_lon = -math.inf
    for lat, lon in coords:
        if lat < min_lat:
            min_lat = lat
        if lat > max_lat:
            max_lat = lat
        if lon < min_lon:
            min_lon = lon
        if lon > max_lon:
            max_lon = lon
    return {
        "min_lat": min_lat - pad,
        "max_lat": max_lat + pad,
        "min_lon": min_lon - pad,
        "max_lon": max_lon + pad,
    }


def _bbox_overlaps(a: dict, b: dict) -> bool:
    return (
        a["min_lat"] <= b["max_lat"]
        and a["max_lat"] >= b["min_lat"]
        and a["min_lon"] <= b["max_lon"]
        and a["max_lon"] >= b["min_lon"]
    )


def _get_api_hole_data(course_data: dict | None) -> list[dict]:
    """Extract hole-by-hole data from Golf API response. Uses longest male tee set."""
    if not course_data or not course_data.get("tees"):
        return []

    tees = course_data["tees"]
    male_tees = tees.get("male", []) if isinstance(tees, dict) else []
    female_tees = tees.get("female", []) if isinstance(tees, dict) else []
    all_tees = male_tees + female_tees

    if not all_tees:
        return []

    if male_tees:
        primary = max(male_tees, key=lambda t: t.get("total_yards", 0))
    else:
        primary = max(all_tees, key=lambda t: t.get("total_yards", 0))

    return primary.get("holes", [])


def _estimate_difficulty(par: int, yardage: int) -> int:
    """Estimate difficulty rank (1-18) from par and yardage."""
    expected = {3: 170, 4: 400, 5: 530}
    exp = expected.get(par, 400)
    ratio = yardage / exp
    rank = round(18 - (ratio - 0.7) * (17 / 0.6))
    return max(1, min(18, rank))


def associate_features(features: list[dict], course_data: dict | None = None) -> list[dict]:
    """Associate OSM features with holes.

    Returns a list of hole bundle dicts with associated features.
    """
    # Extract and deduplicate hole features
    raw_holes = sorted(
        [f for f in features if f.get("category") == "hole" and f.get("ref")],
        key=lambda f: int(f["ref"]),
    )

    holes_by_ref: dict[str, dict] = {}
    for h in raw_holes:
        existing = holes_by_ref.get(h["ref"])
        if not existing or len(h.get("coords", [])) > len(existing.get("coords", [])):
            holes_by_ref[h["ref"]] = h

    holes = sorted(holes_by_ref.values(), key=lambda h: int(h["ref"]))

    if not holes:
        return []

    other_features = [
        f for f in features if f.get("category") not in ("hole", "course_boundary")
    ]

    # Pre-compute bounding boxes
    hole_bboxes = [_bbox(h["coords"], 0.002) for h in holes]

    # Build feature-to-hole map
    hole_feature_map: dict[str, list[dict]] = {h["ref"]: [] for h in holes}

    for feat in other_features:
        if feat.get("category") == "path":
            continue

        feat_bbox = _bbox(feat["coords"], 0.001)

        distances = []
        for i, hole in enumerate(holes):
            if not _bbox_overlaps(feat_bbox, hole_bboxes[i]):
                distances.append((hole, math.inf))
                continue
            d = _min_dist_between(feat["coords"], hole["coords"])
            distances.append((hole, d))

        distances.sort(key=lambda x: x[1])
        nearest_hole, nearest_dist = distances[0]

        if nearest_dist == math.inf:
            continue

        hole_feature_map[nearest_hole["ref"]].append(feat)

    # Get API hole data
    api_holes = _get_api_hole_data(course_data)

    # Build result
    result = []
    for hole in holes:
        ref = int(hole["ref"])
        api_hole = api_holes[ref - 1] if ref - 1 < len(api_holes) else {}

        if api_hole.get("handicap"):
            difficulty = api_hole["handicap"]
        elif hole.get("par") and api_hole.get("yardage"):
            difficulty = _estimate_difficulty(hole["par"], api_hole["yardage"])
        else:
            difficulty = 9  # neutral default

        result.append({
            "ref": ref,
            "par": hole.get("par") or api_hole.get("par"),
            "yardage": api_hole.get("yardage"),
            "handicap": api_hole.get("handicap"),
            "difficulty": float(difficulty),
            "route_coords": hole["coords"],
            "features": hole_feature_map.get(hole["ref"], []),
        })

    return result
