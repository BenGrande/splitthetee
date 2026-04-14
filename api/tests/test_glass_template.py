"""Tests for glass template."""

import math

from app.services.render.glass_template import (
    compute_glass_template,
    glass_wrap_path,
    compute_fill_height,
    create_warp_function,
    warp_layout,
)


class TestComputeGlassTemplate:
    def test_default_values(self):
        t = compute_glass_template()
        assert t["glass_height"] == 146
        assert t["top_radius"] == 43
        assert t["bottom_radius"] == 30
        assert t["inner_r"] > 0
        assert t["outer_r"] > t["inner_r"]
        assert t["sector_angle"] > 0
        assert t["volume_ml"] > 0

    def test_custom_values(self):
        t = compute_glass_template({
            "glass_height": 100,
            "top_radius": 40,
            "bottom_radius": 25,
        })
        assert t["glass_height"] == 100
        assert t["top_radius"] == 40

    def test_geometry_consistency(self):
        t = compute_glass_template()
        # outer_r = inner_r + slant_height
        assert abs(t["outer_r"] - (t["inner_r"] + t["slant_height"])) < 0.001

    def test_sector_angle_reasonable(self):
        t = compute_glass_template()
        # For a typical pint glass, sector angle should be less than pi
        assert 0 < t["sector_angle"] < math.pi


class TestGlassWrapPath:
    def test_returns_valid_svg_path(self):
        t = compute_glass_template()
        path = glass_wrap_path(t)
        assert path.startswith("M ")
        assert "A " in path
        assert "Z" in path

    def test_path_contains_arcs(self):
        t = compute_glass_template()
        path = glass_wrap_path(t)
        assert path.count("A ") == 2  # inner + outer arc


class TestComputeFillHeight:
    def test_full_volume(self):
        t = compute_glass_template()
        result = compute_fill_height(t, t["volume_ml"] + 100)
        assert result["fraction"] == 1.0

    def test_half_volume(self):
        t = compute_glass_template()
        result = compute_fill_height(t, t["volume_ml"] / 2)
        assert 0 < result["fraction"] < 1.0
        assert result["height_mm"] > 0

    def test_zero_volume(self):
        t = compute_glass_template()
        result = compute_fill_height(t, 0)
        # Should be very small
        assert result["fraction"] < 0.1


class TestCreateWarpFunction:
    def test_center_maps_correctly(self):
        t = compute_glass_template()
        warp = create_warp_function(t, 900, 700)
        # Center of rect should map to angle=0 (x near 0)
        wx, wy = warp(450, 350)
        assert abs(wx) < 1  # should be near center

    def test_top_maps_to_outer(self):
        t = compute_glass_template()
        warp = create_warp_function(t, 900, 700)
        # y=0 (top) should map to outer radius
        _, wy_top = warp(450, 0)
        _, wy_bot = warp(450, 700)
        assert abs(wy_top) > abs(wy_bot)  # top is farther from origin


class TestWarpLayout:
    def test_basic_warp(self):
        layout = {
            "holes": [
                {
                    "ref": 1,
                    "par": 4,
                    "start_x": 400,
                    "start_y": 100,
                    "end_x": 500,
                    "end_y": 300,
                    "direction": 1,
                    "features": [
                        {"category": "fairway", "coords": [[400, 150], [450, 250]]},
                    ],
                }
            ],
            "canvas_width": 900,
            "canvas_height": 700,
        }
        template = compute_glass_template()
        result = warp_layout(layout, template)
        assert result["warped"] is True
        assert result["template"] == template
        assert len(result["holes"]) == 1
        # Warped coords should differ from original
        wh = result["holes"][0]
        assert wh["start_x"] != 400
