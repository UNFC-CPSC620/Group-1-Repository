"""Regression tests for integer-like float counts in Airbnb cleaning.

Run from the repository root:
    python -m unittest discover -s tests -v
"""

import unittest

import pandas as pd

from cleaning import clean_airbnb_data, parse_count


class TestCleaningFloatCounts(unittest.TestCase):
    def test_accepts_integer_like_decimal_counts(self):
        values = pd.Series(["5", "5.0", "365.00", 0.0, pd.NA])
        result = parse_count(values)
        expected = pd.Series([5, 5, 365, 0, pd.NA], dtype="Int64")
        pd.testing.assert_series_equal(result, expected)

    def test_rejects_fractional_negative_and_non_numeric_counts(self):
        values = pd.Series(["5.5", "-2", "abc", "", None])
        result = parse_count(values)
        self.assertTrue(result.isna().all())

    def test_known_units_are_supported(self):
        nights = parse_count(pd.Series(["3 nights", "2.0 nights"]), suffix="nights")
        days = parse_count(pd.Series(["365 days", "7.0 days"]), suffix="days")
        self.assertEqual(nights.tolist(), [3, 2])
        self.assertEqual(days.tolist(), [365, 7])

    def test_cleaning_preserves_valid_float_counts_and_original_data(self):
        raw = pd.DataFrame({
            "id": [1, 2, 3, 4],
            "price": [100, 200, 50, 75],
            "neighbourhood_group": ["Manhattan", "Brooklyn", "Queens", "Bronx"],
            "room_type": ["Private room", "Entire home/apt", "Shared room", "Private room"],
            "availability_365": [0.0, 365.0, 365.5, float("nan")],
            "minimum_nights": [1.0, 2.0, 2.5, float("nan")],
        })
        original_copy = raw.copy(deep=True)

        cleaned = clean_airbnb_data(raw)

        self.assertEqual(cleaned.loc[0, "availability_365"], 0)
        self.assertEqual(cleaned.loc[1, "availability_365"], 365)
        self.assertTrue(pd.isna(cleaned.loc[2, "availability_365"]))
        self.assertTrue(pd.isna(cleaned.loc[3, "availability_365"]))
        self.assertEqual(cleaned.loc[0, "minimum_nights"], 1)
        self.assertEqual(cleaned.loc[1, "minimum_nights"], 2)
        self.assertTrue(pd.isna(cleaned.loc[2, "minimum_nights"]))
        self.assertTrue(pd.isna(cleaned.loc[3, "minimum_nights"]))
        pd.testing.assert_frame_equal(raw, original_copy)

    def test_availability_outside_0_to_365_becomes_missing(self):
        raw = pd.DataFrame({
            "id": [1, 2, 3],
            "price": [100, 200, 300],
            "neighbourhood_group": ["Manhattan", "Brooklyn", "Queens"],
            "room_type": ["Private room", "Private room", "Private room"],
            "availability_365": [365.0, 366.0, -1.0],
        })
        cleaned = clean_airbnb_data(raw)
        self.assertEqual(cleaned.loc[0, "availability_365"], 365)
        self.assertTrue(pd.isna(cleaned.loc[1, "availability_365"]))
        self.assertTrue(pd.isna(cleaned.loc[2, "availability_365"]))


if __name__ == "__main__":
    unittest.main()
