
"""Run the integrated NYC Airbnb analytics pipeline (Issue #30).

Load, inspect, and clean the Airbnb dataset once, then calculate
reusable listing, pricing, availability, and review-activity summaries
from the same cleaned DataFrame.

The pipeline returns ten summary tables across four families.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from availability_stats import (
    availability_stats_by_borough,
    availability_stats_by_room_type,
)
from cleaning import clean_airbnb_data, cleaning_report
from data_inspection import inspect_dataset
from data_loader import load_airbnb_data
from pricing_summaries import (
    summarize_prices_by_borough,
    summarize_prices_by_room_type,
)
from review_summaries import summarize_reviews
from summaries import summarize_listings


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_DIR / "Airbnb_NYC.csv"


# Required columns for all four analytics modules.
REQUIRED_PIPELINE_COLUMNS = frozenset({
    "id",
    "neighbourhood_group",
    "room_type",
    "price",
    "availability_365",
    "number_of_reviews",
    "reviews_per_month",
})


def run_pipeline(file_path: str | Path = DEFAULT_DATASET) -> dict:
    """Run the complete NYC Airbnb analytics pipeline.

    The dataset is loaded, inspected, and cleaned once.

    All summary functions receive the same cleaned DataFrame.

    The original DataFrame is preserved, and the source CSV file
    is never overwritten.

    Returns
    -------
    dict
        Original data, cleaned data, inspection results,
        cleaning report, and four families of summary DataFrames.
    """
    raw = load_airbnb_data(file_path)

    # Validate required columns before processing.
    missing = REQUIRED_PIPELINE_COLUMNS.difference(raw.columns)

    if missing:
        raise ValueError(
            "Missing required Airbnb columns: "
            + ", ".join(sorted(missing))
        )

    # Stage 1: Inspect the original dataset.
    inspection = inspect_dataset(raw)

    # Stage 2: Clean the dataset.
    cleaned = clean_airbnb_data(raw)

    # Stage 3: Generate the cleaning report.
    report = cleaning_report(raw, cleaned)

    # Stage 4: Generate listing summaries.
    listing_summaries = summarize_listings(cleaned)

    # Stage 5: Generate pricing summaries.
    pricing_summaries = {
        "by_borough": summarize_prices_by_borough(cleaned),
        "by_room_type": summarize_prices_by_room_type(cleaned),
    }

    # Stage 6: Generate availability summaries.
    availability_summaries = {
        "by_borough": availability_stats_by_borough(cleaned),
        "by_room_type": availability_stats_by_room_type(cleaned),
    }

    # Stage 7: Generate review-activity summaries.
    review_summaries = summarize_reviews(cleaned)

    # Return all pipeline results.
    return {
        "original_data": raw,
        "cleaned_data": cleaned,
        "inspection": inspection,
        "cleaning_report": report,
        "listing_summaries": listing_summaries,
        "pricing_summaries": pricing_summaries,
        "availability_summaries": availability_summaries,
        "review_summaries": review_summaries,
    }


def _print_summaries(title: str, tables: dict) -> None:
    """Print each DataFrame in a named family of summaries."""
    print(f"\n{title}")

    for name, frame in tables.items():
        print(f"\n{name.replace('_', ' ').title()}")
        print(frame.to_string(index=False))


def main() -> None:
    """Execute the complete analytics pipeline from the command line."""

    parser = argparse.ArgumentParser(
        description=(
            "Load, inspect, clean, and summarize "
            "NYC Airbnb listings."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_DATASET,
        help=(
            "Path to Airbnb CSV "
            "(default: Airbnb_NYC.csv beside this script)."
        ),
    )

    args = parser.parse_args()

    # Run the complete pipeline.
    results = run_pipeline(args.input)

    inspection = results["inspection"]
    report = results["cleaning_report"]
    cleaned = results["cleaned_data"]

    print("NYC Airbnb Analytics - Integrated Pipeline")

    print(
        f"Original dataset: {inspection['total_rows']} rows x "
        f"{inspection['total_columns']} columns"
    )

    print(
        "Data-quality issue categories found: "
        f"{len(inspection['potential_issues'])}"
    )

    # Display cleaning results.
    print("\nCleaning results:")

    for metric, value in report.items():
        print(f"  {metric}: {value}")

    # Preview the cleaned dataset.
    preview_columns = [
        "id",
        "neighbourhood_group",
        "room_type",
        "price",
        "availability_365",
    ]

    print("\nPreview of cleaned data:")

    print(
        cleaned.loc[:, preview_columns]
        .head()
        .to_string(index=False)
    )

    # Display all four summary families.
    _print_summaries(
        "Borough and Room-Type Listing Summaries",
        results["listing_summaries"],
    )

    _print_summaries(
        "Pricing Summaries (USD per night)",
        results["pricing_summaries"],
    )

    _print_summaries(
        "Availability Summaries (days per year)",
        results["availability_summaries"],
    )

    _print_summaries(
        "Review-Activity Summaries",
        results["review_summaries"],
    )

    # Final confirmation.
    total_tables = sum(
        len(results[family])
        for family in (
            "listing_summaries",
            "pricing_summaries",
            "availability_summaries",
            "review_summaries",
        )
    )

    print(
        "\nListing, pricing, availability, and "
        "review-activity summaries integrated."
    )

    print(f"Total summary tables generated: {total_tables}")


if __name__ == "__main__":
    main()
