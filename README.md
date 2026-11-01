# NYC Airbnb Data Summary Tool

CPSC 620, Group 1. A small, modular Python toolkit that loads the NYC Airbnb listings dataset (`Airbnb_NYC.csv`), cleans it, and returns ready-to-use summary tables (pandas DataFrames) for pricing, availability, boroughs and room types. There is no dashboard or UI; the functions are designed to be reused by one later.

> **Draft note for the author:** items in `[BRACKETS]` depend on pull requests that are not on `main` yet (pricing, availability, borough/room-type, pipeline). Fill them in after those merge, then delete this note.

## Objectives

- Load and inspect the provided listings dataset.
- Clean messy real-world values (duplicates, mixed formats, invalid numbers) with documented rules.
- Produce reusable summaries of price and availability by borough and room type.
- Keep every step modular, documented and covered by automated tests.

## Requirements

- **Python 3.11 or newer** (the project's automated checks run on 3.11).
- **pandas** (see `requirements.txt`; NumPy is installed with it).
- The dataset file `Airbnb_NYC.csv`, placed in the repository's main folder.

## Installation

```bash
git clone https://github.com/UNFC-CPSC620/Group-1-Repository.git
cd Group-1-Repository
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Project structure

| File | Purpose |
|---|---|
| `data_loader.py` | `load_airbnb_data(file_path)`: reads the CSV into a DataFrame with clear errors for missing, empty or invalid files (Issue #5). |
| `data_inspection.py` | `load_dataset(file_path)` and `inspect_dataset(df)`: report shape, column types, missing values, duplicates, non-numeric and out-of-range values and inconsistent formatting, returned as a dictionary. Run as a script it prints a readable report (Issue #7). |
| `cleaning.py` | `clean_airbnb_data(raw)` and `cleaning_report(original, cleaned)`: apply the cleaning rules below. Run as a script it prints the cleaning report (Issue #8). |
| `pricing_summaries.py` | `summarize_prices_by_borough`, `summarize_prices_by_room_type`, `generate_pricing_summaries(raw)`: count, average and median of valid prices (PR #25). |
| `availability_stats.py` | `availability_stats_by_borough`, `availability_stats_by_room_type`: count, mean and median of valid availability (Issue #26). |
| `summaries.py` | `summarize_listings_by_borough`, `summarize_listings_by_room_type`, `summarize_listings_by_borough_and_room_type`, `summarize_borough_percentages`, `summarize_listings`: listing counts and percentages (Issue #20, PR #23). |
| `run_analysis.py` | `run_pipeline(file_path)` and a command-line entry point. Phase 1 loads, inspects and cleans the dataset and prints a short report; summaries are not connected yet (Issue #30, PR #36). |
| `tests/` | Automated `unittest` tests, one file per module. |
| `docs/cleaning-decisions.md` | Recorded data-cleaning decisions (Issue #11). |
| `.github/workflows/python-tests.yml` | Continuous integration (Python 3.11): installs pandas, runs the unit tests and validates the full dataset with `cleaning.py` on every pull request to `main` (Issue #11). |
| `Airbnb_NYC.csv` | The dataset (42,336 rows, 16 columns). |
| `requirements.txt` | Python dependencies. |

## Workflow sequence

1. **Load:** `load_airbnb_data("Airbnb_NYC.csv")` returns the raw table (42,336 rows, 16 columns). Nothing is changed.
2. **Inspect:** `inspect_dataset(raw)` reports shape, data types, missing values, duplicates and formatting problems (see `data_inspection.py`).
3. **Clean:** `clean_airbnb_data(raw)` returns a new cleaned DataFrame and never modifies `raw`.
4. **Analyse:** pass the cleaned DataFrame to the summary functions.

## How to run

Place `Airbnb_NYC.csv` in the main folder, then use any of these.

**Inspect the raw data** (prints dimensions, column types, missing values and detected issues):

```bash
python data_inspection.py
```

**Clean the data** (prints the cleaning report; add `--output` to save the cleaned CSV):

```bash
python cleaning.py --input Airbnb_NYC.csv
python cleaning.py --input Airbnb_NYC.csv --output cleaned_Airbnb_NYC.csv
```

### Borough and Room-Type Summaries

The `summaries.py` module generates reusable listing summaries
using the cleaned NYC Airbnb dataset.

From the repository root, run:

```bash
python summaries.py
```

The script automatically:

1. Loads `Airbnb_NYC.csv`.
2. Cleans the dataset using `clean_airbnb_data()` from `cleaning.py`.
3. Removes duplicate listing IDs according to the cleaning policy.
4. Standardizes recognized borough and room-type categories.
5. Generates and displays four summary DataFrames:
   - Listing counts by borough.
   - Listing counts by room type.
   - Listing counts by borough and room-type combination.
   - Borough percentage distributions.

Missing or unrecognized categories are excluded from the
corresponding group calculations.

The original CSV file is not modified.

#### Reusing the Functions

```python
from data_loader import load_airbnb_data
from cleaning import clean_airbnb_data
from summaries import summarize_listings

raw = load_airbnb_data("Airbnb_NYC.csv")
cleaned = clean_airbnb_data(raw)

results = summarize_listings(cleaned)

print(results["by_borough"])
print(results["by_room_type"])
print(results["by_borough_and_room_type"])
print(results["borough_percentages"])
```

#### Automated Tests

Run the existing test suite:

```bash
python -m unittest discover -s tests -v
```

The tests cover listing counts, borough percentages, missing
categories, empty DataFrames, required columns, and preservation
of the original input DataFrame.

Related work:
- Issue #17 — Borough and room-type user story.
- Issue #18 — Summary implementation.
- Issue #19 — Automated summary tests.
- Issue #20 — Documentation and integration.
- PR #23 — Summary functions and tests merged into main.
- PR #38 — Automated tests merged into the implementation branch.

**Run the summaries** with the reusable functions on the cleaned data:

```python
from data_loader import load_airbnb_data
from cleaning import clean_airbnb_data
from pricing_summaries import summarize_prices_by_borough
from availability_stats import availability_stats_by_borough  # [once merged]

raw = load_airbnb_data("Airbnb_NYC.csv")
clean = clean_airbnb_data(raw)
print(summarize_prices_by_borough(clean))
print(availability_stats_by_borough(clean))
```

**Run the pipeline** (load, inspect, clean, and print a report; this is Phase 1 of Issue #30):

```bash
python run_analysis.py
python run_analysis.py --input Airbnb_NYC.csv
```

Example output on the full dataset:

```
NYC Airbnb Analytics — Phase 1
Original dataset: 42336 rows x 16 columns
Data-quality issue categories found: 8
Cleaning results:
  original_rows: 42336
  cleaned_rows: 42000
  duplicate_listings_removed: 336
  missing_cleaned_prices: 10
  missing_cleaned_availability: 82
  unknown_borough_labels: 0
  unknown_room_type_labels: 0
```

`run_pipeline()` returns a dictionary with `original_data`, `cleaned_data`, `inspection` and `cleaning_report`, so later stages (pricing, listing, availability and review summaries) can reuse it. These summaries are **not yet connected** to `run_analysis.py`; call them separately as shown below. `[Update this paragraph if PR #36 or a later PR connects them.]`

## Running the tests

```bash
python -m unittest discover -s tests -v
```

All tests should report `OK`. GitHub Actions (`python-tests.yml`) runs the same command, plus `python cleaning.py --input Airbnb_NYC.csv`, on every pull request to `main`.

## Output format

Every summary function returns a `pandas.DataFrame` with one row per group (borough or room type), sorted by the number of valid listings, largest first. Statistics are rounded to 2 decimals. If there is nothing valid to summarise, an empty DataFrame with the same columns is returned.

**Price by borough** (`summarize_prices_by_borough`, USD per night):

| borough | valid_listing_count | average_price | median_price |
|---|---|---|---|
| Manhattan | 18605 | 198.89 | 150.0 |
| Brooklyn | 17262 | 124.70 | 90.0 |
| Queens | 4866 | 100.66 | 75.0 |
| Bronx | 937 | 87.55 | 65.0 |
| Staten Island | 320 | 116.10 | 75.0 |

**Availability by borough** (`availability_stats_by_borough`, days per year):

| neighbourhood_group | valid_listings | mean_availability | median_availability |
|---|---|---|---|
| Manhattan | 18568 | 111.93 | 36.0 |
| Brooklyn | 17239 | 100.42 | 28.0 |
| Queens | 4855 | 145.54 | 103.0 |
| Bronx | 936 | 167.61 | 150.0 |
| Staten Island | 320 | 198.36 | 207.0 |

(`[Price columns above use the names in PR #25; re-run on the merged code to confirm the values.]` Figures come from the full `Airbnb_NYC.csv` after cleaning. `[Re-run on the merged code and update if they differ.]`)

## Data-cleaning decisions

Full record: [`docs/cleaning-decisions.md`](docs/cleaning-decisions.md). Summary:

| Issue in the raw data | Rule applied |
|---|---|
| 336 duplicate listing ids | Keep the first occurrence of each `id`. |
| Borough and room type written in many cases and with extra spaces | Trim and match case-insensitively to 5 boroughs and 3 room types; anything else becomes missing. |
| Prices such as `$1,000`, `USD 63`, `$ 70 / night` | Converted to numbers. Missing, zero or unrecognised prices become missing and are excluded from price statistics. |
| `minimum_nights` as `4 nights`; `availability_365` as `178 days` | Unit text removed; invalid values become missing. |
| `availability_365` outside 0 to 365 | Treated as invalid and excluded. |
| `reviews_per_month` missing | Set to 0 only when the listing has 0 reviews; otherwise left missing. |
| Missing names and host names | Left missing, not invented. |

Output of `python cleaning.py --input Airbnb_NYC.csv` on the full dataset:

```
original_rows: 42336
cleaned_rows: 42000
duplicate_listings_removed: 336
missing_cleaned_prices: 10
missing_cleaned_availability: 82
unknown_borough_labels: 0
unknown_room_type_labels: 0
```

## Assumptions and limitations

- Price and availability are never estimated or filled in; invalid values are excluded, so group counts differ slightly between summaries.
- Prices are nightly USD as listed, including extreme values (up to about $10,000). Medians are more robust than means here.
- The dataset is a single snapshot; results do not describe a particular year or booking pattern.
- Availability is the host-set number of open days, not actual bookings.

## Related issues and pull requests

- Parent story: #29 (Integrate and validate the complete analytics workflow); pipeline #30; end-to-end validation #31.
- Inspection #7; loader #5 (PR #24); cleaning #8; CI and cleaning docs #11; pricing #16; borough and room type #20; availability #26.
- Pull requests: #4 (initial exploration), #23 (borough and room type), #24 (loader), #25 (pricing), #36 (pipeline), #38 (borough and room-type tests), #39 (availability). `[Remove any that are not merged.]`

## Team and workflow

Work was planned as one sprint in the GitHub Project "Group 1 Project". Each change was developed on a feature branch, linked to its issue, and merged through a reviewed pull request.

**Team (GitHub):**
- [@dianamelisavs96](https://github.com/dianamelisavs96)
- [@SamMbadiwe](https://github.com/SamMbadiwe)
- Cristhian Moisés Martínez ([@ChrisMoises](https://github.com/ChrisMoises))
- [@oladipoimelda-dev](https://github.com/oladipoimelda-dev)
