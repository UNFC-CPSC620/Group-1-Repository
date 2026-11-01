import unittest

import pandas as pd

from review_summaries import (
    summarize_reviews_by_borough,
    summarize_reviews_by_room_type,
    summarize_reviews,
)


class TestReviewSummaries(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "neighbourhood_group": [
                "Manhattan", "Manhattan", "Brooklyn", "Brooklyn"
            ],
            "room_type": [
                "Private room", "Entire home/apt",
                "Private room", "Shared room"
            ],
            "number_of_reviews": [10, 0, 20, None],
            "reviews_per_month": [2.0, 0.0, 4.0, None],
        })

    def test_reviews_by_borough(self):
        result = summarize_reviews_by_borough(self.df)

        manhattan = result[result["borough"] == "Manhattan"].iloc[0]
        self.assertEqual(manhattan["average_reviews"], 5)
        self.assertEqual(manhattan["median_reviews"], 5)
        self.assertEqual(manhattan["valid_listing_count"], 2)

    def test_reviews_by_room_type(self):
        result = summarize_reviews_by_room_type(self.df)

        private = result[result["room_type"] == "Private room"].iloc[0]
        self.assertEqual(private["average_reviews"], 15)
        self.assertEqual(private["average_reviews_per_month"], 3)

    def test_negative_and_invalid_values_are_excluded(self):
        df = self.df.copy()
        df.loc[0, "number_of_reviews"] = -5
        df.loc[1, "reviews_per_month"] = "invalid"

        result = summarize_reviews_by_room_type(df)
        private = result[result["room_type"] == "Private room"].iloc[0]

        self.assertEqual(private["valid_review_count"], 1)

    def test_valid_zero_reviews_are_preserved(self):
        result = summarize_reviews_by_borough(self.df)
        manhattan = result[result["borough"] == "Manhattan"].iloc[0]

        self.assertEqual(manhattan["average_reviews"], 5)
        self.assertEqual(manhattan["valid_listing_count"], 2)

    def test_empty_dataframe(self):
        empty = self.df.iloc[0:0]

        result = summarize_reviews_by_borough(empty)
        self.assertTrue(result.empty)
        self.assertEqual(
            list(result.columns),
            ["borough", "average_reviews", "median_reviews",
             "valid_listing_count"]
        )

    def test_missing_required_column(self):
        df = self.df.drop(columns=["number_of_reviews"])

        with self.assertRaises(ValueError):
            summarize_reviews_by_borough(df)

    def test_combined_summaries(self):
        result = summarize_reviews(self.df)

        self.assertIn("by_borough", result)
        self.assertIn("by_room_type", result)

    def test_original_dataframe_is_preserved(self):
        original = self.df.copy(deep=True)

        summarize_reviews(self.df)

        pd.testing.assert_frame_equal(self.df, original)


if __name__ == "__main__":
    unittest.main()
