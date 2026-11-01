import pandas as pd

from cleaning import clean_airbnb_data


def summarize_prices_by_borough(cleaned_df):
    """Return valid listing counts, average prices, and median prices by borough."""
    if not isinstance(cleaned_df, pd.DataFrame):
        raise TypeError("cleaned_df must be a pandas DataFrame")

    required = {"neighbourhood_group", "price"}
    missing = required.difference(cleaned_df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    valid = cleaned_df.loc[
        cleaned_df["neighbourhood_group"].notna()
        & cleaned_df["price"].notna()
        & cleaned_df["price"].gt(0),
        ["neighbourhood_group", "price"],
    ]

    return (
        valid.groupby("neighbourhood_group")["price"]
        .agg(
            valid_listing_count="count",
            average_price="mean",
            median_price="median",
        )
        .reset_index()
        .rename(columns={"neighbourhood_group": "borough"})
        .sort_values("borough", ignore_index=True)
        .round({"average_price": 2, "median_price": 2})
    )


def summarize_prices_by_room_type(cleaned_df):
    """Return valid listing counts, average prices, and median prices by room type."""
    if not isinstance(cleaned_df, pd.DataFrame):
        raise TypeError("cleaned_df must be a pandas DataFrame")

    required = {"room_type", "price"}
    missing = required.difference(cleaned_df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    valid = cleaned_df.loc[
        cleaned_df["room_type"].notna()
        & cleaned_df["price"].notna()
        & cleaned_df["price"].gt(0),
        ["room_type", "price"],
    ]

    return (
        valid.groupby("room_type")["price"]
        .agg(
            valid_listing_count="count",
            average_price="mean",
            median_price="median",
        )
        .reset_index()
        .sort_values("room_type", ignore_index=True)
        .round({"average_price": 2, "median_price": 2})
    )


def generate_pricing_summaries(raw_df):
    """Clean the raw Airbnb dataset and return reusable pricing summary DataFrames."""
    cleaned_df = clean_airbnb_data(raw_df)

    return {
        "cleaned_data": cleaned_df,
        "by_borough": summarize_prices_by_borough(cleaned_df),
        "by_room_type": summarize_prices_by_room_type(cleaned_df),
    }


if __name__ == "__main__":
    from pathlib import Path

    dataset_path = Path(__file__).resolve().parent / "Airbnb_NYC.csv"
    raw_df = pd.read_csv(dataset_path, low_memory=False)
    results = generate_pricing_summaries(raw_df)

    print("\nPricing summary by borough:")
    print(results["by_borough"].to_string(index=False))

    print("\nPricing summary by room type:")
    print(results["by_room_type"].to_string(index=False))
