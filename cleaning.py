"""Reusable cleaning functions for the CPSC-620 NYC Airbnb summary tool.

Issue #8 - clean and validate NYC Airbnb data.

Design principles:
* Preserve the original DataFrame; return a new cleaned copy.
* Do not invent price or availability values.
* Standardize known categories only; unknown categories remain missing.
* For duplicate listing IDs, retain the first occurrence in original row order.
"""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "id", "price", "neighbourhood_group", "room_type", "availability_365"
}

BOROUGH_NAMES = {
    "manhattan": "Manhattan",
    "brooklyn": "Brooklyn",
    "queens": "Queens",
    "bronx": "Bronx",
    "staten island": "Staten Island",
}

ROOM_TYPES = {
    "entire home/apt": "Entire home/apt",
    "private room": "Private room",
    "shared room": "Shared room",
}


def parse_price(values: pd.Series) -> pd.Series:
    """Convert supported nightly USD prices to numbers; invalid/zero prices become NA.

    Supported examples: 100, $100, $1,000, USD 63, $ 70 / night.
    Unexpected text is rejected instead of extracting an unrelated number.
    """
    text = values.astype("string").str.strip()
    text = text.str.replace(r"(?i)^(?:USD|\$)\s*", "", regex=True)
    text = text.str.replace(r"(?i)\s*/\s*night$", "", regex=True)
    is_numeric_price = text.str.fullmatch(
        r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?"
    ).fillna(False)
    parsed = pd.to_numeric(
        text.where(is_numeric_price).str.replace(",", "", regex=False),
        errors="coerce",
    )
    return parsed.where(parsed > 0).astype("Float64")


def parse_count(values: pd.Series, suffix: str | None = None) -> pd.Series:
    """Parse whole-number quantities, optionally removing a known unit suffix.

    Invalid, negative, or fractional counts are represented by nullable NA.
    """
    text = values.astype("string").str.strip()
    if suffix == "nights":
        text = text.str.replace(r"(?i)\s*nights?$", "", regex=True)
    elif suffix == "days":
        text = text.str.replace(r"(?i)\s*days?$", "", regex=True)
    is_whole_number = text.str.fullmatch(r"\d+").fillna(False)
    return pd.to_numeric(text.where(is_whole_number), errors="coerce").astype("Int64")


def standardize_category(values: pd.Series, labels: dict[str, str]) -> pd.Series:
    """Strip/case-normalize labels and map recognized values to canonical names."""
    return values.astype("string").str.strip().str.casefold().map(labels).astype("string")


def clean_airbnb_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a validated, cleaned Airbnb DataFrame without changing `raw`.

    Rules:
    - Deduplicate by listing `id`, retaining first row (source order).
    - Normalize borough and room type; unexpected categories become NA.
    - Convert positive nightly prices to nullable Float64; invalid/zero -> NA.
    - Normalize minimum nights to positive nullable whole numbers.
    - Normalize availability to integer 0..365; invalid values -> NA.
    - Convert reviews per month to numeric; missing/unknown values stay NA,
      except listings with zero reviews: missing review rates become 0.
    - Keep missing names/host names missing rather than inventing values.
    """
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing required Airbnb columns: {', '.join(sorted(missing))}")

    cleaned = raw.copy(deep=True)
    cleaned = cleaned.drop_duplicates(subset="id", keep="first").reset_index(drop=True)

    cleaned["neighbourhood_group"] = standardize_category(
        cleaned["neighbourhood_group"], BOROUGH_NAMES
    )
    cleaned["room_type"] = standardize_category(cleaned["room_type"], ROOM_TYPES)
    cleaned["price"] = parse_price(cleaned["price"])

    if "minimum_nights" in cleaned.columns:
        nights = parse_count(cleaned["minimum_nights"], suffix="nights")
        cleaned["minimum_nights"] = nights.where(nights >= 1)

    availability = parse_count(cleaned["availability_365"], suffix="days")
    cleaned["availability_365"] = availability.where(availability.between(0, 365))

    if "reviews_per_month" in cleaned.columns:
        reviews = pd.to_numeric(cleaned["reviews_per_month"], errors="coerce")
        reviews = reviews.where(reviews >= 0)
        if "number_of_reviews" in cleaned.columns:
            no_reviews = pd.to_numeric(
                cleaned["number_of_reviews"], errors="coerce"
            ).eq(0)
            reviews = reviews.mask(no_reviews & reviews.isna(), 0)
        cleaned["reviews_per_month"] = reviews.astype("Float64")

    if "last_review" in cleaned.columns:
        cleaned["last_review"] = pd.to_datetime(
            cleaned["last_review"], errors="coerce"
        )

    return cleaned


def cleaning_report(original: pd.DataFrame, cleaned: pd.DataFrame) -> dict:
    """Return measurable cleaning outcomes for demos, reports, and tests."""
    return {
        "original_rows": len(original),
        "cleaned_rows": len(cleaned),
        "duplicate_listings_removed": len(original) - len(cleaned),
        "missing_cleaned_prices": int(cleaned["price"].isna().sum()),
        "missing_cleaned_availability": int(cleaned["availability_365"].isna().sum()),
        "unknown_borough_labels": int(cleaned["neighbourhood_group"].isna().sum()),
        "unknown_room_type_labels": int(cleaned["room_type"].isna().sum()),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean the NYC Airbnb dataset")
    parser.add_argument("--input", default="Airbnb_NYC.csv", help="Source CSV path")
    parser.add_argument("--output", default=None, help="Optional cleaned CSV output")
    args = parser.parse_args()

    source = pd.read_csv(args.input, low_memory=False)
    result = clean_airbnb_data(source)
    for metric, value in cleaning_report(source, result).items():
        print(f"{metric}: {value}")
    if args.output:
        result.to_csv(args.output, index=False)
        print(f"Clean data saved to: {args.output}")
