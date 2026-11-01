import unittest
import pandas as pd

from pricing_summaries import (
    generate_pricing_summaries,
    summarize_prices_by_borough,
    summarize_prices_by_room_type,
)


class TestPricingSummaries(unittest.TestCase):
    def setUp(self):
        self.cleaned = pd.DataFrame(
            {
                "neighbourhood_group": [
                    "Manhattan",
                    "Manhattan",
                    "Brooklyn",
                    "Brooklyn",
                    "Queens",
                ],
                "room_type": [
                    "Private room",
                    "Entire home/apt",
                    "Private room",
                    "Entire home/apt",
                    "Private room",
                ],
                "price": [100.0, 200.0, 80.0, 120.0, 0.0],
            }
        )

    def test_prices_by_borough(self):
        result = summarize_prices_by_borough(self.cleaned)
        manhattan = result[result["borough"] == "Manhattan"].iloc[0]

        self.assertEqual(manhattan["valid_listing_count"], 2)
        self.assertEqual(manhattan["average_price"], 150.0)
        self.assertEqual(manhattan["median_price"], 150.0)

    def test_prices_by_room_type(self):
        result = summarize_prices_by_room_type(self.cleaned)
        private = result[result["room_type"] == "Private room"].iloc[0]

        self.assertEqual(private["valid_listing_count"], 2)
        self.assertEqual(private["average_price"], 90.0)
        self.assertEqual(private["median_price"], 90.0)

    def test_invalid_prices_are_excluded(self):
        data = self.cleaned.copy()
        data.loc[0, "price"] = None
        result = summarize_prices_by_borough(data)

        manhattan = result[result["borough"] == "Manhattan"].iloc[0]
        self.assertEqual(manhattan["valid_listing_count"], 1)
        self.assertEqual(manhattan["average_price"], 200.0)

    def test_generate_pricing_summaries_cleans_raw_data(self):
        raw = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "neighbourhood_group": [" manhattan ", "BROOKLYN", "Queens"],
                "room_type": ["PRIVATE ROOM", "Entire Home/Apt", "Shared room"],
                "price": ["$100", "USD 200", "invalid"],
                "availability_365": ["30", "60", "90"],
                "minimum_nights": ["2", "3", "1"],
                "number_of_reviews": [1, 2, 0],
                "reviews_per_month": ["1.5", "2.0", None],
                "last_review": [None, "2024-01-01", None],
            }
        )

        results = generate_pricing_summaries(raw)

        self.assertEqual(len(results["cleaned_data"]), 3)
        self.assertEqual(
            results["by_borough"]["valid_listing_count"].sum(), 2
        )
        self.assertEqual(
            results["by_room_type"]["valid_listing_count"].sum(), 2
        )


if __name__ == "__main__":
    unittest.main()
