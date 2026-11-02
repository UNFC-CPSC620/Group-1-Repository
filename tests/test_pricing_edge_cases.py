"""Additional unit tests for Issue #15 pricing summary acceptance criteria.

Target implementation: pricing_summaries.py from branch
16-airbnb-pricing-summaries-integration.
"""
import unittest

import pandas as pd

from pricing_summaries import (
    summarize_prices_by_borough,
    summarize_prices_by_room_type,
    generate_pricing_summaries,
)


class TestPricingEdgeCases(unittest.TestCase):
    @staticmethod
    def data(boroughs, rooms, prices):
        return pd.DataFrame({
            "neighbourhood_group": boroughs,
            "room_type": rooms,
            "price": prices,
        })

    def test_odd_count_average_and_median(self):
        df = self.data(["Manhattan"] * 3, ["Private room"] * 3, [100., 200., 900.])
        row = summarize_prices_by_borough(df).iloc[0]
        self.assertEqual(row["valid_listing_count"], 3)
        self.assertAlmostEqual(row["average_price"], 400.0)
        self.assertAlmostEqual(row["median_price"], 200.0)

    def test_even_count_median(self):
        df = self.data(["Brooklyn"] * 4, ["Private room"] * 4, [100., 200., 400., 1000.])
        row = summarize_prices_by_borough(df).iloc[0]
        self.assertEqual(row["valid_listing_count"], 4)
        self.assertAlmostEqual(row["average_price"], 425.0)
        self.assertAlmostEqual(row["median_price"], 300.0)

    def test_listing_counts_and_group_values(self):
        df = self.data(["Brooklyn", "Brooklyn", "Queens", "Queens"],
                       ["Private room", "Entire home/apt", "Private room", "Private room"],
                       [80., 120., 150., 250.])
        result = summarize_prices_by_borough(df).set_index("borough")
        self.assertEqual(result.loc["Brooklyn", "valid_listing_count"], 2)
        self.assertEqual(result.loc["Queens", "valid_listing_count"], 2)
        self.assertAlmostEqual(result.loc["Brooklyn", "average_price"], 100)
        self.assertAlmostEqual(result.loc["Queens", "median_price"], 200)

    def test_room_type_average_and_median(self):
        df = self.data(["Queens"] * 4,
                       ["Private room", "Private room", "Private room", "Entire home/apt"],
                       [30., 60., 300., 500.])
        result = summarize_prices_by_room_type(df).set_index("room_type")
        self.assertEqual(result.loc["Private room", "valid_listing_count"], 3)
        self.assertAlmostEqual(result.loc["Private room", "average_price"], 130)
        self.assertAlmostEqual(result.loc["Private room", "median_price"], 60)
        self.assertAlmostEqual(result.loc["Entire home/apt", "median_price"], 500)

    def test_invalid_zero_negative_and_missing_prices_excluded(self):
        df = self.data(["Manhattan"] * 5, ["Private room"] * 5,
                       [100., None, 0., -50., 300.])
        result = summarize_prices_by_borough(df)
        row = result.iloc[0]
        self.assertEqual(row["valid_listing_count"], 2)
        self.assertAlmostEqual(row["average_price"], 200)
        self.assertAlmostEqual(row["median_price"], 200)

    def test_missing_categories_not_counted(self):
        df = self.data(["Manhattan", None, "Brooklyn"],
                       ["Private room", "Private room", None], [100., 200., 300.])
        self.assertEqual(summarize_prices_by_borough(df)["valid_listing_count"].sum(), 2)
        self.assertEqual(summarize_prices_by_room_type(df)["valid_listing_count"].sum(), 2)

    def test_empty_dataframe_returns_structured_empty_dataframes(self):
        df = self.data([], [], [])
        for result, category in [
            (summarize_prices_by_borough(df), "borough"),
            (summarize_prices_by_room_type(df), "room_type"),
        ]:
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)
            self.assertEqual(list(result.columns), [category, "valid_listing_count", "average_price", "median_price"])

    def test_invalid_input_and_missing_columns(self):
        with self.assertRaises(TypeError):
            summarize_prices_by_borough(None)
        with self.assertRaises(ValueError):
            summarize_prices_by_borough(pd.DataFrame({"price": [100.]}))
        with self.assertRaises(ValueError):
            summarize_prices_by_room_type(pd.DataFrame({"price": [100.]}))

    def test_does_not_mutate_input(self):
        df = self.data(["Queens", "Queens"], ["Private room", "Shared room"], [100., 150.])
        before = df.copy(deep=True)
        summarize_prices_by_borough(df)
        summarize_prices_by_room_type(df)
        pd.testing.assert_frame_equal(df, before)

    def test_cleaning_rules_are_used_in_end_to_end_summary(self):
        raw = pd.DataFrame({
            "id": [1, 2, 2, 3, 4],
            "neighbourhood_group": [" manhattan ", "BROOKLYN", "BROOKLYN", "Queens", "Queens"],
            "room_type": ["PRIVATE ROOM", "Entire Home/Apt", "Entire Home/Apt", "Private room", "Private room"],
            "price": ["$100", "USD 200", "USD 999", "0", "invalid"],
            "availability_365": ["30", "60", "60", "90", "0"],
        })
        result = generate_pricing_summaries(raw)
        self.assertEqual(len(result["cleaned_data"]), 4)  # duplicate id removed
        self.assertEqual(int(result["by_borough"]["valid_listing_count"].sum()), 2)
        self.assertEqual(int(result["by_room_type"]["valid_listing_count"].sum()), 2)
        self.assertEqual(set(result["by_borough"]["borough"]), {"Manhattan", "Brooklyn"})


if __name__ == "__main__":
    unittest.main()
