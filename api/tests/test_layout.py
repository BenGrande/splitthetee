"""Tests for layout engine."""

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
