"""Unit tests for issue #8 cleaning behavior (uses only unittest and pandas)."""

import unittest

import pandas as pd

from cleaning import clean_airbnb_data, cleaning_report, parse_price


class TestAirbnbCleaning(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame(
            {
                "id": [1, 2, 2, 3, 4],
                "price": ["USD 63", "$ 70 / night", "$ 70 / night", "0", "invalid"],
                "neighbourhood_group": [
                    " manhattan ", "BROOKLYN", "BROOKLYN", "Queens", "Bronx"
                ],
                "room_type": [
                    "PRIVATE ROOM", " Entire Home/Apt ", " Entire Home/Apt ",
                    "Shared room", "Private room"
                ],
                "minimum_nights": ["3 nights", "2", "2", "0", None],
                "availability_365": ["365 days", "999", "999", "0 days", None],
                "reviews_per_month": [None, "unknown", "unknown", None, "0.5"],
                "number_of_reviews": [0, 4, 4, 0, 1],
                "last_review": [None, "2019-06-24", "2019-06-24", None, None],
            }
        )

    def test_cleaning_does_not_mutate_original(self):
        original = self.raw.copy(deep=True)
        clean_airbnb_data(self.raw)
        pd.testing.assert_frame_equal(self.raw, original)

    def test_duplicate_listing_ids_removed(self):
        cleaned = clean_airbnb_data(self.raw)
        self.assertEqual(len(cleaned), 4)
        self.assertFalse(cleaned["id"].duplicated().any())

    def test_price_formats_and_invalid_values(self):
        cleaned = clean_airbnb_data(self.raw)
        self.assertEqual(float(cleaned.loc[0, "price"]), 63.0)
        self.assertEqual(float(cleaned.loc[1, "price"]), 70.0)
        self.assertTrue(pd.isna(cleaned.loc[2, "price"]))
        self.assertTrue(pd.isna(cleaned.loc[3, "price"]))
        p = parse_price(pd.Series(["$1,000.50", "USD 12", "100 per month"]))
        self.assertEqual(float(p.iloc[0]), 1000.50)
        self.assertEqual(float(p.iloc[1]), 12)
        self.assertTrue(pd.isna(p.iloc[2]))

    def test_categories_are_standardized(self):
        cleaned = clean_airbnb_data(self.raw)
        self.assertEqual(cleaned.loc[0, "neighbourhood_group"], "Manhattan")
        self.assertEqual(cleaned.loc[1, "neighbourhood_group"], "Brooklyn")
        self.assertEqual(cleaned.loc[1, "room_type"], "Entire home/apt")

    def test_invalid_availability_and_nights(self):
        cleaned = clean_airbnb_data(self.raw)
        self.assertEqual(int(cleaned.loc[0, "availability_365"]), 365)
        self.assertTrue(pd.isna(cleaned.loc[1, "availability_365"]))
        self.assertEqual(int(cleaned.loc[0, "minimum_nights"]), 3)
        self.assertTrue(pd.isna(cleaned.loc[2, "minimum_nights"]))

    def test_missing_review_policy(self):
        cleaned = clean_airbnb_data(self.raw)
        self.assertEqual(float(cleaned.loc[0, "reviews_per_month"]), 0.0)
        self.assertTrue(pd.isna(cleaned.loc[1, "reviews_per_month"]))

    def test_required_columns_and_report(self):
        with self.assertRaisesRegex(ValueError, "Missing required Airbnb columns"):
            clean_airbnb_data(pd.DataFrame({"id": [1]}))
        cleaned = clean_airbnb_data(self.raw)
        report = cleaning_report(self.raw, cleaned)
        self.assertEqual(report["duplicate_listings_removed"], 1)
        self.assertEqual(report["cleaned_rows"], 4)


if __name__ == "__main__":
    unittest.main()
