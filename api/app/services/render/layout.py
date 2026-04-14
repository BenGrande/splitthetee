"""Layout engine — positions holes on rectangular canvas."""
from __future__ import annotations

import math


def compute_layout(holes: list[dict], opts: dict | None = None) -> dict:
    """Compute the layout for a set of holes on a rectangular canvas."""
    opts = opts or {}
    canvas_width = opts.get("canvas_width", 900)
    canvas_height = opts.get("canvas_height", 700)
    margin_x = opts.get("margin_x", 30)
    margin_y = opts.get("margin_y", 30)
    text_margin = opts.get("text_margin", 60)
    ruler_margin = opts.get("ruler_margin", 65)
    stats_margin = opts.get("stats_margin", 25)
    max_hole_width = opts.get("max_hole_width", 0.42)
    hole_padding = opts.get("hole_padding", 0.02)

    if not holes:
        return {"holes": [], "canvas_width": canvas_width, "canvas_height": canvas_height}

    draw_left = text_margin + stats_margin
    draw_right = canvas_width - margin_x - ruler_margin
    draw_top = margin_y
    draw_bottom = canvas_height - margin_y
    draw_width = draw_right - draw_left
    draw_height = draw_bottom - draw_top

    # Per-glass normalization
    total_yardage = sum(h.get("yardage") or 350 for h in holes)
    min_angle = 35
    max_angle = 55

    difficulties = [h.get("difficulty") or 9 for h in holes]
    min_diff = min(difficulties)
    max_diff = max(difficulties)
    diff_range = max_diff - min_diff or 1

    hole_layouts = []
    for hole in holes:
        diff = hole.get("difficulty") or 9
        easy_factor = (diff - min_diff) / diff_range
        angle_deg = max_angle - easy_factor * (max_angle - min_angle)
        angle_rad = angle_deg * math.pi / 180
        yardage = hole.get("yardage") or 350
        length_fraction = yardage / total_yardage
        hole_layouts.append({
            "hole": hole,
            "angle_deg": angle_deg,
            "angle_rad": angle_rad,
            "length_fraction": length_fraction,
            "yardage": yardage,
        })

    # Simulate zigzag
    raw_positions = _simulate_zigzag(hole_layouts, hole_padding)

    # Scale to fit canvas
    total_vertical = raw_positions[-1]["end_y"]
    scale_factor = draw_height / total_vertical if total_vertical > 0 else 1

    # Compute X centering
    raw_min_x = min(min(rp["start_x"], rp["end_x"]) for rp in raw_positions)
    raw_max_x = max(max(rp["start_x"], rp["end_x"]) for rp in raw_positions)
    raw_span = raw_max_x - raw_min_x or 0.5

    def map_x(nx):
        return draw_left + (nx - raw_min_x + (1 - raw_span) / 2) * draw_width

    # Position and transform features
    positioned = []
    for rp in raw_positions:
        start_x = map_x(rp["start_x"])
        start_y = draw_top + rp["start_y"] * scale_factor
        end_x = map_x(rp["end_x"])
        end_y = draw_top + rp["end_y"] * scale_factor
        length = rp["raw_length"] * scale_factor
        max_width = length * max_hole_width

        features = _transform_hole_features(
            rp["hole"], start_x, start_y, end_x, end_y, max_width
        )

        positioned.append({
            "ref": rp["hole"].get("ref"),
            "par": rp["hole"].get("par"),
            "yardage": rp["yardage"],
            "handicap": rp["hole"].get("handicap"),
            "difficulty": rp["hole"].get("difficulty"),
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "angle_deg": rp["angle_deg"],
            "direction": rp["direction"],
            "length": length,
            "features": features,
        })

    # Post-processing
    _fix_overlaps(positioned)
    _enforce_green_tee_gap(positioned)
    _rescale_to_fill(positioned, draw_left, draw_top, draw_width, draw_height)
    _pack_holes(positioned)
    _enforce_slope(positioned)
    _rescale_to_fill(positioned, draw_left, draw_top, draw_width, draw_height)

    return {
        "holes": positioned,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
        "draw_area": {
            "left": draw_left,
            "right": draw_right,
            "top": draw_top,
            "bottom": draw_bottom,
        },
    }


def _simulate_zigzag(hole_layouts: list[dict], gap_fraction: float) -> list[dict]:
    """Simulate zigzag in normalized space with gaps between holes."""
    n = len(hole_layouts)
    raw_lengths = [h["length_fraction"] for h in hole_layouts]
    cosines = [math.cos(h["angle_rad"]) for h in hole_layouts]
    sines = [math.sin(h["angle_rad"]) for h in hole_layouts]
    avg_length = sum(raw_lengths) / n
    gap = avg_length * gap_fraction

    cur_x = 0.12
    cur_y = 0.0
    direction = 1
    sweep_accum = 0.0
    target_sweep = 0.7 if n <= 3 else (0.6 if n <= 6 else 0.5)
    result = []

    for i in range(n):
        length = raw_lengths[i]
        dx = length * cosines[i]
        dy = length * sines[i]
        next_x = cur_x + dx * direction
        sweep_accum += dx

        if next_x > 0.88 or next_x < 0.12 or (sweep_accum > target_sweep and i < n - 1):
            direction *= -1
            next_x = cur_x + dx * direction
            sweep_accum = dx

        result.append({
            **hole_layouts[i],
            "start_x": cur_x,
            "start_y": cur_y,
            "end_x": next_x,
            "end_y": cur_y + dy,
            "direction": direction,
            "raw_length": length,
        })

        cur_x = next_x
        cur_y += dy

        if i < n - 1:
            cur_y += gap

    return result


def _rescale_to_fill(holes, draw_left, draw_top, draw_width, draw_height):
    """Rescale all positioned holes so their visible content fills the draw area."""
    content_min_y = math.inf
    content_max_y = -math.inf
    content_min_x = math.inf
    content_max_x = -math.inf

    for h in holes:
        content_min_y = min(content_min_y, h["start_y"] - 6)
        content_max_y = max(content_max_y, h["start_y"] + 20)
        content_min_x = min(content_min_x, h["start_x"] - 16)
        content_max_x = max(content_max_x, h["start_x"] + 16)
        for f in h["features"]:
            for x, y in f["coords"]:
                content_min_y = min(content_min_y, y)
                content_max_y = max(content_max_y, y)
                content_min_x = min(content_min_x, x)
                content_max_x = max(content_max_x, x)

    content_height = content_max_y - content_min_y
    content_width = content_max_x - content_min_x
    if content_height <= 0 or content_width <= 0:
        return

    y_rescale = draw_height / content_height
    x_rescale = draw_width / content_width

    for h in holes:
        h["start_x"] = draw_left + (h["start_x"] - content_min_x) * x_rescale
        h["end_x"] = draw_left + (h["end_x"] - content_min_x) * x_rescale
        h["start_y"] = draw_top + (h["start_y"] - content_min_y) * y_rescale
        h["end_y"] = draw_top + (h["end_y"] - content_min_y) * y_rescale
        h["length"] *= y_rescale
        for f in h["features"]:
            for c in f["coords"]:
                c[0] = draw_left + (c[0] - content_min_x) * x_rescale
                c[1] = draw_top + (c[1] - content_min_y) * y_rescale


def _enforce_green_tee_gap(holes, min_gap: float = 30):
    """Ensure adequate gap between upper hole's green and lower hole's tee."""
    if len(holes) < 2:
        return

    for i in range(1, len(holes)):
        prev = holes[i - 1]
        curr = holes[i]

        # Find lowest Y of previous hole's green features
        prev_green_bottom = prev["end_y"]
        for f in prev["features"]:
            if f.get("category") == "green":
                for _, y in f["coords"]:
                    prev_green_bottom = max(prev_green_bottom, y)

        # Find highest Y of current hole's tee features
        curr_tee_top = curr["start_y"]
        for f in curr["features"]:
            if f.get("category") == "tee":
                for _, y in f["coords"]:
                    curr_tee_top = min(curr_tee_top, y)

        gap = curr_tee_top - prev_green_bottom
        if gap < min_gap:
            shift = min_gap - gap
            for j in range(i, len(holes)):
                holes[j]["start_y"] += shift
                holes[j]["end_y"] += shift
                for f in holes[j]["features"]:
                    for c in f["coords"]:
                        c[1] += shift


def _fix_overlaps(holes):
    """Shift subsequent holes down to eliminate vertical overlap."""
    if len(holes) < 2:
        return
    min_gap = 28

    for i in range(1, len(holes)):
        prev = holes[i - 1]
        curr = holes[i]

        prev_max_y = prev["start_y"] + 20
        for f in prev["features"]:
            for _, y in f["coords"]:
                if y > prev_max_y:
                    prev_max_y = y

        curr_min_y = curr["start_y"] - 6
        for f in curr["features"]:
            for _, y in f["coords"]:
                if y < curr_min_y:
                    curr_min_y = y

        overlap = prev_max_y + min_gap - curr_min_y
        if overlap > 0:
            for j in range(i, len(holes)):
                holes[j]["start_y"] += overlap
                holes[j]["end_y"] += overlap
                for f in holes[j]["features"]:
                    for c in f["coords"]:
                        c[1] += overlap


def _pack_holes(holes):
    """Pack holes tight by removing excess vertical gaps."""
    if len(holes) < 2:
        return
    target_gap = 28

    for i in range(1, len(holes)):
        prev = holes[i - 1]
        curr = holes[i]

        prev_bottom = prev["start_y"] + 14
        for f in prev["features"]:
            for _, y in f["coords"]:
                prev_bottom = max(prev_bottom, y)

        curr_top = curr["start_y"] - 2
        for f in curr["features"]:
            for _, y in f["coords"]:
                curr_top = min(curr_top, y)

        current_gap = curr_top - prev_bottom
        if current_gap > target_gap:
            shift = -(current_gap - target_gap)
            for j in range(i, len(holes)):
                holes[j]["start_y"] += shift
                holes[j]["end_y"] += shift
                for f in holes[j]["features"]:
                    for c in f["coords"]:
                        c[1] += shift


def _enforce_slope(holes):
    """Ensure every hole's tee bottom is above the green top by a minimum amount."""
    min_drop = 6

    for h in holes:
        tees = [f for f in h["features"] if f["category"] == "tee"]
        greens = [f for f in h["features"] if f["category"] == "green"]
        if not tees or not greens:
            continue

        tee_bottom_y = -math.inf
        for t in tees:
            for _, y in t["coords"]:
                tee_bottom_y = max(tee_bottom_y, y)

        green_top_y = math.inf
        for g in greens:
            for _, y in g["coords"]:
                green_top_y = min(green_top_y, y)

        drop = green_top_y - tee_bottom_y
        if drop < min_drop:
            shift = min_drop - drop
            for f in h["features"]:
                if f["category"] == "tee":
                    continue
                for c in f["coords"]:
                    c[1] += shift
            h["end_y"] += shift


def _transform_hole_features(hole, start_x, start_y, end_x, end_y, max_width):
    """Transform a hole's geo-coordinate features to canvas space."""
    route = hole.get("route_coords") or hole.get("routeCoords", [])
    if not route or len(route) < 2:
        return []

    geo_tee = route[0]
    geo_green = route[-1]
    mid_lat = (geo_tee[0] + geo_green[0]) / 2
    cos_lat = math.cos(mid_lat * math.pi / 180)

    geo_dx = (geo_green[1] - geo_tee[1]) * cos_lat
    geo_dy = -(geo_green[0] - geo_tee[0])
    geo_len = math.sqrt(geo_dx * geo_dx + geo_dy * geo_dy)
    if geo_len == 0:
        return []

    canvas_dx = end_x - start_x
    canvas_dy = end_y - start_y
    canvas_len = math.sqrt(canvas_dx * canvas_dx + canvas_dy * canvas_dy)
    if canvas_len == 0:
        return []

    scale = canvas_len / geo_len

    geo_angle = math.atan2(geo_dy, geo_dx)
    canvas_angle = math.atan2(canvas_dy, canvas_dx)
    rotation = canvas_angle - geo_angle
    cos_r = math.cos(rotation)
    sin_r = math.sin(rotation)

    # Global width clamping
    core_categories = {"fairway", "green", "tee", "bunker", "rough"}
    min_perp = 0.0
    max_perp = 0.0
    for f in hole.get("features", []):
        if f.get("category") not in core_categories:
            continue
        for lat, lon in f.get("coords", []):
            dx = (lon - geo_tee[1]) * cos_lat
            dy = -(lat - geo_tee[0])
            perp = -dx * math.sin(geo_angle) + dy * math.cos(geo_angle)
            if perp < min_perp:
                min_perp = perp
            if perp > max_perp:
                max_perp = perp

    for lat, lon in route:
        dx = (lon - geo_tee[1]) * cos_lat
        dy = lat - geo_tee[0]
        perp = -dx * math.sin(geo_angle) + dy * math.cos(geo_angle)
        if perp < min_perp:
            min_perp = perp
        if perp > max_perp:
            max_perp = perp

    core_width = (max_perp - min_perp) * scale
    if core_width > max_width and core_width > 0:
        scale *= max_width / core_width

    # Corridor limits
    max_perp_canvas = max_width * 0.6
    max_along_canvas = canvas_len * 1.15
    min_along_canvas = -canvas_len * 0.15

    # Unit vectors
    ux = canvas_dx / canvas_len
    uy = canvas_dy / canvas_len
    px = -uy
    py = ux

    result = []
    for f in hole.get("features", []):
        f_scale = scale

        # Scale down water individually if too wide
        if f.get("category") == "water":
            f_min_perp = 0.0
            f_max_perp = 0.0
            for lat, lon in f.get("coords", []):
                dx = (lon - geo_tee[1]) * cos_lat
                dy = -(lat - geo_tee[0])
                perp = -dx * math.sin(geo_angle) + dy * math.cos(geo_angle)
                if perp < f_min_perp:
                    f_min_perp = perp
                if perp > f_max_perp:
                    f_max_perp = perp
            feat_width = (f_max_perp - f_min_perp) * f_scale
            if feat_width > max_perp_canvas * 1.5 and feat_width > 0:
                f_scale = f_scale * (max_perp_canvas * 1.2) / feat_width

        coords = []
        for lat, lon in f.get("coords", []):
            dx = (lon - geo_tee[1]) * cos_lat
            dy = -(lat - geo_tee[0])
            rx = (dx * cos_r - dy * sin_r) * f_scale
            ry = (dx * sin_r + dy * cos_r) * f_scale
            cx = start_x + rx
            cy = start_y + ry

            # Clamp to corridor
            along = (cx - start_x) * ux + (cy - start_y) * uy
            perp = (cx - start_x) * px + (cy - start_y) * py

            clamped_along = max(min_along_canvas, min(max_along_canvas, along))
            clamped_perp = max(-max_perp_canvas, min(max_perp_canvas, perp))

            if along != clamped_along or perp != clamped_perp:
                cx = start_x + clamped_along * ux + clamped_perp * px
                cy = start_y + clamped_along * uy + clamped_perp * py

            coords.append([cx, cy])

        result.append({
            "id": f.get("id"),
            "category": f.get("category"),
            "ref": f.get("ref"),
            "par": f.get("par"),
            "name": f.get("name"),
            "coords": coords,
        })

    return result


def split_into_glasses(holes: list[dict], glass_count: int) -> list[list[dict]]:
    """Split holes into glass groups."""
    n = len(holes)
    if glass_count <= 1 or n <= 3:
        return [holes]

    if glass_count == 2:
        mid = math.ceil(n / 2)
        return [holes[:mid], holes[mid:]]

    if glass_count == 6 and n >= 18:
        return [
            holes[0:3], holes[3:6], holes[6:9],
            holes[9:12], holes[12:15], holes[15:18],
        ]

    per_glass = math.ceil(n / glass_count)
    groups = []
    for i in range(0, n, per_glass):
        groups.append(holes[i:min(i + per_glass, n)])
    return groups
