
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
        self.assertEqual(manhattan["missing_review_count"], 0)

    def test_reviews_by_room_type(self):
        result = summarize_reviews_by_room_type(self.df)
        private = result[result["room_type"] == "Private room"].iloc[0]

        self.assertEqual(private["average_reviews"], 15)
        self.assertEqual(private["average_reviews_per_month"], 3)
        self.assertEqual(private["valid_review_count"], 2)
        self.assertEqual(private["missing_review_count"], 0)

    def test_missing_review_values(self):
        result = summarize_reviews_by_borough(self.df)
        brooklyn = result[result["borough"] == "Brooklyn"].iloc[0]

        self.assertEqual(brooklyn["valid_listing_count"], 1)
        self.assertEqual(brooklyn["missing_review_count"], 1)

    def test_missing_monthly_rates(self):
        result = summarize_reviews_by_room_type(self.df)
        shared = result[result["room_type"] == "Shared room"].iloc[0]

        self.assertEqual(shared["valid_monthly_rate_count"], 0)
        self.assertEqual(shared["missing_monthly_rate_count"], 1)

    def test_negative_and_invalid_values(self):
        df = self.df.copy()

        df["number_of_reviews"] = df["number_of_reviews"].astype(object)
        df["reviews_per_month"] = df["reviews_per_month"].astype(object)

        df.loc[0, "number_of_reviews"] = -5
        df.loc[1, "reviews_per_month"] = "invalid"

        result = summarize_reviews_by_room_type(df)
        private = result[result["room_type"] == "Private room"].iloc[0]

        self.assertEqual(private["valid_review_count"], 1)

    def test_zero_reviews_are_preserved(self):
        result = summarize_reviews_by_borough(self.df)
        manhattan = result[result["borough"] == "Manhattan"].iloc[0]

        self.assertEqual(manhattan["valid_listing_count"], 2)
        self.assertEqual(manhattan["average_reviews"], 5)

    def test_empty_dataframe(self):
        empty = self.df.iloc[0:0]
        result = summarize_reviews_by_borough(empty)

        self.assertTrue(result.empty)

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
