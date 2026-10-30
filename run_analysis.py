"""Run the currently integrated stages of the NYC Airbnb analytics project.

Issue #30: Phase 1 — load, inspect, and clean the dataset.
Pricing, listing, availability, and review summaries will be connected
only after their implementations are reviewed and merged into main.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from data_loader import load_airbnb_data
from data_inspection import inspect_dataset
from cleaning import clean_airbnb_data, cleaning_report


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_DIR / "Airbnb_NYC.csv"


def run_pipeline(file_path: str | Path = DEFAULT_DATASET) -> dict:
    """Load, inspect, and clean Airbnb data; return results for reuse.

    The original DataFrame is not modified, and this function does not
    overwrite the source CSV file.
    """
    raw = load_airbnb_data(file_path)
    inspection = inspect_dataset(raw)
    cleaned = clean_airbnb_data(raw)
    report = cleaning_report(raw, cleaned)

    return {
        "original_data": raw,
        "cleaned_data": cleaned,
        "inspection": inspection,
        "cleaning_report": report,
    }


def main() -> None:
    """Run Phase 1 from the command line and display a short report."""
    parser = argparse.ArgumentParser(
        description="Load, inspect, and clean the NYC Airbnb dataset."
    )
    parser.add_argument(
        "--input", type=Path, default=DEFAULT_DATASET,
        help="Path to the original CSV (default: Airbnb_NYC.csv beside this script)",
    )
    args = parser.parse_args()

    results = run_pipeline(args.input)
    inspection = results["inspection"]
    report = results["cleaning_report"]
    cleaned = results["cleaned_data"]

    print("NYC Airbnb Analytics — Phase 1")
    print(
        f"Original dataset: {inspection['total_rows']} rows x "
        f"{inspection['total_columns']} columns"
    )
    print(f"Data-quality issue categories found: {len(inspection['potential_issues'])}")
    print("Cleaning results:")
    for metric, value in report.items():
        print(f"  {metric}: {value}")

    preview_columns = [
        "id", "neighbourhood_group", "room_type", "price", "availability_365"
    ]
    print("\nPreview of cleaned data:")
    print(cleaned.loc[:, preview_columns].head().to_string(index=False))
    print("\nPhase 1 complete. Analysis summaries are not yet integrated.")


if __name__ == "__main__":
    main()
