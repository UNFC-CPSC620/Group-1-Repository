
from pathlib import Path

import pandas as pd


NUMERIC_LIKE_COLUMNS = (
    "id",
    "host_id",
    "latitude",
    "longitude",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
)

RANGE_CHECKS = {
    "latitude": (-90, 90),
    "longitude": (-180, 180),
    "price": (0, None),
    "minimum_nights": (1, None),
    "number_of_reviews": (0, None),
    "reviews_per_month": (0, None),
    "calculated_host_listings_count": (1, None),
    "availability_365": (0, 365),
}

CATEGORICAL_COLUMNS = (
    "neighbourhood_group",
    "neighbourhood",
    "room_type",
)


def load_dataset(file_path="Airbnb_NYC.csv"):
    """Load a CSV dataset and return it as a pandas DataFrame."""
    path = Path(file_path)

    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return pd.read_csv(path)


def _normalize_numeric_values(series):
    """Normalize common currency symbols and units before numeric conversion."""
    values = series.astype("string").str.strip()
    values = values.str.replace(r"(?i)\bUSD\b", "", regex=True)
    values = values.str.replace("$", "", regex=False)
    values = values.str.replace(",", "", regex=False)
    values = values.str.replace(
        r"(?i)\s*/\s*(night|day|month|year)\b", "", regex=True
    )
    values = values.str.replace(
        r"(?i)\b(nights?|days?)\b", "", regex=True
    )
    return values.str.strip()


def inspect_dataset(df):
    """Inspect dataset structure and return reusable data-quality results."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing_values = {
        column: int(count)
        for column, count in df.isna().sum().items()
    }

    missing_percentages = {
        column: round(float(df[column].isna().mean() * 100), 2)
        for column in df.columns
    }

    duplicate_rows = int(df.duplicated().sum())
    duplicate_row_indices = df.index[
        df.duplicated(keep=False)
    ].tolist()

    id_column = next(
        (
            column
            for column in ("id", "listing_id")
            if column in df.columns
        ),
        None,
    )

    duplicate_listing_ids = None
    duplicate_listing_id_values = []
    missing_listing_ids = None

    if id_column is not None:
        ids = df[id_column]
        duplicate_listing_ids = int(
            ids.dropna().duplicated().sum()
        )
        duplicate_listing_id_values = (
            ids[ids.notna() & ids.duplicated(keep=False)]
            .drop_duplicates()
            .tolist()
        )
        missing_listing_ids = int(ids.isna().sum())

    numeric_columns = [
        column
        for column in NUMERIC_LIKE_COLUMNS
        if column in df.columns
    ]

    non_numeric_values = {}
    formatting_issues = {}
    range_violations = {}

    for column in numeric_columns:
        original = df[column]
        normalized = _normalize_numeric_values(original)
        converted = pd.to_numeric(normalized, errors="coerce")

        non_numeric_mask = original.notna() & converted.isna()

        if non_numeric_mask.any():
            non_numeric_values[column] = {
                "count": int(non_numeric_mask.sum()),
                "examples": (
                    original[non_numeric_mask]
                    .astype(str)
                    .drop_duplicates()
                    .head(5)
                    .tolist()
                ),
            }

        original_as_numeric = pd.to_numeric(
            original, errors="coerce"
        )
        formatting_mask = (
            original.notna()
            & original_as_numeric.isna()
            & converted.notna()
        )

        if formatting_mask.any():
            formatting_issues[column] = {
                "count": int(formatting_mask.sum()),
                "examples": (
                    original[formatting_mask]
                    .astype(str)
                    .drop_duplicates()
                    .head(5)
                    .tolist()
                ),
            }

        if column in RANGE_CHECKS:
            minimum, maximum = RANGE_CHECKS[column]
            invalid_mask = converted.notna() & False

            if minimum is not None:
                invalid_mask = invalid_mask | (
                    converted < minimum
                )

            if maximum is not None:
                invalid_mask = invalid_mask | (
                    converted > maximum
                )

            if invalid_mask.any():
                range_violations[column] = {
                    "count": int(invalid_mask.sum()),
                    "examples": (
                        original[invalid_mask]
                        .astype(str)
                        .drop_duplicates()
                        .head(5)
                        .tolist()
                    ),
                    "minimum_allowed": minimum,
                    "maximum_allowed": maximum,
                }

    invalid_dates = {}

    if "last_review" in df.columns:
        dates = df["last_review"]
        parsed_dates = pd.to_datetime(
            dates, errors="coerce", format="mixed"
        )
        invalid_date_mask = dates.notna() & parsed_dates.isna()

        if invalid_date_mask.any():
            invalid_dates["last_review"] = {
                "count": int(invalid_date_mask.sum()),
                "examples": (
                    dates[invalid_date_mask]
                    .astype(str)
                    .drop_duplicates()
                    .head(5)
                    .tolist()
                ),
            }

    categorical_formatting_issues = {}

    for column in CATEGORICAL_COLUMNS:
        if column not in df.columns:
            continue

        values = df[column].dropna().astype(str)
        whitespace_mask = values.ne(values.str.strip())
        normalized_values = values.str.strip().str.casefold()
        case_variants = {}

        for normalized_value in normalized_values.drop_duplicates():
            variants = (
                values[normalized_values == normalized_value]
                .drop_duplicates()
                .tolist()
            )

            if len(variants) > 1:
                case_variants[normalized_value] = variants[:5]

        if whitespace_mask.any() or case_variants:
            categorical_formatting_issues[column] = {
                "leading_or_trailing_whitespace_count": int(
                    whitespace_mask.sum()
                ),
                "case_variants": case_variants,
            }

    potential_issues = []

    missing_columns = {
        column: count
        for column, count in missing_values.items()
        if count > 0
    }

    if missing_columns:
        potential_issues.append({
            "type": "missing_values",
            "details": missing_columns,
        })

    if duplicate_rows:
        potential_issues.append({
            "type": "duplicate_rows",
            "count": duplicate_rows,
            "indices": duplicate_row_indices[:20],
        })

    if id_column is None:
        potential_issues.append({
            "type": "missing_id_column",
            "details": "Neither 'id' nor 'listing_id' exists.",
        })
    else:
        if duplicate_listing_ids:
            potential_issues.append({
                "type": "duplicate_listing_ids",
                "column": id_column,
                "count": duplicate_listing_ids,
                "distinct_ids_affected": len(
                    duplicate_listing_id_values
                ),
                "examples": duplicate_listing_id_values[:10],
            })

        if missing_listing_ids:
            potential_issues.append({
                "type": "missing_listing_ids",
                "column": id_column,
                "count": missing_listing_ids,
            })

    if non_numeric_values:
        potential_issues.append({
            "type": "non_numeric_values_in_numeric_like_columns",
            "details": non_numeric_values,
        })

    if formatting_issues:
        potential_issues.append({
            "type": "inconsistent_numeric_formatting",
            "details": formatting_issues,
        })

    if range_violations:
        potential_issues.append({
            "type": "values_out_of_expected_range",
            "details": range_violations,
        })

    if invalid_dates:
        potential_issues.append({
            "type": "invalid_dates",
            "details": invalid_dates,
        })

    if categorical_formatting_issues:
        potential_issues.append({
            "type": "inconsistent_categorical_formatting",
            "details": categorical_formatting_issues,
        })

    return {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": missing_values,
        "missing_percentages": missing_percentages,
        "duplicate_rows": duplicate_rows,
        "duplicate_row_indices": duplicate_row_indices,
        "id_column": id_column,
        "duplicate_listing_ids": duplicate_listing_ids,
        "duplicate_listing_id_values": duplicate_listing_id_values,
        "missing_listing_ids": missing_listing_ids,
        "non_numeric_values": non_numeric_values,
        "numeric_formatting_issues": formatting_issues,
        "range_violations": range_violations,
        "invalid_dates": invalid_dates,
        "categorical_formatting_issues": categorical_formatting_issues,
        "potential_issues": potential_issues,
    }


if __name__ == "__main__":
    dataset = load_dataset()
    results = inspect_dataset(dataset)

    print(
        f"Dataset dimensions: {results['total_rows']} rows x "
        f"{results['total_columns']} columns"
    )

    print("\nColumn names and data types:")
    print(pd.DataFrame({
        "column": results["column_names"],
        "data_type": [
            results["data_types"][column]
            for column in results["column_names"]
        ],
    }).to_string(index=False))

    print("\nMissing values by column:")
    print(pd.DataFrame({
        "missing_values": results["missing_values"],
        "missing_percentage": results["missing_percentages"],
    }).to_string())

    print(f"\nDuplicate rows: {results['duplicate_rows']}")
    print(
        "Duplicate listing ID occurrences: "
        f"{results['duplicate_listing_ids']}"
    )
    print(
        "Distinct listing IDs affected: "
        f"{len(results['duplicate_listing_id_values'])}"
    )

    print("\nPotential data-quality issues:")

    if results["potential_issues"]:
        for issue in results["potential_issues"]:
            print(issue)
    else:
        print("No issues detected by the checks performed.")

    print("\nDataset preview:")
    print(dataset.head())
