# Group-1
Collaborative Data Analytics team project focused on organized development, consistent GitHub contributions, and transparent teamwork. Due November 1, 2026.

## Airbnb Pricing Summaries
The pricing summary module calculates valid listing counts, average prices, and median prices by borough and room type using the cleaned NYC Airbnb dataset.

### Requirements
- Python 3
- pandas

### Usage
Run the pricing summary module from the project directory:

```bash
python pricing_summaries.py
```

The script loads `Airbnb_NYC.csv`, cleans the dataset using `clean_airbnb_data()` from `cleaning.py`, and prints pricing summaries by borough and room type.

### Reusable Functions
- `summarize_prices_by_borough(cleaned_df)`: calculates valid listing counts, average prices, and median prices by borough.
- `summarize_prices_by_room_type(cleaned_df)`: calculates valid listing counts, average prices, and median prices by room type.
- `generate_pricing_summaries(raw_df)`: cleans the raw dataset and returns the cleaned data and both pricing summary DataFrames.

Missing and invalid prices are excluded from the pricing summaries.
