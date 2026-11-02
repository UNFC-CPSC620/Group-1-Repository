import pandas as pd


BOROUGH_COLUMN = "neighbourhood_group"
ROOM_TYPE_COLUMN = "room_type"
NUMBER_OF_REVIEWS_COLUMN = "number_of_reviews"
REVIEWS_PER_MONTH_COLUMN = "reviews_per_month"


def _validate_dataframe(df, required_columns):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing_columns = set(required_columns).difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_columns))}"
        )


def _valid_review_values(values):
    numeric_values = pd.to_numeric(values, errors="coerce")
    return numeric_values.where(numeric_values >= 0)


def summarize_reviews_by_borough(df):
    """Summarize lifetime review counts by borough."""
    _validate_dataframe(
        df, [BOROUGH_COLUMN, NUMBER_OF_REVIEWS_COLUMN]
    )

    data = df[[BOROUGH_COLUMN, NUMBER_OF_REVIEWS_COLUMN]].copy()
    data[NUMBER_OF_REVIEWS_COLUMN] = _valid_review_values(
        data[NUMBER_OF_REVIEWS_COLUMN]
    )
    data = data.dropna(subset=[BOROUGH_COLUMN])

    return (
        data.groupby(BOROUGH_COLUMN)
        .agg(
            average_reviews=(NUMBER_OF_REVIEWS_COLUMN, "mean"),
            median_reviews=(NUMBER_OF_REVIEWS_COLUMN, "median"),
            valid_listing_count=(NUMBER_OF_REVIEWS_COLUMN, "count"),
            missing_review_count=(NUMBER_OF_REVIEWS_COLUMN, lambda x: x.isna().sum()),
        )
        .reset_index()
        .rename(columns={BOROUGH_COLUMN: "borough"})
        .sort_values("borough", ignore_index=True)
    )


def summarize_reviews_by_room_type(df):
    """Summarize lifetime reviews and monthly review rates by room type."""
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
            missing_review_count=(NUMBER_OF_REVIEWS_COLUMN, lambda x: x.isna().sum()),
            valid_monthly_rate_count=(REVIEWS_PER_MONTH_COLUMN, "count"),
            missing_monthly_rate_count=(REVIEWS_PER_MONTH_COLUMN, lambda x: x.isna().sum()),
        )
        .reset_index()
        .rename(columns={ROOM_TYPE_COLUMN: "room_type"})
        .sort_values("room_type", ignore_index=True)
    )


def summarize_reviews(df):
    """Return review activity summaries by borough and room type."""
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
