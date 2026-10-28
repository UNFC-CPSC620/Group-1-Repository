# NYC Airbnb Data Cleaning — Decisions and Validation

**Course:** CPSC-620 Agile Software Development  
**Project:** NYC Airbnb Data Summary Tool  
**Group:** Group 1  
**Contributor:** SamMbadiwe  
**User Story:** #8 — Clean and validate NYC Airbnb data  
**Related Tasks:** #9, #10, #11  
**Sprint:** October 23–29, 2026

## 1. Purpose

This module prepares the NYC Airbnb dataset for accurate, reliable analysis. The cleaning functions address inconsistent formats, duplicate listings, missing values, and invalid data while preserving the original dataset.

The main function, `clean_airbnb_data()`, accepts a pandas DataFrame and returns a cleaned copy that can be reused by other team members.

## 2. Data Cleaning Decisions

### Duplicate Listings

- Identify duplicate listings using the `id` column.
- Retain the first occurrence of each listing ID in the original row order.
- Remove subsequent occurrences.
- Preserve the original DataFrame.

### Price Cleaning

- Convert supported price formats such as `$100`, `USD 63`, `$1,000`, and `$ 70 / night` into numeric values.
- Remove supported currency symbols, commas, and nightly-rate formatting.
- Convert zero, invalid, missing, or unsupported price values to missing values (`NA`).
- Do not invent or automatically replace missing prices with averages or zeros.

### Minimum Nights

- Convert supported whole-number values, including formats such as `3 nights`, into integers.
- Treat zero, negative, fractional, missing, or invalid minimum-night values as missing.

### Availability

- Convert valid availability values into integers.
- Accept values from 0 to 365 days.
- Treat values outside this range or invalid formats as missing.

### Borough and Room-Type Standardization

- Remove unnecessary surrounding spaces.
- Standardize capitalization.
- Map recognized borough names and room types to consistent labels.
- Leave unrecognized or missing categories as missing rather than guessing their meaning.

### Review Information

- Convert `reviews_per_month` into numeric values.
- Preserve unknown review activity as missing.
- For listings with zero recorded reviews, convert missing monthly review activity to zero.
- Convert valid `last_review` values into dates and represent invalid dates as missing.

## 3. Validation Results

The Python cleaning tool was executed against the supplied `Airbnb_NYC.csv` dataset using GitHub Actions.

| Metric | Result |
|---|---:|
| Original rows | 42,336 |
| Cleaned rows | 42,000 |
| Duplicate listing IDs removed | 336 |
| Missing cleaned prices | 10 |
| Missing cleaned availability values | 82 |
| Unknown borough labels | 0 |
| Unknown room-type labels | 0 |

The remaining missing prices and availability values are intentionally preserved because replacing them with unsupported estimates could produce misleading analytical results.

## 4. Automated Testing

We ran seven automated unit tests using Python's `unittest` framework.

The tests covered:

1. Original DataFrame preservation.
2. Duplicate listing removal.
3. Valid and invalid price conversion.
4. Borough and room-type standardization.
5. Minimum-night and availability validation.
6. Missing review-value handling.
7. Required-column validation and cleaning-report generation.

**Test result:** 7 tests executed, 7 passed.

GitHub Actions also successfully executed the cleaning script against the full Airbnb dataset.

Commands:

```bash
python -m unittest discover -s tests -v
python cleaning.py --input Airbnb_NYC.csv
```

## 5. Limitations and Considerations

- Deduplication retains the first record for each listing ID. This approach assumes the first occurrence should be preserved.
- Unsupported price formats are not automatically interpreted.
- Some values remain missing after cleaning because reliable replacements are unavailable.
- Data consumers must handle missing prices and availability values appropriately.
- Additional validation may be needed for future datasets containing new formats or categories.

## 6. Agile Development and Collaboration

This functionality was developed on the feature branch `feature/8-clean-airbnb-data`.

Work was organized into three implementation tasks:

- **#9:** Clean Airbnb prices and numeric fields.
- **#10:** Remove duplicate listings and standardize categories.
- **#11:** Test and document cleaning functions.

Development was tracked using GitHub Issues and GitHub Projects. The implementation and tests were committed separately, and GitHub Actions provided automated validation.

Peer review and merging into the main branch remain required before the User Story can be considered complete.

## 7. Conclusion

The cleaning module successfully prepares the supplied NYC Airbnb dataset for further analysis while documenting its validation rules and preserving the original data.

The resulting functions can support the group's future pricing, neighbourhood, availability, and review summaries.
