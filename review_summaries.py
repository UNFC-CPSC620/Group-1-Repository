import pandas as pd


BOROUGH_COLUMN = "neighbourhood_group"
ROOM_TYPE_COLUMN = "room_type"
NUMBER_OF_REVIEWS_COLUMN = "number_of_reviews"
REVIEWS_PER_MONTH_COLUMN = "reviews_per_month"


def _validate_dataframe(df, required_columns):
    """Validate the DataFrame and required columns."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing_columns = set(required_columns).difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_columns))}"
        )


def _valid_review_values(values):
    """Convert review values to numeric and exclude negative values."""
    numeric_values = pd.to_numeric(values, errors="coerce")
    return numeric_values.where(numeric_values >= 0)


def summarize_reviews_by_borough(df):
    """Return average and median review counts by borough."""
    _validate_dataframe(
        df, [BOROUGH_COLUMN, NUMBER_OF_REVIEWS_COLUMN]
    )

    data = df[[BOROUGH_COLUMN, NUMBER_OF_REVIEWS_COLUMN]].copy()
    data[NUMBER_OF_REVIEWS_COLUMN] = _valid_review_values(
        data[NUMBER_OF_REVIEWS_COLUMN]
    )
    data = data.dropna(
        subset=[BOROUGH_COLUMN, NUMBER_OF_REVIEWS_COLUMN]
    )

    return (
        data.groupby(BOROUGH_COLUMN)[NUMBER_OF_REVIEWS_COLUMN]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={
            BOROUGH_COLUMN: "borough",
            "mean": "average_reviews",
            "median": "median_reviews",
            "count": "valid_listing_count",
        })
        .sort_values("borough", ignore_index=True)
    )


def summarize_reviews_by_room_type(df):
    """Return review activity summaries by room type."""
    _validate_dataframe(
        df,
        [
            ROOM_TYPE_COLUMN,
            NUMBER_OF_REVIEWS_COLUMN,
            REVIEWS_PER_MONTH_COLUMN,
        ],
    )

    data = df[
        [
            ROOM_TYPE_COLUMN,
            NUMBER_OF_REVIEWS_COLUMN,
            REVIEWS_PER_MONTH_COLUMN,
        ]
    ].copy()

    data[NUMBER_OF_REVIEWS_COLUMN] = _valid_review_values(
        data[NUMBER_OF_REVIEWS_COLUMN]
    )
    data[REVIEWS_PER_MONTH_COLUMN] = _valid_review_values(
        data[REVIEWS_PER_MONTH_COLUMN]
    )
    data = data.dropna(subset=[ROOM_TYPE_COLUMN])

    return (
        data.groupby(ROOM_TYPE_COLUMN)
        .agg(
            average_reviews=(NUMBER_OF_REVIEWS_COLUMN, "mean"),
            median_reviews=(NUMBER_OF_REVIEWS_COLUMN, "median"),
            average_reviews_per_month=(REVIEWS_PER_MONTH_COLUMN, "mean"),
            valid_review_count=(NUMBER_OF_REVIEWS_COLUMN, "count"),
            valid_monthly_rate_count=(REVIEWS_PER_MONTH_COLUMN, "count"),
        )
        .reset_index()
        .rename(columns={ROOM_TYPE_COLUMN: "room_type"})
        .sort_values("room_type", ignore_index=True)
    )


def summarize_reviews(df):
    """Return all review activity summaries."""
    _validate_dataframe(
        df,
        [
            BOROUGH_COLUMN,
            ROOM_TYPE_COLUMN,
            NUMBER_OF_REVIEWS_COLUMN,
            REVIEWS_PER_MONTH_COLUMN,
        ],
    )

    return {
        "by_borough": summarize_reviews_by_borough(df),
        "by_room_type": summarize_reviews_by_room_type(df),
    }


if __name__ == "__main__":
    from pathlib import Path
    from cleaning import clean_airbnb_data

    dataset_path = Path(__file__).resolve().parent / "Airbnb_NYC.csv"

    raw_df = pd.read_csv(dataset_path, low_memory=False)
    cleaned_df = clean_airbnb_data(raw_df)

    results = summarize_reviews(cleaned_df)

    print("NYC Airbnb Review Activity Summaries")
    print(f"Original listings: {len(raw_df)}")
    print(f"Cleaned listings: {len(cleaned_df)}")

    for name, summary in results.items():
        print(f"\n{name.replace('_', ' ').title()}")
        print(summary.to_string(index=False))
