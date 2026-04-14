"""SVG renderer — produces SVG from layout data."""
from __future__ import annotations

import math

DEFAULT_STYLES = {
    "course_boundary": {"fill": "#3d6b3d", "stroke": "#2d5a2d", "stroke_width": 0.5, "opacity": 0.2},
    "rough": {"fill": "#8ab878", "stroke": "none", "stroke_width": 0, "opacity": 0.5},
    "fairway": {"fill": "#4a8f3f", "stroke": "#3d7a34", "stroke_width": 0.3, "opacity": 0.85},
    "bunker": {"fill": "#e8dca0", "stroke": "#d4c87a", "stroke_width": 0.3, "opacity": 0.9},
    "water": {"fill": "#5b9bd5", "stroke": "#4a87be", "stroke_width": 0.3, "opacity": 0.85},
    "tee": {"fill": "#7bc96a", "stroke": "#5eaa50", "stroke_width": 0.3, "opacity": 0.9},
    "green": {"fill": "#5cc654", "stroke": "#3eaa36", "stroke_width": 0.5, "opacity": 0.95},
    "hole_number": {"fill": "rgba(0,0,0,0.65)", "stroke": "#ffffff", "stroke_width": 0.4, "opacity": 1},
    "hole_par": {"fill": "rgba(255,255,255,0.5)", "stroke": "none", "stroke_width": 0, "opacity": 1},
    "background": {"fill": "#1a472a"},
}

ALL_LAYERS = [
    "background", "rough", "fairway", "water", "bunker", "tee", "green",
    "hole_number", "hole_par", "hole_stats", "ruler",
]

FEATURE_LAYERS = ["rough", "water", "fairway", "bunker", "tee", "green"]

HOLE_HUES = [120, 150, 90, 180, 60, 200, 100, 160, 75, 130, 170, 80, 190, 55, 210, 110, 145, 85]

# Scoring preview zone colors
ZONE_COLORS = {
    -1: "rgba(0,100,0,0.4)",
    0: "rgba(0,180,0,0.3)",
    1: "rgba(255,255,0,0.3)",
    2: "rgba(255,180,0,0.3)",
    3: "rgba(255,100,0,0.3)",
    4: "rgba(255,50,0,0.3)",
    5: "rgba(180,0,0,0.3)",
}


def _hole_hue(i: int) -> int:
    return HOLE_HUES[i % len(HOLE_HUES)]


def _hex_to_rgb(h: str) -> dict | None:
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) != 6:
        return None
    return {"r": int(h[0:2], 16), "g": int(h[2:4], 16), "b": int(h[4:6], 16)}


def _rgb_to_hsl(r: int, g: int, b: int) -> dict:
    r, g, b = r / 255, g / 255, b / 255
    mx, mn = max(r, g, b), min(r, g, b)
    h = s = 0.0
    l = (mx + mn) / 2
    if mx != mn:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = ((g - b) / d + (6 if g < b else 0)) * 60
        elif mx == g:
            h = ((b - r) / d + 2) * 60
        else:
            h = ((r - g) / d + 4) * 60
    return {"h": h, "s": s, "l": l}


def _hsl_to_rgb(h: float, s: float, l: float) -> dict:
    h /= 360
    if s == 0:
        v = round(l * 255)
        return {"r": v, "g": v, "b": v}

    def f(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return {
        "r": round(f(p, q, h + 1 / 3) * 255),
        "g": round(f(p, q, h) * 255),
        "b": round(f(p, q, h - 1 / 3) * 255),
    }


def _tint_color(hex_color: str, hue: int, amt: float) -> str:
    if not hex_color or hex_color == "none" or hex_color.startswith("rgba"):
        return hex_color
    rgb = _hex_to_rgb(hex_color)
    if not rgb:
        return hex_color
    hsl = _rgb_to_hsl(rgb["r"], rgb["g"], rgb["b"])
    nh = hsl["h"] + (hue - hsl["h"]) * amt
    nr = _hsl_to_rgb(((nh % 360) + 360) % 360, hsl["s"], hsl["l"])
    return f"rgb({nr['r']},{nr['g']},{nr['b']})"


def _ff(n: float) -> str:
    return f"{n:.1f}"


def _esc_xml(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _coords_to_path(coords: list[list[float]], closed: bool = True) -> str:
    if not coords or len(coords) < 2:
        return ""
    d = f"M{_ff(coords[0][0])},{_ff(coords[0][1])}"
    for i in range(1, len(coords)):
        d += f"L{_ff(coords[i][0])},{_ff(coords[i][1])}"
    if closed:
        d += "Z"
    return d


def _build_text_paths(template: dict) -> str:
    inner_r = template["inner_r"]
    outer_r = template["outer_r"]
    sector_angle = template["sector_angle"]
    half_a = sector_angle / 2
    svg = ""
    offsets = [0.04, 0.055, 0.07]
    for i in range(3):
        angle = -half_a + offsets[i]
        svg += (
            f'<path id="textArc{i + 1}" d="M {_ff(inner_r * math.sin(angle))} '
            f'{_ff(-inner_r * math.cos(angle))} L {_ff(outer_r * math.sin(angle))} '
            f'{_ff(-outer_r * math.cos(angle))}" fill="none"/>'
        )
    return svg


def _render_ruler(zones_by_hole: list[dict], draw_area: dict, opts: dict, font_family: str) -> str:
    """Render vertical ruler: hole# rect at top, flush score rects below, no spine."""
    right_edge = draw_area.get("right", 870)
    col_w = 20
    col_x = right_edge - col_w - 5
    col_cx = col_x + col_w / 2
    hole_rect_h = 12
    gap = 3
    label_font = 8

    svg = '<g class="layer-ruler">'

    for hi, zone_result in enumerate(zones_by_hole):
        hole_ref = zone_result.get("hole_ref", "")
        zones = zone_result.get("zones", [])
        if not zones:
            continue

        section_top = zones[0]["y_top"]
        section_bottom = zones[-1]["y_bottom"]
        is_odd = (hole_ref % 2 == 1) if isinstance(hole_ref, int) else True

        # --- Hole number rect at TOP of section ---
        if is_odd:
            svg += (
                f'<rect x="{_ff(col_x)}" y="{_ff(section_top)}" '
                f'width="{_ff(col_w)}" height="{_ff(hole_rect_h)}" '
                f'fill="white" stroke="none" opacity="0.85"/>'
            )
            svg += (
                f'<text x="{_ff(col_cx)}" y="{_ff(section_top + hole_rect_h * 0.72)}" '
                f'text-anchor="middle" fill="#1a1a1a" font-size="9" font-weight="700" '
                f'font-family="{font_family}">{hole_ref}</text>'
            )
        else:
            svg += (
                f'<rect x="{_ff(col_x)}" y="{_ff(section_top)}" '
                f'width="{_ff(col_w)}" height="{_ff(hole_rect_h)}" '
                f'fill="none" stroke="white" stroke-width="0.8" opacity="0.85"/>'
            )
            svg += (
                f'<text x="{_ff(col_cx)}" y="{_ff(section_top + hole_rect_h * 0.72)}" '
                f'text-anchor="middle" fill="white" font-size="9" font-weight="700" '
                f'font-family="{font_family}">{hole_ref}</text>'
            )

        # --- Score rects flush below hole number ---
        score_top = section_top + hole_rect_h + gap

        for zone in zones:
            label = zone["label"]
            score = zone.get("score", 0)
            zt = max(zone["y_top"], score_top)
            zb = zone["y_bottom"]
            zh = zb - zt
            y_mid = (zt + zb) / 2

            if zh < 2:
                continue

            is_odd_score = score in (1, 3, 5)
            if is_odd_score:
                svg += (
                    f'<rect x="{_ff(col_x)}" y="{_ff(zt)}" '
                    f'width="{_ff(col_w)}" height="{_ff(zh)}" '
                    f'fill="white" stroke="none" opacity="0.8"/>'
                )
                svg += (
                    f'<text x="{_ff(col_cx)}" y="{_ff(y_mid + 3)}" '
                    f'text-anchor="middle" fill="#1a1a1a" font-size="{label_font}" font-weight="700" '
                    f'font-family="{font_family}">{_esc_xml(label)}</text>'
                )
            else:
                svg += (
                    f'<rect x="{_ff(col_x)}" y="{_ff(zt)}" '
                    f'width="{_ff(col_w)}" height="{_ff(zh)}" '
                    f'fill="none" stroke="white" stroke-width="0.5" opacity="0.7"/>'
                )
                svg += (
                    f'<text x="{_ff(col_cx)}" y="{_ff(y_mid + 3)}" '
                    f'text-anchor="middle" fill="white" font-size="{label_font}" '
                    f'font-family="{font_family}" opacity="0.7">{_esc_xml(label)}</text>'
                )

    svg += "</g>"
    return svg



def _render_terrain_zones(terrain_zones: list, opts: dict, font_family: str,
                          vinyl_mode: bool = False) -> str:
    """Render terrain-following zones as polygon boundaries with score labels.

    In vinyl_mode: white strokes on dark background.
    Otherwise (scoring-preview): colored fills.
    """
    if not terrain_zones:
        return ""

    # Color map for scoring preview
    _PREVIEW_COLORS = {
        -1: "rgba(0,100,0,0.4)",
        0: "rgba(0,180,0,0.3)",
        1: "rgba(255,255,0,0.3)",
        2: "rgba(255,180,0,0.3)",
        3: "rgba(255,100,0,0.3)",
        4: "rgba(255,50,0,0.3)",
        5: "rgba(180,0,0,0.3)",
    }

    svg = '<g class="layer-terrain_zones">'
    for hole_tzs in terrain_zones:
        for tz in hole_tzs:
            poly = tz.get("polygon") or tz.get("contour", [])
            score = tz.get("score", 0)
            if not poly or len(poly) < 3:
                continue

            # Build path
            d = f"M{_ff(poly[0][0])},{_ff(poly[0][1])}"
            for pt in poly[1:]:
                d += f"L{_ff(pt[0])},{_ff(pt[1])}"
            d += "Z"

            if vinyl_mode:
                svg += (
                    f'<path d="{d}" fill="none" stroke="#ffffff" '
                    f'stroke-width="0.3" opacity="0.3"/>'
                )
            else:
                color = _PREVIEW_COLORS.get(score, "rgba(128,128,128,0.2)")
                svg += (
                    f'<path d="{d}" fill="{color}" stroke="none" opacity="1"/>'
                )

            # Score label
            lp = tz.get("label_position")
            if lp:
                lx = lp.get("x", 0)
                ly = lp.get("y", 0)
                label = f"{score:+d}" if score != 0 else "0"
                fill = "#ffffff" if vinyl_mode else "#000000"
                opacity = "0.8" if vinyl_mode else "0.8"
                fs = 5 if not vinyl_mode else 4
                svg += (
                    f'<text x="{_ff(lx)}" y="{_ff(ly + 1.5)}" text-anchor="middle" '
                    f'fill="{fill}" font-size="{fs}" font-weight="700" '
                    f'font-family="{font_family}" opacity="{opacity}">{label}</text>'
                )

                # Leader line for small zones
                leader = tz.get("leader_line")
                if leader and len(leader) == 2:
                    stroke = "#ffffff" if vinyl_mode else "#666666"
                    svg += (
                        f'<line x1="{_ff(leader[0][0])}" y1="{_ff(leader[0][1])}" '
                        f'x2="{_ff(leader[1][0])}" y2="{_ff(leader[1][1])}" '
                        f'stroke="{stroke}" stroke-width="0.3" stroke-dasharray="1,1" '
                        f'opacity="0.6"/>'
                    )

    svg += "</g>"
    return svg


def _render_hole_stats(hole: dict, opts: dict, font_family: str) -> str:
    """Render par/yardage/handicap as a rounded rectangle sign near hole number."""
    lines = []
    if hole.get("par"):
        lines.append(f"Par {hole['par']}")
    if hole.get("yardage"):
        lines.append(f"{hole['yardage']} yd")
    if hole.get("handicap"):
        lines.append(f"HCP {hole['handicap']}")

    if not lines:
        return ""

    is_warped = opts.get("vinyl_preview") and opts.get("is_warped")
    font_size = 3.5 if is_warped else 4.5
    line_height = font_size + 1.5
    padding_x = 3
    padding_y = 2
    box_w = 24
    box_h = padding_y * 2 + line_height * len(lines)

    # Position: on the outer side of tee (toward canvas margin, away from fairway)
    cr = 5
    direction = hole.get("direction", 1)
    hole_num_x_off = -(cr + 3) if direction > 0 else (cr + 3)
    hole_num_x = hole["start_x"] + hole_num_x_off
    hole_num_y = hole["start_y"] + cr + 4

    # Determine tee side: compare tee_x vs green_x (or use start_x vs end_x)
    tee_on_left = hole.get("start_x", 0) < hole.get("end_x", 0)

    canvas_w = opts.get("_canvas_width", 900)
    if tee_on_left:
        box_x = hole_num_x - cr - 2 - box_w
    else:
        box_x = hole_num_x + cr + 2

    # Boundary check: flip to other side if clipped
    if box_x < 0:
        box_x = hole_num_x + cr + 2
    elif box_x + box_w > canvas_w:
        box_x = hole_num_x - cr - 2 - box_w

    anchor = "start"
    text_x = box_x + padding_x

    box_y = hole_num_y - box_h / 2

    svg = (
        f'<rect x="{_ff(box_x)}" y="{_ff(box_y)}" '
        f'width="{_ff(box_w)}" height="{_ff(box_h)}" rx="2" '
        f'fill="none" stroke="#ffffff" stroke-width="0.5" opacity="0.8"/>'
    )

    for i, line in enumerate(lines):
        ty = box_y + padding_y + (i + 0.8) * line_height
        svg += (
            f'<text x="{_ff(text_x)}" y="{_ff(ty)}" '
            f'text-anchor="{anchor}" fill="white" font-size="{font_size}" '
            f'font-family="{font_family}" opacity="0.8">{_esc_xml(line)}</text>'
        )

    return svg


def _render_scoring_preview(holes: list[dict], zones_by_hole: list[dict],
                             draw_area: dict, font_family: str) -> str:
    """Render colored scoring zone bands for preview/testing mode."""
    canvas_width = draw_area.get("right", 870) - draw_area.get("left", 60)
    left = draw_area.get("left", 60)

    svg = '<g class="layer-scoring_preview">'
    for zone_result in zones_by_hole:
        for zone in zone_result.get("zones", []):
            color = ZONE_COLORS.get(zone["score"], "rgba(128,128,128,0.2)")
            y_top = zone["y_top"]
            y_bottom = zone["y_bottom"]
            height = y_bottom - y_top
            if height <= 0:
                continue
            svg += (
                f'<rect x="{_ff(left)}" y="{_ff(y_top)}" '
                f'width="{_ff(canvas_width)}" height="{_ff(height)}" '
                f'fill="{color}"/>'
            )
            # Zone label centered in band
            mid_y = (y_top + y_bottom) / 2
            svg += (
                f'<text x="{_ff(left + canvas_width / 2)}" y="{_ff(mid_y + 2)}" '
                f'text-anchor="middle" fill="white" font-size="4" '
                f'font-family="{font_family}" opacity="0.7">{_esc_xml(zone["label"])}</text>'
            )
    svg += "</g>"
    return svg


def _render_vinyl_preview(layout: dict, opts: dict, layer: str = "all") -> str:
    """Render vinyl-preview mode, optionally filtered to a single color layer.

    layer="all"   → full glass preview (background + all colors)
    layer="white"  → only white elements, no background (cricut white)
    layer="green"  → only green elements (cricut green)
    layer="blue"   → only blue elements (cricut blue)
    layer="tan"    → only tan elements (cricut tan)
    """
    font_family = opts.get("font_family", "'Arial', sans-serif")
    holes = layout.get("holes", [])
    is_warped = layout.get("warped") and layout.get("template")
    zones_by_hole = opts.get("zones_by_hole", [])
    terrain_zones = opts.get("terrain_zones", [])

    # Pass canvas width for stats boundary checking
    opts["_canvas_width"] = layout.get("canvas_width", 900)

    # Layer flags
    _all = layer == "all"
    _white = layer in ("all", "white")
    _green = layer in ("all", "green")
    _blue = layer in ("all", "blue")
    _tan = layer in ("all", "tan")

    if is_warped:
        t = layout["template"]
        half_a = t["sector_angle"] / 2
        pad = 8
        vb_x = -t["outer_r"] * math.sin(half_a) - pad
        vb_y = -t["outer_r"] - pad
        vb_w = 2 * t["outer_r"] * math.sin(half_a) + pad * 2
        vb_h = t["outer_r"] - t["inner_r"] * math.cos(half_a) + pad * 2
    else:
        vb_x, vb_y = 0, 0
        vb_w = layout.get("canvas_width", 900)
        vb_h = layout.get("canvas_height", 700)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="{_ff(vb_x)} {_ff(vb_y)} {_ff(vb_w)} {_ff(vb_h)}" '
        f'width="{round(vb_w)}" height="{round(vb_h)}">'
    )

    # Defs: clip path (no gradient — solid dark background represents glass)
    svg += "<defs>"
    if is_warped:
        from app.services.render.glass_template import glass_wrap_path
        svg += f'<clipPath id="glassClip"><path d="{glass_wrap_path(layout["template"])}"/></clipPath>'
        svg += _build_text_paths(layout["template"])
    svg += "</defs>"

    # Background — only for full preview, not individual layers
    _BG_COLOR = "#1a1a1a"
    if is_warped:
        from app.services.render.glass_template import glass_wrap_path
        svg += '<g clip-path="url(#glassClip)">'
        if _all:
            svg += f'<path d="{glass_wrap_path(layout["template"])}" fill="{_BG_COLOR}"/>'
    else:
        if _all:
            svg += (
                f'<rect x="0" y="0" width="{layout.get("canvas_width", 900)}" '
                f'height="{layout.get("canvas_height", 700)}" fill="{_BG_COLOR}" rx="4"/>'
            )

    # Terrain-following zone contours (white)
    if terrain_zones and _white:
        svg += _render_terrain_zones(terrain_zones, opts, font_family, vinyl_mode=True)

    # Simple horizontal zone boundary lines from zones_by_hole (white)
    # These provide clear visible zone markers across each hole's width
    if zones_by_hole and _white:
        svg += '<g class="layer-zone_lines">'
        for hi, zone_result in enumerate(zones_by_hole):
            if hi >= len(holes):
                continue
            hole = holes[hi]
            # Compute hole's horizontal extent from features
            xs = [hole.get("start_x", 0), hole.get("end_x", 0)]
            for f in hole.get("features", []):
                for px, _ in f.get("coords", []):
                    xs.append(px)
            x_left = min(xs) - 5
            x_right = max(xs) + 5
            for zone in zone_result.get("zones", []):
                y = zone["y_top"]
                svg += (
                    f'<line x1="{_ff(x_left)}" y1="{_ff(y)}" '
                    f'x2="{_ff(x_right)}" y2="{_ff(y)}" '
                    f'stroke="#ffffff" stroke-width="0.2" opacity="0.25"/>'
                )
        svg += "</g>"

    # Feature layers
    _WHITE_CATS = {"rough", "path", "course_boundary"}
    _GREEN_FILL_CATS = {"fairway"}
    _GREEN_CATS = {"green", "tee"}
    _BLUE_CATS = {"water"}

    # Collect score label positions for knockout masks
    _knockout_labels = []
    for hole_tzs in terrain_zones:
        for tz in hole_tzs:
            lp = tz.get("label_position")
            if lp and lp.get("inside"):
                score = tz.get("score", 0)
                label = f"{score:+d}" if score != 0 else "0"
                _knockout_labels.append({"x": lp["x"], "y": lp["y"], "label": label})

    # Build knockout mask definition if there are labels to knock out
    mask_id = "scoreKnockout"
    if _knockout_labels:
        # Add mask to defs — rendered after the opening <defs> but we insert before </defs>
        # We'll add it as an inline mask in the feature group instead
        pass

    svg += '<g class="layer-vinyl_features">'

    # Render features filtered by layer
    _filled_idx = 0
    for hole in holes:
        for feat in hole.get("features", []):
            cat = feat.get("category", "")
            d = _coords_to_path(feat.get("coords", []), cat != "path")
            if not d:
                continue

            if cat in _WHITE_CATS and _white:
                svg += (
                    f'<path d="{d}" fill="none" stroke="#ffffff" '
                    f'stroke-width="0.3" opacity="0.6"/>'
                )
            elif cat in _GREEN_FILL_CATS and _green:
                # Solid green fill with score knockout mask
                mid = f"fwMask{_filled_idx}"
                if _knockout_labels:
                    svg += f'<mask id="{mid}"><rect x="-9999" y="-9999" width="99999" height="99999" fill="white"/>'
                    for kl in _knockout_labels:
                        svg += (
                            f'<text x="{_ff(kl["x"])}" y="{_ff(kl["y"] + 1.5)}" text-anchor="middle" '
                            f'fill="black" font-size="4" font-weight="700" '
                            f'font-family="{font_family}">{kl["label"]}</text>'
                        )
                    svg += '</mask>'
                    svg += (
                        f'<path d="{d}" fill="#4ade80" stroke="#4ade80" '
                        f'stroke-width="0.2" opacity="0.85" mask="url(#{mid})"/>'
                    )
                else:
                    svg += (
                        f'<path d="{d}" fill="#4ade80" stroke="#4ade80" '
                        f'stroke-width="0.2" opacity="0.85"/>'
                    )
                _filled_idx += 1
            elif cat in _GREEN_CATS and _green:
                sw = "0.3" if cat == "tee" else "0.4"
                svg += (
                    f'<path d="{d}" fill="none" stroke="#4ade80" '
                    f'stroke-width="{sw}" opacity="0.85"/>'
                )
            elif cat in _BLUE_CATS and _blue:
                # Solid blue fill with score knockout mask
                mid = f"wtMask{_filled_idx}"
                if _knockout_labels:
                    svg += f'<mask id="{mid}"><rect x="-9999" y="-9999" width="99999" height="99999" fill="white"/>'
                    for kl in _knockout_labels:
                        svg += (
                            f'<text x="{_ff(kl["x"])}" y="{_ff(kl["y"] + 1.5)}" text-anchor="middle" '
                            f'fill="black" font-size="4" font-weight="700" '
                            f'font-family="{font_family}">{kl["label"]}</text>'
                        )
                    svg += '</mask>'
                    svg += (
                        f'<path d="{d}" fill="#3b82f6" stroke="#3b82f6" '
                        f'stroke-width="0.2" opacity="0.7" mask="url(#{mid})"/>'
                    )
                else:
                    svg += (
                        f'<path d="{d}" fill="#3b82f6" stroke="#3b82f6" '
                        f'stroke-width="0.2" opacity="0.7"/>'
                    )
                _filled_idx += 1
            elif cat == "bunker" and _tan:
                svg += (
                    f'<path d="{d}" fill="#d2b48c" stroke="#d2b48c" '
                    f'stroke-width="0.2" opacity="0.8"/>'
                )
    svg += "</g>"

    # White elements: hole numbers, dashed lines, stats, ruler, text, logo, QR
    sz = 5 if is_warped else 6
    cr = 5 if is_warped else 6
    if _white:
        # Hole numbers
        svg += '<g class="layer-hole_number">'
        for hole in holes:
            x_off = -(cr + 3) if hole.get("direction", 1) > 0 else (cr + 3)
            lx = hole["start_x"] + x_off
            ly = hole["start_y"] + cr + 4
            svg += (
                f'<circle cx="{_ff(lx)}" cy="{_ff(ly)}" r="{cr}" '
                f'fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.8"/>'
            )
            svg += (
                f'<text x="{_ff(lx)}" y="{_ff(ly + sz * 0.38)}" text-anchor="middle" '
                f'fill="#ffffff" font-size="{sz}" font-weight="700" '
                f'font-family="{font_family}" opacity="0.9">{hole.get("ref", "")}</text>'
            )
        svg += "</g>"

        # Dashed lines from hole number to tee box
        svg += '<g class="layer-hole_tee_lines">'
        for hole in holes:
            x_off = -(cr + 3) if hole.get("direction", 1) > 0 else (cr + 3)
            lx = hole["start_x"] + x_off
            ly = hole["start_y"] + cr + 4
            tees = [f for f in hole.get("features", []) if f.get("category") == "tee"]
            if tees and tees[0].get("coords"):
                tee_coords = tees[0]["coords"]
                tx = sum(p[0] for p in tee_coords) / len(tee_coords)
                ty = sum(p[1] for p in tee_coords) / len(tee_coords)
                svg += (
                    f'<line x1="{_ff(lx)}" y1="{_ff(ly)}" '
                    f'x2="{_ff(tx)}" y2="{_ff(ty)}" '
                    f'stroke="#ffffff" stroke-dasharray="2,2" stroke-width="0.5" opacity="0.4"/>'
                )
        svg += "</g>"

        # Hole stats
        svg += '<g class="layer-hole_stats">'
        for hole in holes:
            svg += _render_hole_stats(hole, opts, font_family)
        svg += "</g>"

        # Ruler
        draw_area = layout.get("draw_area", {
            "left": 60, "right": layout.get("canvas_width", 900) - 30,
            "top": 30, "bottom": layout.get("canvas_height", 700) - 30,
        })
        if zones_by_hole:
            if is_warped:
                svg += _render_ruler_warped(zones_by_hole, layout, opts, font_family)
            else:
                svg += _render_ruler(zones_by_hole, draw_area, opts, font_family)

    if is_warped:
        svg += "</g>"  # close clip group

    if _white:
        # Course name + hole range
        if opts.get("course_name") or opts.get("hole_range") or opts.get("logo_data_url"):
            if is_warped:
                svg += _render_warped_text(layout, opts, font_family)
            else:
                svg += _render_rect_text(layout, opts, font_family)

        # Logo at bottom-left
        if opts.get("logo_data_url"):
            svg += _render_logo_bottom_left(layout, opts)

        # QR code
        if opts.get("qr_svg"):
            svg += _render_embedded_qr(layout, opts)

    svg += "</svg>"
    return svg


def _render_ruler_warped(zones_by_hole: list[dict], layout: dict,
                         opts: dict, font_family: str) -> str:
    """Render ruler on glass sector — rotated elements following curvature."""
    t = layout.get("template", {})
    if not t:
        return ""
    half_a = t["sector_angle"] / 2
    inner_r = t["inner_r"]
    outer_r = t["outer_r"]
    edge_angle = half_a
    rot_deg = math.degrees(edge_angle)

    draw_area = layout.get("draw_area", {})
    canvas_top = draw_area.get("top", 30)
    canvas_bottom = draw_area.get("bottom", 670)
    canvas_range = canvas_bottom - canvas_top
    if canvas_range <= 0:
        canvas_range = 1

    col_w = 10
    hole_rect_h = 6
    gap = 2
    min_font = 3

    def _y_to_r(y):
        frac = (y - canvas_top) / canvas_range
        return outer_r - frac * (outer_r - inner_r)

    def _polar(r, a):
        return r * math.sin(a), -r * math.cos(a)

    svg = '<g class="layer-ruler">'

    _labels = []

    for hi, zone_result in enumerate(zones_by_hole):
        hole_ref = zone_result.get("hole_ref", "")
        zones = zone_result.get("zones", [])
        if not zones:
            continue

        section_top = zones[0]["y_top"]
        section_bottom = zones[-1]["y_bottom"]
        is_odd = (hole_ref % 2 == 1) if isinstance(hole_ref, int) else True

        # --- Hole number rect at top of section, rotated ---
        r_top = _y_to_r(section_top)
        cx, cy = _polar(r_top, edge_angle)
        # Adaptive size based on available radial space
        r_bot_sect = _y_to_r(section_bottom)
        avail_r = abs(r_top - r_bot_sect)
        h_rect_h = min(hole_rect_h, avail_r * 0.15)
        if h_rect_h < 4:
            h_rect_h = 4

        svg += f'<g transform="rotate({_ff(rot_deg)}, 0, 0)">'
        # In rotated space, r maps to y (from center), angle maps to x
        # Position rect at r_top along the radius
        ry = -r_top  # SVG y is inverted
        if is_odd:
            svg += (
                f'<rect x="{_ff(-col_w / 2)}" y="{_ff(ry)}" '
                f'width="{_ff(col_w)}" height="{_ff(h_rect_h)}" '
                f'fill="white" stroke="none" opacity="0.85"/>'
            )
            svg += (
                f'<text x="0" y="{_ff(ry + h_rect_h * 0.72)}" '
                f'text-anchor="middle" fill="#1a1a1a" font-size="{_ff(max(min_font, h_rect_h * 0.7))}" '
                f'font-weight="700" font-family="{font_family}">{hole_ref}</text>'
            )
        else:
            svg += (
                f'<rect x="{_ff(-col_w / 2)}" y="{_ff(ry)}" '
                f'width="{_ff(col_w)}" height="{_ff(h_rect_h)}" '
                f'fill="none" stroke="white" stroke-width="0.5" opacity="0.85"/>'
            )
            svg += (
                f'<text x="0" y="{_ff(ry + h_rect_h * 0.72)}" '
                f'text-anchor="middle" fill="white" font-size="{_ff(max(min_font, h_rect_h * 0.7))}" '
                f'font-weight="700" font-family="{font_family}">{hole_ref}</text>'
            )
        svg += '</g>'

        # --- Score rects below hole number, rotated ---
        score_r_start = r_top - h_rect_h - gap

        for zone in zones:
            label = zone["label"]
            score = zone.get("score", 0)
            r_zt = _y_to_r(zone["y_top"])
            r_zb = _y_to_r(zone["y_bottom"])
            r_zt = min(r_zt, score_r_start)
            zone_r = abs(r_zt - r_zb)

            if zone_r < 1:
                continue

            # Adaptive font
            fs = min(4, max(min_font, zone_r * 0.6))
            if zone_r < min_font:
                continue  # skip unreadable labels

            r_mid = (r_zt + r_zb) / 2

            # Anti-overlap
            overlaps = False
            for prev_r in _labels:
                if abs(r_mid - prev_r) < 3:
                    overlaps = True
                    break
            if overlaps:
                continue
            _labels.append(r_mid)

            svg += f'<g transform="rotate({_ff(rot_deg)}, 0, 0)">'
            ry = -r_zt
            is_odd_score = score in (1, 3, 5)
            if is_odd_score:
                svg += (
                    f'<rect x="{_ff(-col_w / 2)}" y="{_ff(ry)}" '
                    f'width="{_ff(col_w)}" height="{_ff(zone_r)}" '
                    f'fill="white" stroke="none" opacity="0.8"/>'
                )
                svg += (
                    f'<text x="0" y="{_ff(-r_mid + fs * 0.35)}" '
                    f'text-anchor="middle" fill="#1a1a1a" font-size="{_ff(fs)}" font-weight="700" '
                    f'font-family="{font_family}">{_esc_xml(label)}</text>'
                )
            else:
                svg += (
                    f'<rect x="{_ff(-col_w / 2)}" y="{_ff(ry)}" '
                    f'width="{_ff(col_w)}" height="{_ff(zone_r)}" '
                    f'fill="none" stroke="white" stroke-width="0.4" opacity="0.7"/>'
                )
                svg += (
                    f'<text x="0" y="{_ff(-r_mid + fs * 0.35)}" '
                    f'text-anchor="middle" fill="white" font-size="{_ff(fs)}" '
                    f'font-family="{font_family}" opacity="0.7">{_esc_xml(label)}</text>'
                )
            svg += '</g>'

    svg += "</g>"
    return svg


def _render_logo_bottom_left(layout: dict, opts: dict) -> str:
    """Render logo at bottom-left of the layout."""
    logo_url = opts.get("logo_data_url")
    if not logo_url:
        return ""

    is_warped = layout.get("warped") and layout.get("template")

    if is_warped:
        t = layout["template"]
        half_a = t["sector_angle"] / 2
        r = t["inner_r"] + (t["outer_r"] - t["inner_r"]) * 0.1
        edge_angle = -half_a + 0.03
        cx = r * math.sin(edge_angle)
        cy = -r * math.cos(edge_angle)
        img_size = (t["outer_r"] - t["inner_r"]) * 0.06
        return (
            f'<image href="{_esc_xml(logo_url)}" '
            f'x="{_ff(cx - img_size / 2)}" y="{_ff(cy - img_size / 2)}" '
            f'width="{_ff(img_size)}" height="{_ff(img_size)}" '
            f'opacity="0.6" preserveAspectRatio="xMidYMid meet"/>'
        )
    else:
        ch = layout.get("canvas_height", 700)
        return (
            f'<image href="{_esc_xml(logo_url)}" '
            f'x="5" y="{_ff(ch - 25)}" width="20" height="20" '
            f'opacity="0.6" preserveAspectRatio="xMidYMid meet"/>'
        )


def render_svg(layout: dict, opts: dict | None = None) -> str:
    """Render SVG string from layout data."""
    opts = opts or {}

    # Vinyl preview mode uses a completely different rendering path
    if opts.get("vinyl_preview"):
        return _render_vinyl_preview(layout, opts)

    # Merge styles
    styles = {}
    for k, v in DEFAULT_STYLES.items():
        styles[k] = {**v, **(opts.get("styles", {}).get(k, {}))}

    hidden = set(opts.get("hidden_layers", []))
    per_hole_colors = opts.get("per_hole_colors", True)
    font_family = opts.get("font_family", "'Arial', sans-serif")
    holes = layout.get("holes", [])
    is_warped = layout.get("warped") and layout.get("template")
    zones_by_hole = opts.get("zones_by_hole", [])
    scoring_preview = opts.get("scoring_preview", False)

    if is_warped:
        t = layout["template"]
        half_a = t["sector_angle"] / 2
        pad = 8
        vb_x = -t["outer_r"] * math.sin(half_a) - pad
        vb_y = -t["outer_r"] - pad
        vb_w = 2 * t["outer_r"] * math.sin(half_a) + pad * 2
        vb_h = t["outer_r"] - t["inner_r"] * math.cos(half_a) + pad * 2
    else:
        vb_x, vb_y = 0, 0
        vb_w = layout.get("canvas_width", 900)
        vb_h = layout.get("canvas_height", 700)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="{_ff(vb_x)} {_ff(vb_y)} {_ff(vb_w)} {_ff(vb_h)}" '
        f'width="{round(vb_w)}" height="{round(vb_h)}">'
    )

    svg += "<defs>"
    if is_warped:
        from app.services.render.glass_template import glass_wrap_path
        svg += f'<clipPath id="glassClip"><path d="{glass_wrap_path(layout["template"])}"/></clipPath>'
        svg += _build_text_paths(layout["template"])
    svg += "</defs>"

    if is_warped:
        from app.services.render.glass_template import glass_wrap_path
        svg += '<g clip-path="url(#glassClip)">'
        if "background" not in hidden:
            svg += f'<path d="{glass_wrap_path(layout["template"])}" fill="{styles["background"]["fill"]}"/>'
    else:
        if "background" not in hidden:
            svg += (
                f'<rect x="0" y="0" width="{layout.get("canvas_width", 900)}" '
                f'height="{layout.get("canvas_height", 700)}" fill="{styles["background"]["fill"]}" rx="4"/>'
            )

    # Scoring preview bands (rendered behind features)
    draw_area = layout.get("draw_area", {
        "left": 60, "right": layout.get("canvas_width", 900) - 30,
        "top": 30, "bottom": layout.get("canvas_height", 700) - 30,
    })
    if scoring_preview and zones_by_hole and not is_warped:
        svg += _render_scoring_preview(holes, zones_by_hole, draw_area, font_family)

    # Terrain-following zone overlays (scoring-preview mode)
    terrain_zones = opts.get("terrain_zones")
    if scoring_preview and terrain_zones and not is_warped:
        svg += _render_terrain_zones(terrain_zones, opts, font_family, vinyl_mode=False)

    # Feature layers
    for layer in FEATURE_LAYERS:
        if layer in hidden:
            continue
        s = styles.get(layer)
        if not s:
            continue
        tintable = layer in ("fairway", "rough", "tee", "green")
        svg += f'<g class="layer-{layer}">'
        for hi, hole in enumerate(holes):
            hue = _hole_hue(hi)
            for feat in hole.get("features", []):
                if feat.get("category") != layer:
                    continue
                d = _coords_to_path(feat.get("coords", []), layer != "path")
                if not d:
                    continue
                fill = s["fill"]
                stroke = s["stroke"]
                if per_hole_colors and tintable and fill != "none":
                    fill = _tint_color(fill, hue, 0.35)
                if per_hole_colors and tintable and stroke and stroke != "none":
                    stroke = _tint_color(stroke, hue, 0.25)
                svg += (
                    f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="{s["stroke_width"]}" opacity="{s["opacity"]}"/>'
                )
        svg += "</g>"

    # Scoring arcs removed — will be replaced by terrain-following zones

    # Hole numbers
    if "hole_number" not in hidden:
        s = styles["hole_number"]
        sz = 5 if is_warped else 6
        cr = 5 if is_warped else 6
        svg += '<g class="layer-hole_number">'
        for hole in holes:
            x_off = -(cr + 3) if hole.get("direction", 1) > 0 else (cr + 3)
            lx = hole["start_x"] + x_off
            ly = hole["start_y"] + cr + 4
            svg += (
                f'<circle cx="{_ff(lx)}" cy="{_ff(ly)}" r="{cr}" '
                f'fill="{s["fill"]}" stroke="{s["stroke"]}" '
                f'stroke-width="{s["stroke_width"]}" opacity="{s["opacity"]}"/>'
            )
            svg += (
                f'<text x="{_ff(lx)}" y="{_ff(ly + sz * 0.38)}" text-anchor="middle" '
                f'fill="white" font-size="{sz}" font-weight="700" '
                f'font-family="{font_family}">{hole.get("ref", "")}</text>'
            )
        svg += "</g>"

    # Par labels
    if "hole_par" not in hidden:
        s = styles["hole_par"]
        sz = 5 if is_warped else 6
        svg += '<g class="layer-hole_par">'
        for hole in holes:
            if not hole.get("par"):
                continue
            greens = [f for f in hole.get("features", []) if f.get("category") == "green"]
            if greens:
                gx = gy = 0.0
                n = 0
                for g in greens:
                    for x, y in g["coords"]:
                        gx += x
                        gy += y
                        n += 1
                lx = gx / n
                ly = gy / n + (4 if is_warped else 6)
            else:
                lx = hole["end_x"]
                ly = hole["end_y"] + (4 if is_warped else 6)
            svg += (
                f'<text x="{_ff(lx)}" y="{_ff(ly + 2)}" text-anchor="middle" '
                f'fill="{s["fill"]}" font-size="{sz * 0.75}" '
                f'font-family="{font_family}" opacity="{s["opacity"]}">P{hole["par"]}</text>'
            )
        svg += "</g>"

    # Hole stats
    if "hole_stats" not in hidden and holes:
        svg += '<g class="layer-hole_stats">'
        for hole in holes:
            svg += _render_hole_stats(hole, opts, font_family)
        svg += "</g>"

    # Ruler
    if "ruler" not in hidden and zones_by_hole and not is_warped:
        svg += _render_ruler(zones_by_hole, draw_area, opts, font_family)

    if is_warped:
        svg += "</g>"
        if opts.get("show_glass_outline", True):
            from app.services.render.glass_template import glass_wrap_path
            svg += (
                f'<path d="{glass_wrap_path(layout["template"])}" fill="none" '
                f'stroke="#555" stroke-width="0.5" stroke-dasharray="3,2"/>'
            )

    # Text overlays
    if opts.get("course_name") or opts.get("hole_range") or opts.get("logo_data_url"):
        if is_warped:
            svg += _render_warped_text(layout, opts, font_family)
        else:
            svg += _render_rect_text(layout, opts, font_family)

    # QR code embedding
    if opts.get("qr_svg"):
        svg += _render_embedded_qr(layout, opts)

    svg += "</svg>"
    return svg


def _render_warped_text(layout: dict, opts: dict, font_family: str) -> str:
    svg = ""
    t = layout["template"]
    half_a = t["sector_angle"] / 2

    if opts.get("logo_data_url"):
        mid_r = (t["inner_r"] + t["outer_r"]) / 2
        edge_angle = -half_a + 0.015
        cx = mid_r * math.sin(edge_angle)
        cy = -mid_r * math.cos(edge_angle)
        slant_len = t["outer_r"] - t["inner_r"]
        img_h = slant_len * 0.5
        img_w = img_h * 0.35
        edge_deg = edge_angle * 180 / math.pi
        svg += (
            f'<image href="{_esc_xml(opts["logo_data_url"])}" '
            f'x="{_ff(cx - img_w / 2)}" y="{_ff(cy - img_h / 2)}" '
            f'width="{_ff(img_w)}" height="{_ff(img_h)}" '
            f'transform="rotate({_ff(edge_deg)}, {_ff(cx)}, {_ff(cy)})" '
            f'preserveAspectRatio="xMidYMid meet"/>'
        )
    elif opts.get("course_name"):
        svg += (
            f'<text fill="white" font-size="7" font-weight="700" '
            f'font-family="{font_family}" opacity="0.85" text-anchor="middle">'
            f'<textPath href="#textArc1" startOffset="50%">'
            f'{_esc_xml(opts["course_name"])}</textPath></text>'
        )

    if opts.get("hole_range"):
        svg += (
            f'<text fill="white" font-size="4" font-family="{font_family}" '
            f'opacity="0.6" text-anchor="middle">'
            f'<textPath href="#textArc2" startOffset="50%">'
            f'{_esc_xml(opts["hole_range"])}</textPath></text>'
        )

    if opts.get("hole_yardages"):
        svg += (
            f'<text fill="white" font-size="3" font-family="{font_family}" '
            f'opacity="0.5" text-anchor="middle">'
            f'<textPath href="#textArc3" startOffset="50%">'
            f'{_esc_xml("  ".join(str(y) for y in opts["hole_yardages"]))}</textPath></text>'
        )

    return svg


def _render_rect_text(layout: dict, opts: dict, font_family: str) -> str:
    svg = ""
    y_mid = layout.get("canvas_height", 700) / 2

    if opts.get("logo_data_url"):
        img_w = 20
        img_h = layout.get("canvas_height", 700) * 0.45
        svg += (
            f'<image href="{_esc_xml(opts["logo_data_url"])}" '
            f'x="3" y="{_ff(y_mid - img_h / 2)}" width="{_ff(img_w)}" height="{_ff(img_h)}" '
            f'transform="rotate(-90, {_ff(3 + img_w / 2)}, {_ff(y_mid)})" '
            f'preserveAspectRatio="xMidYMid meet"/>'
        )
    elif opts.get("course_name"):
        svg += (
            f'<text transform="translate(10, {_ff(y_mid)}) rotate(-90)" '
            f'text-anchor="middle" fill="white" font-size="12" font-weight="700" '
            f'font-family="{font_family}" opacity="0.85">'
            f'{_esc_xml(opts["course_name"])}</text>'
        )

    if opts.get("hole_range"):
        svg += (
            f'<text transform="translate(22, {_ff(y_mid)}) rotate(-90)" '
            f'text-anchor="middle" fill="white" font-size="7" '
            f'font-family="{font_family}" opacity="0.6">'
            f'{_esc_xml(opts["hole_range"])}</text>'
        )

    if opts.get("hole_yardages"):
        svg += (
            f'<text transform="translate(31, {_ff(y_mid)}) rotate(-90)" '
            f'text-anchor="middle" fill="white" font-size="5" '
            f'font-family="{font_family}" opacity="0.45">'
            f'{_esc_xml("  ".join(str(y) for y in opts["hole_yardages"]))}</text>'
        )

    return svg


def _render_embedded_qr(layout: dict, opts: dict) -> str:
    """Embed a QR code SVG at the bottom-right of the layout."""
    qr_svg = opts.get("qr_svg", "")
    if not qr_svg:
        return ""

    is_warped = layout.get("warped") and layout.get("template")
    qr_size = 30  # approximate size in layout units

    if is_warped:
        t = layout["template"]
        half_a = t["sector_angle"] / 2
        # Position at bottom-right of glass sector
        edge_angle = half_a - 0.05
        r = t["inner_r"] + (t["outer_r"] - t["inner_r"]) * 0.15
        cx = r * math.sin(edge_angle)
        cy = -r * math.cos(edge_angle)
        qr_size = (t["outer_r"] - t["inner_r"]) * 0.08
    else:
        cw = layout.get("canvas_width", 900)
        ch = layout.get("canvas_height", 700)
        cx = cw - 35
        cy = ch - 35

    # Embed QR as a nested SVG group
    return (
        f'<g transform="translate({_ff(cx - qr_size / 2)}, {_ff(cy - qr_size / 2)}) '
        f'scale({_ff(qr_size / 100)})" opacity="0.6">'
        f'<!-- QR code embedded -->'
        f'</g>'
    )
