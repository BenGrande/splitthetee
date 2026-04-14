"""Tests for hole association service."""

from app.services.golf.holes import (
    associate_features,
    _get_api_hole_data,
    _estimate_difficulty,
    _dist_sq,
    _min_dist_between,
    _bbox,
    _bbox_overlaps,
)


class TestDistSq:
    def test_same_point(self):
        assert _dist_sq([0, 0], [0, 0]) == 0.0

    def test_known_distance(self):
        assert _dist_sq([0, 0], [3, 4]) == 25.0


class TestMinDistBetween:
    def test_closest_pair(self):
        coords1 = [[0, 0], [10, 10]]
        coords2 = [[1, 0], [20, 20]]
        assert _min_dist_between(coords1, coords2) == 1.0


class TestBbox:
    def test_basic(self):
        bb = _bbox([[0, 0], [1, 2]])
        assert bb["min_lat"] == 0
        assert bb["max_lat"] == 1
        assert bb["min_lon"] == 0
        assert bb["max_lon"] == 2

    def test_padding(self):
        bb = _bbox([[0, 0], [1, 1]], pad=0.5)
        assert bb["min_lat"] == -0.5
        assert bb["max_lat"] == 1.5


class TestBboxOverlaps:
    def test_overlapping(self):
        a = _bbox([[0, 0], [2, 2]])
        b = _bbox([[1, 1], [3, 3]])
        assert _bbox_overlaps(a, b)

    def test_non_overlapping(self):
        a = _bbox([[0, 0], [1, 1]])
        b = _bbox([[5, 5], [6, 6]])
        assert not _bbox_overlaps(a, b)


class TestGetApiHoleData:
    def test_no_course_data(self):
        assert _get_api_hole_data(None) == []

    def test_no_tees(self):
        assert _get_api_hole_data({"name": "Test"}) == []

    def test_male_tees_preferred(self):
        data = {
            "tees": {
                "male": [
                    {"total_yards": 6000, "holes": [{"par": 4, "yardage": 400}]},
                    {"total_yards": 6500, "holes": [{"par": 4, "yardage": 420}]},
                ],
                "female": [
                    {"total_yards": 5000, "holes": [{"par": 4, "yardage": 350}]},
                ],
            }
        }
        result = _get_api_hole_data(data)
        assert result[0]["yardage"] == 420  # longest male tee

    def test_female_tees_fallback(self):
        data = {
            "tees": {
                "male": [],
                "female": [
                    {"total_yards": 5000, "holes": [{"par": 4, "yardage": 350}]},
                ],
            }
        }
        result = _get_api_hole_data(data)
        assert result[0]["yardage"] == 350


class TestEstimateDifficulty:
    def test_long_par4_is_hard(self):
        d = _estimate_difficulty(4, 480)
        assert d <= 5  # hard

    def test_short_par3_is_easy(self):
        d = _estimate_difficulty(3, 130)
        assert d >= 14  # easy

    def test_clamped_min(self):
        d = _estimate_difficulty(4, 600)
        assert d >= 1

    def test_clamped_max(self):
        d = _estimate_difficulty(3, 50)
        assert d <= 18


class TestAssociateFeatures:
    def _make_hole(self, ref, coords=None):
        return {
            "id": f"way/{ref}",
            "category": "hole",
            "ref": str(ref),
            "par": 4,
            "name": None,
            "coords": coords or [[36.0 + ref * 0.001, -121.0]],
        }

    def _make_feature(self, fid, category, coords):
        return {
            "id": f"way/{fid}",
            "category": category,
            "ref": None,
            "par": None,
            "name": None,
            "coords": coords,
        }

    def test_no_holes(self):
        features = [self._make_feature(1, "fairway", [[36.0, -121.0]])]
        assert associate_features(features) == []

    def test_basic_association(self):
        hole1 = self._make_hole(1, [[36.0, -121.0], [36.001, -121.0]])
        hole2 = self._make_hole(2, [[36.01, -121.0], [36.011, -121.0]])
        fairway = self._make_feature(10, "fairway", [[36.0005, -121.0], [36.0008, -121.0]])

        result = associate_features([hole1, hole2, fairway])
        assert len(result) == 2
        # Fairway should be associated with hole 1 (closer)
        assert len(result[0]["features"]) == 1
        assert result[0]["features"][0]["id"] == "way/10"
        assert len(result[1]["features"]) == 0

    def test_deduplicates_holes_by_ref(self):
        hole1a = self._make_hole(1, [[36.0, -121.0]])
        hole1b = self._make_hole(1, [[36.0, -121.0], [36.001, -121.0], [36.002, -121.0]])

        result = associate_features([hole1a, hole1b])
        assert len(result) == 1
        # Should keep the one with more coords
        assert len(result[0]["route_coords"]) == 3

    def test_skips_path_features(self):
        hole = self._make_hole(1, [[36.0, -121.0], [36.001, -121.0]])
        path_feat = self._make_feature(10, "path", [[36.0005, -121.0]])

        result = associate_features([hole, path_feat])
        assert len(result[0]["features"]) == 0

    def test_skips_course_boundary(self):
        hole = self._make_hole(1, [[36.0, -121.0], [36.001, -121.0]])
        boundary = self._make_feature(10, "course_boundary", [[36.0, -121.0]])

        result = associate_features([hole, boundary])
        assert len(result[0]["features"]) == 0

    def test_difficulty_from_handicap(self):
        hole = self._make_hole(1, [[36.0, -121.0], [36.001, -121.0]])
        course_data = {
            "tees": {
                "male": [{"total_yards": 6500, "holes": [
                    {"par": 4, "yardage": 400, "handicap": 3}
                ]}],
                "female": [],
            }
        }
        result = associate_features([hole], course_data)
        assert result[0]["difficulty"] == 3.0

    def test_default_difficulty(self):
        hole = self._make_hole(1, [[36.0, -121.0], [36.001, -121.0]])
        result = associate_features([hole])
        assert result[0]["difficulty"] == 9.0
