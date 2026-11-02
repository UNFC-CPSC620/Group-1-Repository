
"""Integration review tests for the NYC Airbnb analytics pipeline.

Issue #30, PR #36.

Verify that:
1. The complete Airbnb dataset is available.
2. All ten summary DataFrames are generated.
3. Missing required columns produce clear errors.
4. Listing counts match the cleaned dataset.
5. Pricing summary counts match valid cleaned prices.
6. Availability counts match valid cleaned availability.
7. Review summary counts match valid review data.
8. The original dataset is preserved.
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
        """Run the integrated pipeline using the full dataset."""

        if not DEFAULT_DATASET.is_file():
            raise FileNotFoundError(
                f"Required Airbnb dataset not found: {DEFAULT_DATASET}"
            )

        cls.results = run_pipeline(DEFAULT_DATASET)
        cls.cleaned = cls.results["cleaned_data"]

    def test_full_dataset_is_available(self):
        """Verify the expected source and cleaned dataset sizes."""

        self.assertTrue(DEFAULT_DATASET.is_file())

        self.assertEqual(
            len(self.results["original_data"]),
            42336,
        )

        self.assertEqual(
            len(self.cleaned),
            42000,
        )

    def test_pipeline_returns_all_ten_summaries(self):
        """Verify all four families and ten summary DataFrames."""

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
            "review_summaries": {
                "by_borough",
                "by_room_type",
            },
        }

        total_tables = 0

        for family, expected_names in expected.items():
            with self.subTest(family=family):
                self.assertIn(family, self.results)

                tables = self.results[family]

                self.assertEqual(
                    set(tables.keys()),
                    expected_names,
                )

                for name, table in tables.items():
                    with self.subTest(
                        family=family,
                        table=name,
                    ):
                        self.assertIsInstance(
                            table,
                            pd.DataFrame,
                        )
                        self.assertFalse(table.empty)

                total_tables += len(tables)

        self.assertEqual(total_tables, 10)

    def test_missing_required_columns_raise_clear_errors(self):
        """Each missing required column must raise a clear ValueError."""

        complete_row = {
            "id": 1,
            "neighbourhood_group": "Manhattan",
            "room_type": "Private room",
            "price": 100,
            "availability_365": 180,
            "number_of_reviews": 5,
            "reviews_per_month": 1.5,
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
        """Listing totals must match valid cleaned categories."""

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

    def test_pricing_summary_counts_match_cleaned_data(self):
        """Pricing summaries must count only valid positive prices."""

        valid_prices = pd.to_numeric(
            self.cleaned["price"],
            errors="coerce",
        )

        valid_mask = valid_prices.gt(0).fillna(False)

        groups = [
            ("by_borough", "neighbourhood_group", "borough"),
            ("by_room_type", "room_type", "room_type"),
        ]

        for summary_name, group_column, output_column in groups:
            with self.subTest(summary=summary_name):

                expected = (
                    self.cleaned.loc[
                        valid_mask
                        & self.cleaned[group_column].notna()
                    ]
                    .groupby(group_column)
                    .size()
                    .to_dict()
                )

                actual = (
                    self.results["pricing_summaries"][summary_name]
                    .set_index(output_column)["valid_listing_count"]
                    .to_dict()
                )

                self.assertEqual(actual, expected)

    def test_availability_summary_counts_match_cleaned_data(self):
        """Availability summaries must count valid days from 0 to 365."""

        days = pd.to_numeric(
            self.cleaned["availability_365"],
            errors="coerce",
        )

        valid_mask = (
            days.between(0, 365).fillna(False)
            & days.mod(1).eq(0).fillna(False)
        )

        groups = [
            (
                "by_borough",
                "neighbourhood_group",
                "neighbourhood_group",
            ),
            (
                "by_room_type",
                "room_type",
                "room_type",
            ),
        ]

        for summary_name, group_column, output_column in groups:
            with self.subTest(summary=summary_name):

                expected = (
                    self.cleaned.loc[
                        valid_mask
                        & self.cleaned[group_column].notna()
                    ]
                    .groupby(group_column)
                    .size()
                    .to_dict()
                )

                actual = (
                    self.results["availability_summaries"][summary_name]
                    .set_index(output_column)["valid_listings"]
                    .to_dict()
                )

                self.assertEqual(actual, expected)

    def test_review_summary_counts_match_cleaned_data(self):
        """Review summaries must agree with valid cleaned review values."""

        valid_reviews = pd.to_numeric(
            self.cleaned["number_of_reviews"],
            errors="coerce",
        )

        valid_reviews = valid_reviews.where(
            valid_reviews >= 0
        )

        valid_monthly_rates = pd.to_numeric(
            self.cleaned["reviews_per_month"],
            errors="coerce",
        )

        valid_monthly_rates = valid_monthly_rates.where(
            valid_monthly_rates >= 0
        )

        review_data = self.cleaned.assign(
            _valid_reviews=valid_reviews,
            _valid_monthly_rates=valid_monthly_rates,
        )

        # Check valid review counts by borough.
        expected_borough = (
            review_data
            .dropna(subset=["neighbourhood_group"])
            .groupby("neighbourhood_group")["_valid_reviews"]
            .count()
            .to_dict()
        )

        actual_borough = (
            self.results["review_summaries"]["by_borough"]
            .set_index("borough")["valid_listing_count"]
            .to_dict()
        )

        self.assertEqual(
            actual_borough,
            expected_borough,
        )

        # Check valid review counts by room type.
        room_groups = (
            review_data
            .dropna(subset=["room_type"])
            .groupby("room_type")
        )

        expected_room = (
            room_groups["_valid_reviews"]
            .count()
            .to_dict()
        )

        actual_room = (
            self.results["review_summaries"]["by_room_type"]
            .set_index("room_type")["valid_review_count"]
            .to_dict()
        )

        self.assertEqual(
            actual_room,
            expected_room,
        )

        # Check valid monthly review-rate counts.
        expected_monthly = (
            room_groups["_valid_monthly_rates"]
            .count()
            .to_dict()
        )

        actual_monthly = (
            self.results["review_summaries"]["by_room_type"]
            .set_index("room_type")["valid_monthly_rate_count"]
            .to_dict()
        )

        self.assertEqual(
            actual_monthly,
            expected_monthly,
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
