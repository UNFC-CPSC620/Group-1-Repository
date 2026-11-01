
"""Run the integrated NYC Airbnb analytics pipeline (Issue #30).

Load, inspect, and clean the dataset once, then calculate reusable listing,
pricing, and availability summaries from that same cleaned DataFrame.
Review-activity summaries are not yet integrated.
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
from summaries import summarize_listings


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_DIR / "Airbnb_NYC.csv"

# Required by cleaning, listing summaries, pricing, availability and preview.
REQUIRED_PIPELINE_COLUMNS = frozenset({
    "id", "neighbourhood_group", "room_type", "price", "availability_365"
})


def run_pipeline(file_path: str | Path = DEFAULT_DATASET) -> dict:
    """Load, inspect and clean data, then return three families of summaries.

    All analysis functions receive the SAME cleaned DataFrame. This function
    never modifies the original DataFrame or overwrites the source CSV.
    """
    raw = load_airbnb_data(file_path)
    missing = REQUIRED_PIPELINE_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(
            "Missing required Airbnb columns: " + ", ".join(sorted(missing))
        )

    inspection = inspect_dataset(raw)
    cleaned = clean_airbnb_data(raw)
    report = cleaning_report(raw, cleaned)

    listing_summaries = summarize_listings(cleaned)
    pricing_summaries = {
        "by_borough": summarize_prices_by_borough(cleaned),
        "by_room_type": summarize_prices_by_room_type(cleaned),
    }
    availability_summaries = {
        "by_borough": availability_stats_by_borough(cleaned),
        "by_room_type": availability_stats_by_room_type(cleaned),
    }

    return {
        "original_data": raw,
        "cleaned_data": cleaned,
        "inspection": inspection,
        "cleaning_report": report,
        "listing_summaries": listing_summaries,
        "pricing_summaries": pricing_summaries,
        "availability_summaries": availability_summaries,
    }


def _print_summaries(title: str, tables: dict) -> None:
    """Print each DataFrame in a named family of summaries."""
    print(f"\n{title}")
    for name, frame in tables.items():
        print(f"\n{name.replace('_', ' ').title()}")
        print(frame.to_string(index=False))


def main() -> None:
    """Execute the pipeline from the command line."""
    parser = argparse.ArgumentParser(
        description="Load, inspect, clean, and summarize NYC Airbnb listings."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to Airbnb CSV (default: Airbnb_NYC.csv beside this script).",
    )
    args = parser.parse_args()

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

    print("\nCleaning results:")
    for metric, value in report.items():
        print(f"  {metric}: {value}")

    preview_columns = [
        "id", "neighbourhood_group", "room_type", "price", "availability_365"
    ]
    print("\nPreview of cleaned data:")
    print(cleaned.loc[:, preview_columns].head().to_string(index=False))

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

    print("\nListing, pricing, and availability summaries integrated.")
    print("Review-activity summaries are not yet integrated.")


if __name__ == "__main__":
    main()
