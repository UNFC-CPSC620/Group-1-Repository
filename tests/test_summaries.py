"""Issue #19: borough and room-type summary unit tests."""
import unittest

import pandas as pd

from cleaning import clean_airbnb_data
from summaries import (
    summarize_listings_by_borough,
    summarize_listings_by_room_type,
    summarize_listings_by_borough_and_room_type,
    summarize_borough_percentages,
    summarize_listings,
)


class TestBoroughRoomSummaries(unittest.TestCase):
    def setUp(self):
        self.cleaned = pd.DataFrame({
            "neighbourhood_group": ["Manhattan", "Manhattan", "Brooklyn", "Queens", None],
            "room_type": ["Private room", "Entire home/apt", "Private room", "Private room", "Shared room"],
        })

    def test_borough_counts(self):
        result = summarize_listings_by_borough(self.cleaned)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result.columns), ["borough", "listing_count"])
        self.assertEqual(dict(zip(result.borough, result.listing_count)),
                         {"Manhattan": 2, "Brooklyn": 1, "Queens": 1})

    def test_room_type_counts(self):
        result = summarize_listings_by_room_type(self.cleaned)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(dict(zip(result.room_type, result.listing_count)),
                         {"Private room": 3, "Entire home/apt": 1, "Shared room": 1})

    def test_borough_room_type_combinations(self):
        result = summarize_listings_by_borough_and_room_type(self.cleaned)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result.columns), ["borough", "room_type", "listing_count"])
        counts = {(row.borough, row.room_type): row.listing_count for row in result.itertuples(index=False)}
        self.assertEqual(counts, {
            ("Manhattan", "Private room"): 1,
            ("Manhattan", "Entire home/apt"): 1,
            ("Brooklyn", "Private room"): 1,
            ("Queens", "Private room"): 1,
        })

    def test_percentages_sum_to_100(self):
        result = summarize_borough_percentages(self.cleaned)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result.columns), ["borough", "listing_count", "percentage"])
        percentages = dict(zip(result.borough, result.percentage))
        self.assertAlmostEqual(percentages["Manhattan"], 50.0)
        self.assertAlmostEqual(percentages["Brooklyn"], 25.0)
        self.assertAlmostEqual(percentages["Queens"], 25.0)
        self.assertAlmostEqual(result.percentage.sum(), 100.0, places=2)

    def test_missing_categories_are_excluded_per_summary(self):
        df = pd.DataFrame({
            "neighbourhood_group": ["Manhattan", None, "Brooklyn", "Queens"],
            "room_type": [None, "Private room", "Private room", None],
        })
        self.assertEqual(summarize_listings_by_borough(df).listing_count.sum(), 3)
        self.assertEqual(summarize_listings_by_room_type(df).listing_count.sum(), 2)
        self.assertEqual(summarize_listings_by_borough_and_room_type(df).listing_count.sum(), 1)

    def test_uses_cleaned_categories(self):
        raw = pd.DataFrame({
            "id": [1, 2, 2, 3],
            "price": ["100", "200", "200", "300"],
            "neighbourhood_group": [" manhattan ", "BROOKLYN", "BROOKLYN", "Unknown borough"],
            "room_type": ["PRIVATE ROOM", "Entire home/apt", "Entire home/apt", "Private room"],
            "availability_365": [0, 10, 10, 100],
        })
        cleaned = clean_airbnb_data(raw)
        result = summarize_listings(cleaned)
        self.assertEqual(dict(zip(result["by_borough"].borough,
                                  result["by_borough"].listing_count)),
                         {"Manhattan": 1, "Brooklyn": 1})
        self.assertEqual(result["by_room_type"].listing_count.sum(), 3)
        self.assertEqual(result["by_borough_and_room_type"].listing_count.sum(), 2)

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["neighbourhood_group", "room_type"])
        results = summarize_listings(df)
        self.assertEqual(set(results), {"by_borough", "by_room_type", "by_borough_and_room_type", "borough_percentages"})
        for result in results.values():
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)
        self.assertEqual(list(results["borough_percentages"].columns),
                         ["borough", "listing_count", "percentage"])

    def test_missing_required_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            summarize_listings_by_borough(pd.DataFrame({"neighbourhood_group": ["Brooklyn"]}))
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            summarize_listings_by_room_type(pd.DataFrame({"room_type": ["Private room"]}))
        with self.assertRaises(TypeError):
            summarize_listings(None)

    def test_does_not_modify_input(self):
        original = self.cleaned.copy(deep=True)
        summarize_listings(self.cleaned)
        pd.testing.assert_frame_equal(self.cleaned, original)


if __name__ == "__main__":
    unittest.main()
