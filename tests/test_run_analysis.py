
"""Integration tests for the NYC Airbnb analytics pipeline.

Issue #30: Verify that loading, cleaning, and listing
summaries work together using the complete dataset.
"""

import unittest

import pandas as pd

from data_loader import load_airbnb_data
from run_analysis import run_pipeline, DEFAULT_DATASET


class TestAnalyticsPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.results = run_pipeline(DEFAULT_DATASET)
        cls.cleaned = cls.results["cleaned_data"]
        cls.summaries = cls.results["listing_summaries"]

    def test_pipeline_returns_required_outputs(self):
        required = {
            "original_data",
            "cleaned_data",
            "inspection",
            "cleaning_report",
            "listing_summaries",
        }
        self.assertTrue(required.issubset(self.results))

    def test_four_summary_dataframes(self):
        expected_columns = {
            "by_borough": ["borough", "listing_count"],
            "by_room_type": ["room_type", "listing_count"],
            "by_borough_and_room_type": [
                "borough", "room_type", "listing_count"
            ],
            "borough_percentages": [
                "borough", "listing_count", "percentage"
            ],
        }

        for name, columns in expected_columns.items():
            with self.subTest(summary=name):
                df = self.summaries[name]
                self.assertIsInstance(df, pd.DataFrame)
                self.assertEqual(list(df.columns), columns)

    def test_listing_counts_match_cleaned_data(self):
        borough_count = self.cleaned[
            "neighbourhood_group"
        ].notna().sum()

        room_count = self.cleaned[
            "room_type"
        ].notna().sum()

        self.assertEqual(
            self.summaries["by_borough"]["listing_count"].sum(),
            borough_count,
        )
        self.assertEqual(
            self.summaries["by_room_type"]["listing_count"].sum(),
            room_count,
        )

    def test_combination_counts(self):
        expected = self.cleaned[
            ["neighbourhood_group", "room_type"]
        ].notna().all(axis=1).sum()

        actual = self.summaries[
            "by_borough_and_room_type"
        ]["listing_count"].sum()

        self.assertEqual(actual, expected)

    def test_borough_percentages(self):
        summary = self.summaries["borough_percentages"]
        total = summary["listing_count"].sum()

        self.assertGreater(total, 0)

        for _, row in summary.iterrows():
            expected = round(
                row["listing_count"] / total * 100, 2
            )
            self.assertAlmostEqual(
                row["percentage"], expected, places=2
            )

        self.assertAlmostEqual(
            summary["percentage"].sum(),
            100.0,
            delta=0.05,
        )

    def test_original_data_is_preserved(self):
        original = load_airbnb_data(DEFAULT_DATASET)

        pd.testing.assert_frame_equal(
            self.results["original_data"],
            original,
        )

        self.assertIsNot(
            self.results["original_data"],
            self.results["cleaned_data"],
        )

    def test_individual_group_counts_match_cleaned_data(self):
        # Verify individual borough counts.
        expected_borough = (
            self.cleaned["neighbourhood_group"]
            .value_counts()
            .to_dict()
        )

        actual_borough = (
            self.summaries["by_borough"]
            .set_index("borough")["listing_count"]
            .to_dict()
        )

        self.assertEqual(actual_borough, expected_borough)

        # Verify individual room-type counts.
        expected_room = (
            self.cleaned["room_type"]
            .value_counts()
            .to_dict()
        )

        actual_room = (
            self.summaries["by_room_type"]
            .set_index("room_type")["listing_count"]
            .to_dict()
        )

        self.assertEqual(actual_room, expected_room)

        # Verify each borough and room-type combination.
        expected_combinations = (
            self.cleaned
            .groupby(
                ["neighbourhood_group", "room_type"],
                observed=True
            )
            .size()
            .to_dict()
        )

        actual_combinations = {
            (row.borough, row.room_type): row.listing_count
            for row in self.summaries[
                "by_borough_and_room_type"
            ].itertuples(index=False)
        }

        self.assertEqual(
            actual_combinations,
            expected_combinations
        )


if __name__ == "__main__":
    unittest.main()
