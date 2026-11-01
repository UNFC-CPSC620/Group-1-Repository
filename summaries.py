import pandas as pd


BOROUGH_COLUMN = "neighbourhood_group"
ROOM_TYPE_COLUMN = "room_type"


def _validate_dataframe(df):
    """Validate that the input contains the required summary columns."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_columns = {BOROUGH_COLUMN, ROOM_TYPE_COLUMN}
    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_columns))}"
        )


def summarize_listings_by_borough(df):
    """Return listing counts by borough, excluding missing borough values."""
    _validate_dataframe(df)

    result = (
        df.loc[df[BOROUGH_COLUMN].notna(), BOROUGH_COLUMN]
        .value_counts()
        .rename_axis("borough")
        .reset_index(name="listing_count")
    )

    return result


def summarize_listings_by_room_type(df):
    """Return listing counts by room type, excluding missing room types."""
    _validate_dataframe(df)

    result = (
        df.loc[df[ROOM_TYPE_COLUMN].notna(), ROOM_TYPE_COLUMN]
        .value_counts()
        .rename_axis("room_type")
        .reset_index(name="listing_count")
    )

    return result


def summarize_listings_by_borough_and_room_type(df):
    """Return listing counts for each valid borough and room type combination."""
    _validate_dataframe(df)

    valid_rows = df.loc[
        df[BOROUGH_COLUMN].notna()
        & df[ROOM_TYPE_COLUMN].notna(),
        [BOROUGH_COLUMN, ROOM_TYPE_COLUMN],
    ]

    result = (
        valid_rows.groupby(
            [BOROUGH_COLUMN, ROOM_TYPE_COLUMN],
            observed=True,
        )
        .size()
        .reset_index(name="listing_count")
        .rename(columns={
            BOROUGH_COLUMN: "borough",
            ROOM_TYPE_COLUMN: "room_type",
        })
        .sort_values(
            ["borough", "listing_count", "room_type"],
            ascending=[True, False, True],
            ignore_index=True,
        )
    )

    return result


def summarize_borough_percentages(df):
    """Return borough listing counts and percentages among valid boroughs."""
    _validate_dataframe(df)

    counts = summarize_listings_by_borough(df)
    total = int(counts["listing_count"].sum())

    if total == 0:
        counts["percentage"] = pd.Series(dtype="float64")
    else:
        counts["percentage"] = (
            counts["listing_count"] / total * 100
        ).round(2)

    return counts


def summarize_listings(df):
    """Return all borough and room type summaries as reusable DataFrames."""
    _validate_dataframe(df)

    return {
        "by_borough": summarize_listings_by_borough(df),
        "by_room_type": summarize_listings_by_room_type(df),
        "by_borough_and_room_type": (
            summarize_listings_by_borough_and_room_type(df)
        ),
        "borough_percentages": summarize_borough_percentages(df),
    }
