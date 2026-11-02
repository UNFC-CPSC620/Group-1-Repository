
"""Review validation tests for the NYC Airbnb analytics pipeline.

Issue #30, PR #36.

Verify that:
1. The complete Airbnb dataset is available.
2. All eight summary DataFrames are generated.
3. Required-column errors are clear.
4. Listing counts match the cleaned dataset.
5. The original dataset is preserved.
"""

import unittest
from unittest.mock import patch

import pandas as pd

from data_loader import load_airbnb_data
from run_analysis import (
    DEFAULT_DATASET,
    REQUIRED_PIPELINE_COLUMNS,
    run_pipeline,
)


class TestPipelineReviewRequirements(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not DEFAULT_DATASET.is_file():
            raise FileNotFoundError(
                f"Required Airbnb dataset not found: {DEFAULT_DATASET}"
            )

        cls.results = run_pipeline(DEFAULT_DATASET)
        cls.cleaned = cls.results["cleaned_data"]

    def test_full_dataset_is_available(self):
        """The complete NYC Airbnb dataset must be accessible."""
        self.assertTrue(DEFAULT_DATASET.is_file())

        self.assertEqual(
            len(self.results["original_data"]),
            42336,
        )

        self.assertEqual(
            len(self.cleaned),
            42000,
        )

    def test_pipeline_returns_all_eight_summaries(self):
        """Verify all listing, pricing and availability tables."""

        expected = {
            "listing_summaries": {
                "by_borough",
                "by_room_type",
                "by_borough_and_room_type",
                "borough_percentages",
            },
            "pricing_summaries": {
                "by_borough",
                "by_room_type",
            },
            "availability_summaries": {
                "by_borough",
                "by_room_type",
            },
        }

        total_tables = 0

        for family, expected_names in expected.items():
            with self.subTest(family=family):
                self.assertIn(family, self.results)

                tables = self.results[family]
                self.assertEqual(set(tables), expected_names)

                for name, table in tables.items():
                    with self.subTest(table=name):
                        self.assertIsInstance(table, pd.DataFrame)

                total_tables += len(tables)

        self.assertEqual(total_tables, 8)

    def test_missing_required_columns_raise_clear_errors(self):
        """Every missing core column must produce a useful error."""

        complete_row = {
            "id": 1,
            "neighbourhood_group": "Manhattan",
            "room_type": "Private room",
            "price": 100,
            "availability_365": 180,
        }

        for column in sorted(REQUIRED_PIPELINE_COLUMNS):
            with self.subTest(missing_column=column):
                incomplete_data = (
                    pd.DataFrame([complete_row])
                    .drop(columns=[column])
                )

                with patch(
                    "run_analysis.load_airbnb_data",
                    return_value=incomplete_data,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"Missing required Airbnb columns: {column}",
                    ):
                        run_pipeline(DEFAULT_DATASET)

    def test_listing_counts_match_cleaned_dataset(self):
        """Listing summaries must agree with cleaned data."""

        borough_count = (
            self.cleaned["neighbourhood_group"]
            .notna()
            .sum()
        )

        room_count = (
            self.cleaned["room_type"]
            .notna()
            .sum()
        )

        listing_tables = self.results["listing_summaries"]

        self.assertEqual(
            listing_tables["by_borough"]["listing_count"].sum(),
            borough_count,
        )

        self.assertEqual(
            listing_tables["by_room_type"]["listing_count"].sum(),
            room_count,
        )

    def test_original_data_is_preserved(self):
        """The pipeline must not modify the original dataset."""

        original = load_airbnb_data(DEFAULT_DATASET)

        pd.testing.assert_frame_equal(
            self.results["original_data"],
            original,
        )

        self.assertIsNot(
            self.results["original_data"],
            self.results["cleaned_data"],
        )


if __name__ == "__main__":
    unittest.main()
