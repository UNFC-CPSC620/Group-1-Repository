
"""Run the integrated stages of the NYC Airbnb analytics project.

Issue #30: Load, inspect, clean, and summarize NYC Airbnb listings.
Borough and room-type summaries are integrated.
Pricing, availability, and review-activity summaries will be
connected after their implementations are verified.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from data_loader import load_airbnb_data
from data_inspection import inspect_dataset
from cleaning import clean_airbnb_data, cleaning_report
from summaries import summarize_listings


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_DIR / "Airbnb_NYC.csv"


def run_pipeline(file_path: str | Path = DEFAULT_DATASET) -> dict:
    """Load, inspect, clean, and summarize Airbnb data.

    The original DataFrame is not modified, and this function
    does not overwrite the source CSV file.
    """
    raw = load_airbnb_data(file_path)
    inspection = inspect_dataset(raw)
    cleaned = clean_airbnb_data(raw)
    report = cleaning_report(raw, cleaned)

    # Generate summaries using the cleaned dataset.
    listing_summaries = summarize_listings(cleaned)

    return {
        "original_data": raw,
        "cleaned_data": cleaned,
        "inspection": inspection,
        "cleaning_report": report,
        "listing_summaries": listing_summaries,
    }


def main() -> None:
    """Execute the integrated analytics pipeline."""
    parser = argparse.ArgumentParser(
        description="Load, inspect, clean, and summarize NYC Airbnb data."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to the Airbnb CSV dataset.",
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

    # Display all four listing summary tables.
    print("\nBorough and Room-Type Summaries")

    for name, summary in results["listing_summaries"].items():
        print(f"\n{name.replace('_', ' ').title()}")
        print(summary.to_string(index=False))

    print("\nBorough and room-type summary integration complete.")
    print(
        "Pricing, availability, and review-activity "
        "summaries are not yet integrated."
    )


if __name__ == "__main__":
    main()
