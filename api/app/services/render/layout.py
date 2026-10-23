"""Layout engine — positions holes on rectangular canvas."""
from __future__ import annotations

import math


def compute_layout(holes: list[dict], opts: dict | None = None) -> dict:
    """Compute the layout for a set of holes on a rectangular canvas."""
    opts = opts or {}
    canvas_width = opts.get("canvas_width", 900)
    canvas_height = opts.get("canvas_height", 700)
    # Scale layout chrome (rulers, title strip, info-box channels) with the
    # canvas so a 2738x1275 print-shop sheet doesn't reserve only the same
    # 45/50px strip designed for the 900x700 on-screen preview.
    chrome_scale = max(1.0, max(canvas_width / 900.0, canvas_height / 700.0))
    margin_x = opts.get("margin_x", 20 * chrome_scale)
    margin_y = opts.get("margin_y", 20 * chrome_scale)
    text_margin = opts.get("text_margin", 45 * chrome_scale)
    ruler_margin = opts.get("ruler_margin", 50 * chrome_scale)
    stats_margin = opts.get("stats_margin", 5 * chrome_scale)
    max_hole_width = opts.get("max_hole_width", 0.42)
    hole_padding = opts.get("hole_padding", 0.02)

    if not holes:
        return {"holes": [], "canvas_width": canvas_width, "canvas_height": canvas_height}

    if opts.get("synthesize_fairways", True):
        holes = [synthesize_missing_features(h) for h in holes]

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

    # Featured layout: a handful of hand-picked holes drawn big. Flatter
    # angles let each hole run most of the glass width, and length is only
    # half-weighted by yardage so a par 3 still reads as a full hole.
    featured = bool(opts.get("featured_layout")) and len(holes) <= 8
    if featured:
        min_angle = 16
        max_angle = 28

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
        if featured:
            length_fraction = 0.5 * length_fraction + 0.5 / len(holes)
        hole_layouts.append({
            "hole": hole,
            "angle_deg": angle_deg,
            "angle_rad": angle_rad,
            "length_fraction": length_fraction,
            "yardage": yardage,
        })

    if opts.get("layout") == "two_column" and (len(hole_layouts) >= 6 or (featured and len(hole_layouts) >= 2)):
        return _compute_two_pass_layout(
            holes, hole_layouts, opts,
            draw_left, draw_right, draw_top, draw_bottom,
            draw_width, draw_height,
            canvas_width, canvas_height,
            max_hole_width, hole_padding,
            featured=featured,
        )

    # Simulate zigzag (featured: reverse direction on every hole so each
    # one sweeps the full width instead of stair-stepping down the glass)
    if featured:
        raw_positions = _simulate_featured(hole_layouts, hole_padding)
    else:
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
        if featured:
            # x and y are scaled independently above; use the real spine
            # length so the width clamp does not shrink the features.
            length = math.hypot(end_x - start_x, end_y - start_y)
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

    # Post-processing. Featured holes get breathing room between them so
    # the big corridors never touch once the glass warp squeezes them.
    gap = draw_height * 0.035 if featured else 5
    _fix_overlaps(positioned, min_gap=gap)
    _enforce_green_tee_gap(positioned, min_gap=gap if featured else 2)
    _rescale_to_fill(positioned, draw_left, draw_top, draw_width, draw_height)
    _pack_holes(positioned, target_gap=gap)
    _enforce_slope(positioned)
    # Re-enforce after packing — packing can pull a later tee back above the
    # earlier green if feature coverage is uneven.
    _enforce_green_tee_gap(positioned, min_gap=gap if featured else 2)
    _rescale_to_fill(positioned, draw_left, draw_top, draw_width, draw_height)

    if featured:
        for h in positioned:
            h["_featured_label"] = True

    return {
        "holes": positioned,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
        "featured": featured,
        "draw_area": {
            "left": draw_left,
            "right": draw_right,
            "top": draw_top,
            "bottom": draw_bottom,
        },
    }


# ---------------------------------------------------------------------------
# Synthetic features for sparsely mapped courses
# ---------------------------------------------------------------------------
_METERS_PER_DEG_LAT = 111_320.0


def _offset_polyline(route: list[list[float]], half_width_m: float, cos_lat: float,
                     start_m: float, end_m: float, taper_m: float) -> list[list[float]]:
    """Build a closed polygon (lat, lon) around a centerline.

    The corridor starts ``start_m`` metres from the first point and stops
    ``end_m`` metres short of the last one. Width ramps up over ``taper_m``
    at the start and down again at the end so the ends are rounded rather
    than square. Returns [] when the corridor would be degenerate.
    """
    if len(route) < 2 or half_width_m <= 0:
        return []

    # Work in local metres with the first point as origin.
    lat0, lon0 = route[0]
    pts = [((lon - lon0) * cos_lat * _METERS_PER_DEG_LAT,
            (lat - lat0) * _METERS_PER_DEG_LAT) for lat, lon in route]

    # Cumulative arc length and per-vertex tangents.
    seg_len = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg_len.append(math.hypot(x1 - x0, y1 - y0))
    total = sum(seg_len)
    if total <= start_m + end_m + 1.0:
        return []

    def point_at(d: float) -> tuple[float, float, float, float]:
        """Position and unit tangent at arc distance d."""
        acc = 0.0
        for i, L in enumerate(seg_len):
            if L == 0:
                continue
            if d <= acc + L or i == len(seg_len) - 1:
                t = max(0.0, min(1.0, (d - acc) / L))
                (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t,
                        (x1 - x0) / L, (y1 - y0) / L)
            acc += L
        x, y = pts[-1]
        return x, y, 1.0, 0.0

    usable = total - start_m - end_m
    taper = min(taper_m, usable / 2.5)
    samples = max(8, int(usable / 12.0))
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for k in range(samples + 1):
        d_local = usable * k / samples
        x, y, tx, ty = point_at(start_m + d_local)
        # Rounded-ish ends: width follows a quarter-circle profile in the taper.
        if taper > 0 and d_local < taper:
            u = d_local / taper
            w = half_width_m * math.sqrt(max(0.0, 1 - (1 - u) ** 2))
        elif taper > 0 and d_local > usable - taper:
            u = (usable - d_local) / taper
            w = half_width_m * math.sqrt(max(0.0, 1 - (1 - u) ** 2))
        else:
            w = half_width_m
        nx, ny = -ty, tx
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))

    ring = left + right[::-1]
    out = []
    for x, y in ring:
        out.append([lat0 + y / _METERS_PER_DEG_LAT,
                    lon0 + x / (_METERS_PER_DEG_LAT * cos_lat)])
    out.append(out[0])
    return out


def _route_coverage(coords: list[list[float]], route: list[list[float]],
                    cos_lat: float, max_dist_m: float = 60.0) -> float:
    """Fraction of polygon vertices within ``max_dist_m`` of the route polyline."""
    if not coords or len(route) < 2:
        return 0.0

    def to_m(p):
        return ((p[1] - route[0][1]) * cos_lat * _METERS_PER_DEG_LAT,
                (p[0] - route[0][0]) * _METERS_PER_DEG_LAT)

    segs = [(to_m(a), to_m(b)) for a, b in zip(route, route[1:])]

    def dist_to_route(pt):
        best = math.inf
        px, py = pt
        for (ax, ay), (bx, by) in segs:
            vx, vy = bx - ax, by - ay
            L2 = vx * vx + vy * vy
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
            best = min(best, math.hypot(px - (ax + vx * t), py - (ay + vy * t)))
        return best

    near = sum(1 for c in coords if dist_to_route(to_m(c)) <= max_dist_m)
    return near / len(coords)


def synthesize_missing_features(hole: dict) -> dict:
    """Return a copy of ``hole`` with a fairway (and rough) corridor added when
    OpenStreetMap has none for it.

    Many courses are only partially mapped: tees, greens and bunkers exist
    but no fairway polygon, which renders as a few specks. The corridor
    follows ``route_coords`` so doglegs are preserved, and is sized by par.
    """
    route = hole.get("route_coords") or hole.get("routeCoords") or []
    if len(route) < 2:
        return hole
    features = list(hole.get("features") or [])
    mid_lat = sum(p[0] for p in route) / len(route)
    cos_lat = math.cos(mid_lat * math.pi / 180) or 1e-6

    # A fairway only counts if it actually sits on this hole's route. A
    # driving range or a neighbouring polygon that got associated by
    # proximity would otherwise block the corridor and draw as a blob.
    real_fairways = [f for f in features
                     if f.get("category") == "fairway"
                     and len(f.get("coords") or []) >= 2
                     and _route_coverage(f["coords"], route, cos_lat) >= 0.5]
    if real_fairways:
        return hole
    features = [f for f in features if f.get("category") != "fairway"]
    cats = {f.get("category") for f in features}

    par = hole.get("par") or 4

    if par <= 3:
        half_w, start_m, end_m = 12.0, 16.0, 12.0
    elif par == 4:
        half_w, start_m, end_m = 28.0, 40.0, 12.0
    else:
        half_w, start_m, end_m = 30.0, 45.0, 12.0

    hole_id = hole.get("ref", "x")
    fairway = _offset_polyline(route, half_w, cos_lat, start_m, end_m, taper_m=35.0)
    if not fairway:
        return hole

    synthetic = []
    if "rough" not in cats:
        rough = _offset_polyline(route, half_w + (9.0 if par <= 3 else 14.0), cos_lat,
                                 max(0.0, start_m - 30.0), max(0.0, end_m - 16.0),
                                 taper_m=30.0)
        if rough:
            synthetic.append({
                "id": f"synthetic-rough-{hole_id}", "category": "rough",
                "ref": None, "par": None, "name": None, "coords": rough,
                "synthetic": True,
            })
    synthetic.append({
        "id": f"synthetic-fairway-{hole_id}", "category": "fairway",
        "ref": None, "par": None, "name": None, "coords": fairway,
        "synthetic": True,
    })

    # Draw synthetic ground first so mapped tees/greens/bunkers sit on top.
    new_hole = dict(hole)
    new_hole["features"] = synthetic + features
    return new_hole


def _find_pass_split(hole_layouts: list[dict]) -> int:
    """Find the split index for two-column layout. Prefers 5 (holes 1-5 | 6-9)."""
    n = len(hole_layouts)
    candidates = [i for i in (4, 5) if 2 <= i <= n - 2]
    if not candidates:
        return n // 2
    # Prefer 5 when available so the left column has holes 1-5 and right has 6-9
    return 5 if 5 in candidates else candidates[0]


def _position_raw(raw_positions, hole_layouts_subset, draw_left, draw_top,
                  draw_width, draw_height, max_hole_width, true_length: bool = False):
    """Scale raw zigzag positions to canvas coordinates and transform features.

    ``true_length`` measures each hole's length from its canvas spine (x and
    y are scaled independently here) so the feature width clamp never
    shrinks a hole that sweeps a wide column.
    """
    if not raw_positions:
        return []

    total_vertical = raw_positions[-1]["end_y"]
    scale_factor = draw_height / total_vertical if total_vertical > 0 else 1

    raw_min_x = min(min(rp["start_x"], rp["end_x"]) for rp in raw_positions)
    raw_max_x = max(max(rp["start_x"], rp["end_x"]) for rp in raw_positions)
    raw_span = raw_max_x - raw_min_x or 0.5

    def map_x(nx):
        return draw_left + (nx - raw_min_x + (1 - raw_span) / 2) * draw_width

    positioned = []
    for rp in raw_positions:
        start_x = map_x(rp["start_x"])
        start_y = draw_top + rp["start_y"] * scale_factor
        end_x = map_x(rp["end_x"])
        end_y = draw_top + rp["end_y"] * scale_factor
        length = rp["raw_length"] * scale_factor
        if true_length:
            length = math.hypot(end_x - start_x, end_y - start_y)
        mw = length * max_hole_width

        features = _transform_hole_features(
            rp["hole"], start_x, start_y, end_x, end_y, mw
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

    return positioned


def _compute_two_pass_layout(holes, hole_layouts, opts,
                             draw_left, draw_right, draw_top, draw_bottom,
                             draw_width, draw_height,
                             canvas_width, canvas_height,
                             max_hole_width, hole_padding,
                             featured: bool = False):
    """Compute a side-by-side two-column layout — both columns span full height.

    Column 1 (first N holes): LEFT column, full canvas height.
    Column 2 (remaining holes): RIGHT column, full canvas height.
    Left ruler sits between the title and column 1; right ruler on the far right.
    """
    # Featured: balance the columns (3 | 2 for five holes) and keep the
    # extra hole on the left so the eye reads top-left first.
    split_idx = math.ceil(len(hole_layouts) / 2) if featured else _find_pass_split(hole_layouts)
    col1_layouts = hole_layouts[:split_idx]
    col2_layouts = hole_layouts[split_idx:]

    # Re-normalize length_fraction within each column
    for group in (col1_layouts, col2_layouts):
        total = sum(h["length_fraction"] for h in group)
        if total > 0:
            for h in group:
                h["length_fraction"] /= total

    # Layout geometry for two-column mode:
    #   title | left ruler | outside-left info-box channel | col 1 |
    #     middle gap (holds middle-left + middle-right info boxes) |
    #     col 2 | outside-right info-box channel | right ruler
    #
    # The left ruler is tight against the title, leaving a wider "outside"
    # channel where info boxes from holes with tees on the left side of their
    # column can sit — giving short dotted connectors.
    chrome_scale = max(1.0, max(canvas_width / 900.0, canvas_height / 700.0))
    # box_factor matches _render_hole_stats: callouts grow extra on large
    # rect canvases so they read as the hole's "card", not a postage stamp.
    box_factor = 1.0 if chrome_scale <= 1.0 else 1.8
    ruler_total_w = 30 * chrome_scale  # ruler width + safety padding
    info_channel_w = 32 * chrome_scale * box_factor  # space for the info box + padding on both sides

    left_ruler_right = draw_left + ruler_total_w  # left ruler ends here
    left_draw_left = left_ruler_right + info_channel_w
    # Right column ends leaving room for outside-right info channel + right ruler
    right_col_boundary = draw_right - info_channel_w - ruler_total_w
    effective_width = right_col_boundary - left_draw_left

    # Middle gap fits two info-box channels (direction-1 left col + dir+1 right col)
    col_gap = max(effective_width * 0.10, info_channel_w * 2 + 4)
    left_col_width = (effective_width - col_gap) / 2
    right_col_left = left_draw_left + left_col_width + col_gap
    right_col_width = effective_width - left_col_width - col_gap

    # Slightly wider holes than default for two-column mode
    two_col_hole_width = max(max_hole_width, 0.5)

    if featured:
        # Every hole gets the same slot height in both columns; a column
        # with fewer holes is centred vertically instead of stretched, so
        # the two columns read as one balanced composition. Columns mirror
        # each other (left column starts tee-left, right column tee-right).
        slots = max(len(col1_layouts), len(col2_layouts))
        slot_gap = draw_height * 0.05
        slot_h = (draw_height - slot_gap * (slots - 1)) / slots
        raw1 = _simulate_featured_column(col1_layouts, start_direction=1)
        raw2 = _simulate_featured_column(col2_layouts, start_direction=-1)
        col_tops = []
        col_heights = []
        for group in (col1_layouts, col2_layouts):
            k = len(group)
            h = slot_h * k + slot_gap * (k - 1)
            col_heights.append(h)
            col_tops.append(draw_top + (draw_height - h) / 2)
        pos1 = _position_raw(raw1, col1_layouts, left_draw_left, col_tops[0],
                             left_col_width, col_heights[0], two_col_hole_width,
                             true_length=True)
        pos2 = _position_raw(raw2, col2_layouts, right_col_left, col_tops[1],
                             right_col_width, col_heights[1], two_col_hole_width,
                             true_length=True)
        for group, dl, dw, dt, dh in [(pos1, left_draw_left, left_col_width, col_tops[0], col_heights[0]),
                                      (pos2, right_col_left, right_col_width, col_tops[1], col_heights[1])]:
            _fix_overlaps(group, min_gap=slot_gap)
            _enforce_green_tee_gap(group, min_gap=slot_gap)
            _rescale_to_fill(group, dl, dt, dw, dh, uniform=True)
            _pack_holes(group, target_gap=slot_gap)
            _enforce_slope(group)
            _enforce_green_tee_gap(group, min_gap=slot_gap)
            _rescale_to_fill(group, dl, dt, dw, dh, uniform=True)
    else:
        raw1 = _simulate_zigzag(col1_layouts, hole_padding,
                                start_x=0.06, start_direction=1)
        raw2 = _simulate_zigzag(col2_layouts, hole_padding,
                                start_x=0.06, start_direction=1)

        pos1 = _position_raw(raw1, col1_layouts, left_draw_left, draw_top,
                             left_col_width, draw_height, two_col_hole_width)
        pos2 = _position_raw(raw2, col2_layouts, right_col_left, draw_top,
                             right_col_width, draw_height, two_col_hole_width)

        # Post-process each column independently — both span full draw_height
        for group, dl, dw in [(pos1, left_draw_left, left_col_width),
                              (pos2, right_col_left, right_col_width)]:
            _fix_overlaps(group)
            _enforce_green_tee_gap(group)
            _rescale_to_fill(group, dl, draw_top, dw, draw_height)
            _pack_holes(group)
            _enforce_slope(group)
            _rescale_to_fill(group, dl, draw_top, dw, draw_height)

    # Stagger info-box positions alongside each hole. The box sits at the
    # GREEN's X position but at the TEE's Y level — so it's vertically above
    # the green and horizontally offset from the tee. The dotted connector
    # runs horizontally from the tee across to the box at the same Y.
    middle_gap_left_edge = left_draw_left + left_col_width
    middle_gap_right_edge = right_col_left
    if featured:
        # Featured: the hole card sits in the channel on the TEE's side, a
        # little below the tee, so the connector is short and the card reads
        # as the hole's title block. Outer channels for outer tees, the two
        # halves of the middle gap for inner tees.
        # The card sits in the empty upper corner of the slot: level with
        # the tee, halfway along the hole's run, so it is clear of the
        # rulers and the glass-edge reserves whichever way the glass warps.
        label_drop = 16 * chrome_scale
        for hole in pos1 + pos2:
            hole["_featured_label"] = True
            run = abs(hole["end_x"] - hole["start_x"])
            hole["_info_box_cx"] = hole["start_x"] + hole["direction"] * run * 0.5
            hole["_info_box_cy"] = hole["start_y"] + label_drop
    else:
        for group in (pos1, pos2):
            for hole in group:
                hole["_info_box_cx"] = hole["end_x"]    # same X as green
                hole["_info_box_cy"] = hole["start_y"]  # same Y as tee

    # If the default position (above the green) collides with any course
    # feature, shift the box horizontally until the overlap clears. Use the
    # actual rendered box dimensions and per-column bounds so the box stays
    # in its lane (between the ruler and the middle gap), not punted into
    # the opposite column.
    rb_w = 17 * chrome_scale * box_factor
    rb_h = 22 * chrome_scale * box_factor
    rb_safety = 2 * chrome_scale
    rb_shift = max(60, 0.4 * effective_width)
    rb_step = 3 * chrome_scale
    _resolve_info_box_overlaps(
        pos1,
        box_w=rb_w, box_h=rb_h,
        safety=rb_safety, max_shift=rb_shift, step=rb_step,
        min_cx=left_ruler_right + rb_w / 2 + rb_safety,
        max_cx=middle_gap_right_edge - rb_w / 2 - rb_safety,
    )
    _resolve_info_box_overlaps(
        pos2,
        box_w=rb_w, box_h=rb_h,
        safety=rb_safety, max_shift=rb_shift, step=rb_step,
        min_cx=middle_gap_left_edge + rb_w / 2 + rb_safety,
        max_cx=draw_right - ruler_total_w - rb_w / 2 - rb_safety,
    )

    positioned = pos1 + pos2

    return {
        "holes": positioned,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
        "layout_mode": "two_column",
        "featured": featured,
        "column_split": split_idx,
        "draw_area": {
            "left": left_draw_left,
            "right": draw_right,
            "top": draw_top,
            "bottom": draw_bottom,
            "left_ruler_right": left_ruler_right,
            "middle_gap_left": middle_gap_left_edge,
            "middle_gap_right": middle_gap_right_edge,
        },
    }


def _resolve_info_box_overlaps(holes: list[dict],
                               box_w: float = 13,
                               box_h: float = 18,
                               safety: float = 2,
                               max_shift: float = 60,
                               step: float = 3,
                               obstacles: list[dict] | None = None,
                               min_cx: float | None = None,
                               max_cx: float | None = None,
                               min_cx_fn=None) -> None:
    """Shift info boxes horizontally when their bounding rect overlaps any
    feature. Tries both LEFT and RIGHT shifts, picks the smaller successful
    one. `min_cx` / `max_cx` hard-stop the search in each direction.

    Checks each hole's `_info_box_cx/cy` against the bounding rectangles of
    all features (fairway/green/tee/bunker/water/rough) across the full hole
    set. Extra `obstacles` (e.g. the ruler area) can be provided as bbox
    dicts with `x_min/x_max/y_min/y_max`.
    """
    _categories = {"fairway", "green", "tee", "bunker", "water", "rough"}

    # Precompute feature bboxes + coord lists for quick rejection.
    feats = []
    for h in holes:
        for f in h.get("features", []):
            if f.get("category") not in _categories:
                continue
            coords = f.get("coords", [])
            if not coords:
                continue
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            feats.append({
                "x_min": min(xs), "x_max": max(xs),
                "y_min": min(ys), "y_max": max(ys),
                "coords": coords,
            })

    obstacles = obstacles or []

    def _overlaps(cx: float, cy: float) -> bool:
        x_min = cx - box_w / 2 - safety
        x_max = cx + box_w / 2 + safety
        y_min = cy - box_h / 2 - safety
        y_max = cy + box_h / 2 + safety
        # Bbox-only obstacles (e.g., ruler zone)
        for o in obstacles:
            if o["x_max"] < x_min or o["x_min"] > x_max:
                continue
            if o["y_max"] < y_min or o["y_min"] > y_max:
                continue
            return True
        # Feature coord checks
        for feat in feats:
            if feat["x_max"] < x_min or feat["x_min"] > x_max:
                continue
            if feat["y_max"] < y_min or feat["y_min"] > y_max:
                continue
            for x, y in feat["coords"]:
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    return True
        return False

    for hole in holes:
        if "_info_box_cx" not in hole or "_info_box_cy" not in hole:
            continue
        original_cx = hole["_info_box_cx"]
        box_cy = hole["_info_box_cy"]

        # Per-hole left bound (e.g. the ruler's right edge at this Y).
        hole_min_cx = min_cx
        if min_cx_fn is not None:
            try:
                hole_min_cx = min_cx_fn(box_cy)
            except Exception:
                pass

        if not _overlaps(original_cx, box_cy):
            continue  # already clear — leave it alone

        # Try shifting LEFT first; record shift size if it resolves.
        left_cx = None
        left_shift = 0.0
        shifted_cx = original_cx
        while left_shift < max_shift:
            shifted_cx -= step
            left_shift += step
            if hole_min_cx is not None and shifted_cx < hole_min_cx:
                break
            if not _overlaps(shifted_cx, box_cy):
                left_cx = shifted_cx
                break

        # Try shifting RIGHT; pick whichever direction has the smaller
        # resolving shift so the box stays as close to its hole as possible.
        right_cx = None
        right_shift = 0.0
        shifted_cx = original_cx
        while right_shift < max_shift:
            shifted_cx += step
            right_shift += step
            if max_cx is not None and shifted_cx > max_cx:
                break
            if not _overlaps(shifted_cx, box_cy):
                right_cx = shifted_cx
                break

        if left_cx is not None and right_cx is not None:
            hole["_info_box_cx"] = left_cx if left_shift <= right_shift else right_cx
        elif left_cx is not None:
            hole["_info_box_cx"] = left_cx
        elif right_cx is not None:
            hole["_info_box_cx"] = right_cx
        # else: couldn't resolve in either direction — leave original X.


def _simulate_zigzag(hole_layouts: list[dict], gap_fraction: float,
                     x_min: float = 0.06, x_max: float = 0.94,
                     start_x: float | None = None,
                     start_direction: int = 1,
                     target_sweep: float | None = None) -> list[dict]:
    """Simulate zigzag in normalized space with gaps between holes."""
    n = len(hole_layouts)
    raw_lengths = [h["length_fraction"] for h in hole_layouts]
    cosines = [math.cos(h["angle_rad"]) for h in hole_layouts]
    sines = [math.sin(h["angle_rad"]) for h in hole_layouts]
    avg_length = sum(raw_lengths) / n
    gap = avg_length * gap_fraction

    cur_x = start_x if start_x is not None else (x_min + 0.01)
    cur_y = 0.0
    direction = start_direction
    sweep_accum = 0.0
    if target_sweep is None:
        target_sweep = 0.7 if n <= 3 else (0.6 if n <= 6 else 0.5)
    result = []

    for i in range(n):
        length = raw_lengths[i]
        dx = length * cosines[i]
        dy = length * sines[i]
        next_x = cur_x + dx * direction
        sweep_accum += dx

        if next_x > x_max or next_x < x_min or (sweep_accum > target_sweep and i < n - 1):
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


def _simulate_featured_column(hole_layouts: list[dict], start_direction: int = 1,
                              x_min: float = 0.06, x_max: float = 0.94,
                              angle_deg: float = 48.0) -> list[dict]:
    """Stack featured holes in one column as equal-height diagonal slots.

    Each hole sweeps 70-100% of the column width (longer holes sweep more),
    zigzagging so consecutive tees and greens stay close. The slot height is
    the same for every hole; _position_raw scales the column to its box.
    """
    n = len(hole_layouts)
    if n == 0:
        return []
    span = x_max - x_min
    max_len = max(h["length_fraction"] for h in hole_layouts) or 1.0
    full_dx = span
    full_dy = full_dx * math.tan(math.radians(angle_deg))
    gap = full_dy * 0.12

    cur_y = 0.0
    direction = start_direction
    result = []
    for i, h in enumerate(hole_layouts):
        frac = 0.7 + 0.3 * h["length_fraction"] / max_len
        dx = full_dx * frac
        dy = full_dy  # same slot height for every hole
        # Centre shorter holes in the column so the column edges stay even.
        inset = (span - dx) / 2
        start_x = (x_min + inset) if direction > 0 else (x_max - inset)
        end_x = start_x + direction * dx
        result.append({
            **h,
            "start_x": start_x,
            "start_y": cur_y,
            "end_x": end_x,
            "end_y": cur_y + dy,
            "direction": direction,
            "raw_length": math.hypot(dx, dy),
        })
        cur_y += dy
        if i < n - 1:
            cur_y += gap
        direction *= -1
    return result


def _simulate_featured(hole_layouts: list[dict], gap_fraction: float,
                       x_min: float = 0.06, x_max: float = 0.94) -> list[dict]:
    """Place a few featured holes so each one sweeps most of the width.

    Direction alternates every hole (a true zigzag). Each hole's horizontal
    run is 65-100% of the available width, scaled by its relative length,
    and always starts at the edge so the holes read as big diagonal bands.
    """
    n = len(hole_layouts)
    span = x_max - x_min
    max_len = max(h["length_fraction"] for h in hole_layouts) or 1.0
    avg_length = sum(h["length_fraction"] for h in hole_layouts) / n
    gap = avg_length * gap_fraction

    cur_y = 0.0
    direction = 1
    result = []
    for i, h in enumerate(hole_layouts):
        dx = span * (0.55 + 0.45 * h["length_fraction"] / max_len)
        dy = dx * math.tan(h["angle_rad"])
        start_x = x_min if direction > 0 else x_max
        end_x = start_x + direction * dx
        result.append({
            **h,
            "start_x": start_x,
            "start_y": cur_y,
            "end_x": end_x,
            "end_y": cur_y + dy,
            "direction": direction,
            "raw_length": math.hypot(dx, dy),
        })
        cur_y += dy
        if i < n - 1:
            cur_y += gap
        direction *= -1
    return result


def _rescale_to_fill(holes, draw_left, draw_top, draw_width, draw_height,
                     uniform: bool = False):
    """Rescale all positioned holes so their visible content fills the draw area.

    ``uniform`` keeps the aspect ratio (one scale for x and y, content
    centred in the box) so designed hole angles survive; the default
    stretches x and y independently to fill the box exactly.
    """
    content_min_y = math.inf
    content_max_y = -math.inf
    content_min_x = math.inf
    content_max_x = -math.inf

    for h in holes:
        # Include BOTH endpoints of the hole spine (start is the tee label top,
        # end is the green). Features are pushed through on top of that, so a
        # sparse last hole never clips off the canvas.
        content_min_y = min(content_min_y, h["start_y"] - 2, h["end_y"] - 2)
        content_max_y = max(content_max_y, h["start_y"] + 8, h["end_y"] + 8)
        content_min_x = min(content_min_x, h["start_x"] - 2, h["end_x"] - 2)
        content_max_x = max(content_max_x, h["start_x"] + 2, h["end_x"] + 2)
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
    if uniform:
        x_rescale = y_rescale = min(x_rescale, y_rescale)
        # Centre the content inside the box.
        draw_left = draw_left + (draw_width - content_width * x_rescale) / 2
        draw_top = draw_top + (draw_height - content_height * y_rescale) / 2

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


def _enforce_green_tee_gap(holes, min_gap: float = 2):
    """Ensure the next hole's tee sits strictly below the previous hole's
    green. Uses the spine end_y as a floor (covers holes with no tagged
    green polygon) and picks up tee polygons that extend above start_y."""
    if len(holes) < 2:
        return

    for i in range(1, len(holes)):
        prev = holes[i - 1]
        curr = holes[i]

        # Prev green bottom: spine end_y as floor, then push past any green
        # or rough polygon (rough tends to wrap the green).
        prev_green_bottom = prev["end_y"]
        for f in prev["features"]:
            if f.get("category") in ("green", "rough"):
                for _, y in f["coords"]:
                    prev_green_bottom = max(prev_green_bottom, y)

        # Curr tee top: spine start_y as ceiling, then pull up past any tee
        # polygon point.
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


def _fix_overlaps(holes, min_gap: float = 5):
    """Shift subsequent holes down to eliminate vertical overlap."""
    if len(holes) < 2:
        return

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


def _pack_holes(holes, target_gap: float = 5):
    """Pack holes tight by removing excess vertical gaps.

    Uses end_y as a floor for prev_bottom so that a hole with no green
    polygon still counts its spine terminus (= logical green position);
    otherwise packing can pull the next hole's tee above the previous
    hole's green.
    """
    if len(holes) < 2:
        return

    for i in range(1, len(holes)):
        prev = holes[i - 1]
        curr = holes[i]

        prev_bottom = max(prev["end_y"], prev["start_y"] + 14)
        for f in prev["features"]:
            for _, y in f["coords"]:
                prev_bottom = max(prev_bottom, y)

        curr_top = min(curr["start_y"] - 2, curr["end_y"])
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
        # Same y convention as the feature loop above (canvas y grows south).
        # With the sign flipped, a diagonal route looked far off-axis and the
        # width clamp shrank every feature on the hole.
        dy = -(lat - geo_tee[0])
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
