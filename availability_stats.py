"""Availability summaries for the cleaned NYC Airbnb dataset (Issue #26).

Validity rule for availability_365 (used by every function in this module)
--------------------------------------------------------------------------
A listing's availability is VALID when it is a whole number of days from 0 to
365, inclusive. Values such as "178 days" are read as 178. Missing values,
non-numeric text (e.g. "unknown"), fractional numbers, negative numbers and
numbers above 365 are INVALID and are excluded from every statistic. Rows with
a missing borough / room type are also left out of the grouped results.
"""
import pandas as pd

BOROUGH_COLUMN = "neighbourhood_group"
ROOM_TYPE_COLUMN = "room_type"
AVAILABILITY_COLUMN = "availability_365"
MIN_DAYS = 0
MAX_DAYS = 365


def _get_valid_availability_rows(df, group_column):
    """Return a copy of `df` containing only rows with valid availability.

    `availability_365` in the returned frame is a float column. The input
    DataFrame is never modified.

    Raises TypeError if `df` is not a DataFrame and KeyError if a required
    column is missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__}.")
    missing = [c for c in (group_column, AVAILABILITY_COLUMN) if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required column(s): {', '.join(missing)}")

    text = (
        df[AVAILABILITY_COLUMN]
        .astype("string")
        .str.strip()
        .str.replace(r"(?i)\s*days?$", "", regex=True)
    )
    is_whole_number = text.str.fullmatch(r"\d+(?:\.0+)?").fillna(False).astype(bool)
    days = pd.to_numeric(text.where(is_whole_number), errors="coerce").astype("float64")

    valid = days.between(MIN_DAYS, MAX_DAYS) & df[group_column].notna()
    result = df.loc[valid].copy()
    result[AVAILABILITY_COLUMN] = days[valid]
    return result


def availability_stats_by_borough(df):
    """Count, average and median annual availability for each borough.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned listings with `neighbourhood_group` and `availability_365`.

    Returns
    -------
    pandas.DataFrame
        Columns: neighbourhood_group, valid_listings, mean_availability,
        median_availability (days per year). Sorted by valid_listings, largest
        first. Empty, with the same columns, if there are no valid values.
    """
    columns = [BOROUGH_COLUMN, "valid_listings", "mean_availability", "median_availability"]
    valid = _get_valid_availability_rows(df, BOROUGH_COLUMN)
    if valid.empty:
        return pd.DataFrame(columns=columns)

    return (
        valid.groupby(BOROUGH_COLUMN)[AVAILABILITY_COLUMN]
        .agg(valid_listings="count", mean_availability="mean", median_availability="median")
        .round(2)
        .reset_index()
        .sort_values("valid_listings", ascending=False)
        .reset_index(drop=True)
    )


def availability_stats_by_room_type(df):
    """Count and average annual availability for each room type.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned listings with `room_type` and `availability_365`.

    Returns
    -------
    pandas.DataFrame
        Columns: room_type, valid_listings, mean_availability (days per year).
        Sorted by valid_listings, largest first. Empty, with the same columns,
        if there are no valid values.
    """
    columns = [ROOM_TYPE_COLUMN, "valid_listings", "mean_availability"]
    valid = _get_valid_availability_rows(df, ROOM_TYPE_COLUMN)
    if valid.empty:
        return pd.DataFrame(columns=columns)

    return (
        valid.groupby(ROOM_TYPE_COLUMN)[AVAILABILITY_COLUMN]
        .agg(valid_listings="count", mean_availability="mean")
        .round(2)
        .reset_index()
        .sort_values("valid_listings", ascending=False)
        .reset_index(drop=True)
    )
