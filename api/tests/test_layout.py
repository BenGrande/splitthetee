"""Tests for layout engine."""

import math

from app.services.render.layout import (
    compute_layout,
    split_into_glasses,
    _simulate_zigzag,
    _fix_overlaps,
    _pack_holes,
    _enforce_slope,
)


def _make_hole(ref, par=4, yardage=400, difficulty=9):
    return {
        "ref": ref,
        "par": par,
        "yardage": yardage,
        "difficulty": difficulty,
        "handicap": None,
        "route_coords": [[36.0, -121.0], [36.001, -121.001]],
        "features": [
            {
                "id": f"way/{ref}0",
                "category": "fairway",
                "ref": None,
                "par": None,
                "name": None,
                "coords": [[36.0, -121.0], [36.0005, -121.0005]],
            },
            {
                "id": f"way/{ref}1",
                "category": "tee",
                "ref": None,
                "par": None,
                "name": None,
                "coords": [[36.0, -121.0], [36.0001, -121.0001]],
            },
            {
                "id": f"way/{ref}2",
                "category": "green",
                "ref": None,
                "par": None,
                "name": None,
                "coords": [[36.001, -121.001], [36.0011, -121.0011]],
            },
        ],
    }


class TestComputeLayout:
    def test_empty_holes(self):
        result = compute_layout([], {})
        assert result["holes"] == []
        assert result["canvas_width"] == 900
        assert result["canvas_height"] == 700

    def test_single_hole(self):
        holes = [_make_hole(1)]
        result = compute_layout(holes)
        assert len(result["holes"]) == 1
        h = result["holes"][0]
        assert h["ref"] == 1
        assert "start_x" in h
        assert "start_y" in h
        assert len(h["features"]) == 3

    def test_multiple_holes(self):
        holes = [_make_hole(i, yardage=350 + i * 10) for i in range(1, 4)]
        result = compute_layout(holes)
        assert len(result["holes"]) == 3
        # Holes should have increasing start_y (flowing down)
        for i in range(1, len(result["holes"])):
            assert result["holes"][i]["start_y"] > result["holes"][i - 1]["start_y"]

    def test_custom_canvas_size(self):
        holes = [_make_hole(1)]
        result = compute_layout(holes, {"canvas_width": 1200, "canvas_height": 800})
        assert result["canvas_width"] == 1200
        assert result["canvas_height"] == 800

    def test_draw_area_includes_ruler_margin(self):
        holes = [_make_hole(1)]
        result = compute_layout(holes, {"canvas_width": 900, "canvas_height": 700})
        da = result["draw_area"]
        # draw_right should be canvas_width - margin_x(20) - ruler_margin(50) = 830
        assert da["right"] == 900 - 20 - 50
        # draw_left should be text_margin(45) + stats_margin(5) = 50
        assert da["left"] == 45 + 5

    def test_custom_ruler_margin(self):
        holes = [_make_hole(1)]
        result = compute_layout(holes, {"canvas_width": 900, "ruler_margin": 80})
        assert result["draw_area"]["right"] == 900 - 20 - 80

    def test_difficulty_affects_angle(self):
        holes = [_make_hole(1, difficulty=1), _make_hole(2, difficulty=18)]
        result = compute_layout(holes)
        # Harder hole (lower difficulty) should have steeper angle (closer to 55)
        assert result["holes"][0]["angle_deg"] > result["holes"][1]["angle_deg"]


class TestSimulateZigzag:
    def test_basic(self):
        import math
        layouts = [
            {"hole": {"ref": i}, "angle_deg": 45, "angle_rad": math.pi / 4,
             "length_fraction": 0.33, "yardage": 400}
            for i in range(3)
        ]
        result = _simulate_zigzag(layouts, 0.02)
        assert len(result) == 3
        assert result[0]["start_y"] == 0.0


class TestFixOverlaps:
    def test_no_overlap(self):
        holes = [
            {"start_y": 0, "end_y": 50, "features": [{"coords": [[100, 10], [100, 40]]}]},
            {"start_y": 100, "end_y": 150, "features": [{"coords": [[100, 110], [100, 140]]}]},
        ]
        _fix_overlaps(holes)
        assert holes[1]["start_y"] == 100  # unchanged

    def test_shifts_overlapping(self):
        holes = [
            {"start_y": 0, "end_y": 50, "features": [{"coords": [[100, 45]]}]},
            {"start_y": 10, "end_y": 60, "features": [{"coords": [[100, 15]]}]},
        ]
        _fix_overlaps(holes)
        assert holes[1]["start_y"] > 10  # shifted down


class TestEnforceSlope:
    def test_shifts_green_down(self):
        holes = [{
            "start_y": 0,
            "end_y": 50,
            "features": [
                {"category": "tee", "coords": [[100, 20], [100, 30]]},
                {"category": "green", "coords": [[100, 25], [100, 28]]},  # too close
            ],
        }]
        _enforce_slope(holes)
        # Green should be shifted down
        green = holes[0]["features"][1]
        assert green["coords"][0][1] > 30


class TestSplitIntoGlasses:
    def test_single_glass(self):
        holes = list(range(9))
        assert split_into_glasses(holes, 1) == [holes]

    def test_two_glasses(self):
        holes = list(range(18))
        groups = split_into_glasses(holes, 2)
        assert len(groups) == 2
        assert len(groups[0]) == 9

    def test_six_glasses_18_holes(self):
        holes = list(range(18))
        groups = split_into_glasses(holes, 6)
        assert len(groups) == 6
        assert all(len(g) == 3 for g in groups)

    def test_small_group(self):
        holes = list(range(3))
        groups = split_into_glasses(holes, 3)
        assert len(groups) == 1  # n <= 3 returns single group


# ---------------------------------------------------------------------------
# Synthetic corridors + featured layout
# ---------------------------------------------------------------------------
from app.services.render.layout import (  # noqa: E402
    synthesize_missing_features,
    _route_coverage,
    _simulate_featured,
)


def _sparse_hole(ref, par=4, yardage=420, extra_features=None):
    """A hole mapped like many real courses: tee, green, bunker, no fairway."""
    # ~400 m dogleg running roughly south-west
    route = [[51.0300, -114.0000], [51.0280, -114.0015], [51.0268, -114.0030]]
    feats = [
        {"id": "t", "category": "tee", "ref": None, "par": None, "name": None,
         "coords": [[51.0301, -114.0001], [51.0301, -113.9999], [51.0300, -113.9999]]},
        {"id": "g", "category": "green", "ref": None, "par": None, "name": None,
         "coords": [[51.0269, -114.0031], [51.0269, -114.0029], [51.0267, -114.0029]]},
        {"id": "b", "category": "bunker", "ref": None, "par": None, "name": None,
         "coords": [[51.0271, -114.0028], [51.0271, -114.0027]]},
    ]
    return {"ref": ref, "par": par, "yardage": yardage, "difficulty": 5.0, "handicap": 5,
            "route_coords": route, "features": feats + (extra_features or [])}


class TestSynthesizeMissingFeatures:
    def test_adds_fairway_and_rough_when_missing(self):
        out = synthesize_missing_features(_sparse_hole(1))
        cats = [f["category"] for f in out["features"]]
        assert cats[:2] == ["rough", "fairway"]  # ground first, mapped features on top
        assert cats.count("fairway") == 1 and cats.count("rough") == 1
        fw = next(f for f in out["features"] if f["category"] == "fairway")
        assert fw["synthetic"] is True
        assert len(fw["coords"]) > 10
        assert fw["coords"][0] == fw["coords"][-1]  # closed ring

    def test_corridor_follows_route(self):
        hole = _sparse_hole(1)
        out = synthesize_missing_features(hole)
        fw = next(f for f in out["features"] if f["category"] == "fairway")
        mid_lat = 51.0284
        cos_lat = math.cos(math.radians(mid_lat))
        assert _route_coverage(fw["coords"], hole["route_coords"], cos_lat, max_dist_m=40) == 1.0

    def test_par3_is_narrower(self):
        def width(par):
            out = synthesize_missing_features(_sparse_hole(1, par=par))
            fw = next(f for f in out["features"] if f["category"] == "fairway")
            lons = [c[1] for c in fw["coords"]]
            return max(lons) - min(lons)
        assert width(3) < width(4) <= width(5)

    def test_real_fairway_is_kept_untouched(self):
        real = {"id": "f", "category": "fairway", "ref": None, "par": None, "name": None,
                "coords": [[51.0296, -114.0003], [51.0290, -114.0008], [51.0282, -114.0014],
                           [51.0275, -114.0022], [51.0272, -114.0026], [51.0296, -114.0003]]}
        hole = _sparse_hole(1, extra_features=[real])
        out = synthesize_missing_features(hole)
        assert out is hole

    def test_off_route_fairway_is_dropped_and_replaced(self):
        # A driving range 300 m east of the hole that got associated by proximity.
        junk = {"id": "range", "category": "fairway", "ref": None, "par": None, "name": None,
                "coords": [[51.0300, -113.9950], [51.0300, -113.9940], [51.0280, -113.9940],
                           [51.0280, -113.9950], [51.0300, -113.9950]]}
        out = synthesize_missing_features(_sparse_hole(1, extra_features=[junk]))
        fairways = [f for f in out["features"] if f["category"] == "fairway"]
        assert len(fairways) == 1 and fairways[0].get("synthetic") is True

    def test_no_route_returns_input(self):
        hole = _sparse_hole(1)
        hole["route_coords"] = []
        assert synthesize_missing_features(hole) is hole


class TestRouteCoverage:
    def test_points_on_route_are_covered(self):
        route = [[51.0, -114.0], [51.001, -114.0]]
        cos_lat = math.cos(math.radians(51.0))
        assert _route_coverage([[51.0005, -114.0]], route, cos_lat) == 1.0

    def test_far_points_are_not(self):
        route = [[51.0, -114.0], [51.001, -114.0]]
        cos_lat = math.cos(math.radians(51.0))
        assert _route_coverage([[51.0005, -114.01]], route, cos_lat) == 0.0


class TestFeaturedLayout:
    def test_alternates_direction_and_starts_at_edges(self):
        hl = [{"length_fraction": 0.2, "angle_rad": math.radians(20)} for _ in range(4)]
        pos = _simulate_featured(hl, 0.02)
        assert [p["direction"] for p in pos] == [1, -1, 1, -1]
        assert pos[0]["start_x"] == 0.06 and pos[1]["start_x"] == 0.94
        assert pos[0]["end_x"] > 0.9  # equal lengths -> full sweep
        assert all(pos[i]["start_y"] > pos[i - 1]["end_y"] for i in range(1, 4))

    def test_shorter_hole_sweeps_less(self):
        hl = [{"length_fraction": 0.3, "angle_rad": math.radians(20)},
              {"length_fraction": 0.1, "angle_rad": math.radians(20)}]
        pos = _simulate_featured(hl, 0.02)
        assert abs(pos[1]["end_x"] - pos[1]["start_x"]) < abs(pos[0]["end_x"] - pos[0]["start_x"])

    def test_compute_layout_featured_fills_width(self):
        holes = [_sparse_hole(i, par=p, yardage=y)
                 for i, (p, y) in enumerate([(4, 426), (3, 202), (4, 483), (3, 198), (5, 514)], 1)]
        lay = compute_layout(holes, {"featured_layout": True})
        draw = lay["draw_area"]
        width = draw["right"] - draw["left"]
        for h in lay["holes"]:
            xs = [c[0] for f in h["features"] for c in f["coords"]]
            # features (not just the spine) span at least half the draw width
            assert max(xs) - min(xs) > 0.5 * width
            assert all(f["category"] != "rough" or len(f["coords"]) > 10 for f in h["features"])

    def test_featured_ignored_for_many_holes(self):
        holes = [_sparse_hole(i) for i in range(1, 12)]
        a = compute_layout(holes, {"featured_layout": True})
        b = compute_layout(holes, {})
        assert [round(h["start_x"]) for h in a["holes"]] == [round(h["start_x"]) for h in b["holes"]]

    def test_synthesis_can_be_disabled(self):
        lay = compute_layout([_sparse_hole(1)], {"synthesize_fairways": False})
        cats = {f["category"] for f in lay["holes"][0]["features"]}
        assert "fairway" not in cats
