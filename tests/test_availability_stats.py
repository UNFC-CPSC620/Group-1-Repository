import unittest

import pandas as pd

from availability_stats import (
    availability_stats_by_borough,
    availability_stats_by_room_type,
)

BOROUGH_COLUMNS = [
    "neighbourhood_group",
    "valid_listings",
    "mean_availability",
    "median_availability",
]
ROOM_COLUMNS = ["room_type", "valid_listings", "mean_availability"]


class TestAvailabilityStats(unittest.TestCase):
    def setUp(self):
        self.listings = pd.DataFrame(
            {
                "neighbourhood_group": ["Manhattan", "Manhattan", "Manhattan", "Brooklyn", "Brooklyn", "Queens"],
                "room_type": ["Entire home/apt", "Private room", "Private room", "Entire home/apt", "Private room", "Private room"],
                "availability_365": [0, 100, 365, 50, 150, 80],
            }
        )

    def test_borough_count_mean_median(self):
        out = availability_stats_by_borough(self.listings).set_index("neighbourhood_group")
        self.assertEqual(out.loc["Manhattan", "valid_listings"], 3)
        self.assertAlmostEqual(out.loc["Manhattan", "mean_availability"], 155.0)
        self.assertAlmostEqual(out.loc["Manhattan", "median_availability"], 100.0)
        self.assertAlmostEqual(out.loc["Brooklyn", "mean_availability"], 100.0)
        self.assertEqual(out.loc["Queens", "valid_listings"], 1)

    def test_room_type_count_and_mean(self):
        out = availability_stats_by_room_type(self.listings).set_index("room_type")
        self.assertEqual(out.loc["Private room", "valid_listings"], 4)
        self.assertAlmostEqual(out.loc["Private room", "mean_availability"], 173.75)
        self.assertAlmostEqual(out.loc["Entire home/apt", "mean_availability"], 25.0)

    def test_returns_dataframes_with_clear_columns(self):
        by_borough = availability_stats_by_borough(self.listings)
        by_room = availability_stats_by_room_type(self.listings)
        self.assertIsInstance(by_borough, pd.DataFrame)
        self.assertEqual(list(by_borough.columns), BOROUGH_COLUMNS)
        self.assertEqual(list(by_room.columns), ROOM_COLUMNS)

    def test_boundaries_0_and_365_are_valid(self):
        df = pd.DataFrame(
            {"neighbourhood_group": ["Bronx", "Bronx"], "room_type": ["Private room"] * 2, "availability_365": [0, 365]}
        )
        out = availability_stats_by_borough(df)
        self.assertEqual(out.loc[0, "valid_listings"], 2)
        self.assertAlmostEqual(out.loc[0, "mean_availability"], 182.5)

    def test_invalid_values_are_excluded(self):
        bad = pd.DataFrame(
            {
                "neighbourhood_group": ["Manhattan"] * 6,
                "room_type": ["Private room"] * 6,
                "availability_365": [None, "unknown", -1, 366, 999, 12.5],
            }
        )
        messy = pd.concat([self.listings, bad], ignore_index=True)
        out = availability_stats_by_borough(messy).set_index("neighbourhood_group")
        self.assertEqual(out.loc["Manhattan", "valid_listings"], 3)
        self.assertAlmostEqual(out.loc["Manhattan", "mean_availability"], 155.0)

    def test_text_with_days_suffix_is_read(self):
        df = pd.DataFrame(
            {"neighbourhood_group": ["Bronx", "Bronx"], "room_type": ["Private room"] * 2, "availability_365": ["178 days", "22 days"]}
        )
        self.assertAlmostEqual(availability_stats_by_borough(df).loc[0, "mean_availability"], 100.0)

    def test_nullable_integer_column_with_missing_values(self):
        df = pd.DataFrame(
            {
                "neighbourhood_group": ["Bronx"] * 3,
                "room_type": ["Private room"] * 3,
                "availability_365": pd.array([10, None, 30], dtype="Int64"),
            }
        )
        out = availability_stats_by_borough(df)
        self.assertEqual(out.loc[0, "valid_listings"], 2)
        self.assertAlmostEqual(out.loc[0, "mean_availability"], 20.0)

    def test_empty_dataframe_returns_empty_result(self):
        empty = pd.DataFrame(columns=["neighbourhood_group", "room_type", "availability_365"])
        self.assertTrue(availability_stats_by_borough(empty).empty)
        self.assertEqual(list(availability_stats_by_borough(empty).columns), BOROUGH_COLUMNS)
        self.assertEqual(list(availability_stats_by_room_type(empty).columns), ROOM_COLUMNS)

    def test_no_valid_values_returns_empty_result(self):
        df = pd.DataFrame(
            {"neighbourhood_group": ["Bronx"], "room_type": ["Private room"], "availability_365": [999]}
        )
        self.assertTrue(availability_stats_by_room_type(df).empty)

    def test_input_is_not_modified(self):
        before = self.listings.copy()
        availability_stats_by_borough(self.listings)
        availability_stats_by_room_type(self.listings)
        pd.testing.assert_frame_equal(self.listings, before)

    def test_missing_column_gives_clear_error(self):
        with self.assertRaisesRegex(KeyError, "availability_365"):
            availability_stats_by_borough(pd.DataFrame({"neighbourhood_group": ["Bronx"]}))
        with self.assertRaisesRegex(KeyError, "room_type"):
            availability_stats_by_room_type(pd.DataFrame({"availability_365": [5]}))

    def test_non_dataframe_gives_type_error(self):
        with self.assertRaises(TypeError):
            availability_stats_by_borough([1, 2, 3])

    def test_functions_have_docstrings(self):
        self.assertTrue(availability_stats_by_borough.__doc__)
        self.assertTrue(availability_stats_by_room_type.__doc__)


if __name__ == "__main__":
    unittest.main()
