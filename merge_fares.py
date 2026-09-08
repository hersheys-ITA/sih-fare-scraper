#!/usr/bin/env python3
"""
Merge fare_data.csv and fare_data_duffel.csv into one clean, unified,
all-INR dataset.

Cleaning decisions (see accompanying summary for the reasoning):
  - fare_data.csv: DEDUPLICATED. Every repeated row appears an even
    number of times (2, 4, 6, ... up to 30) with zero odd counts --
    the signature of a collection bug (each real observation written
    twice or more), not genuinely tied flights.
  - fare_data_duffel.csv: NOT deduplicated. Repeat counts are a
    natural mix of odd and even (1, 3, 5, 7... alongside 2, 4, 6...),
    consistent with real flight-search results where several distinct
    flights legitimately share a fare-class price.
  - Duffel's USD prices are converted to INR at a flat rate of 94.50
    (current mid-market USD/INR as of early Sept 2026, per Xe/Yahoo
    Finance/Wise) applied uniformly across all rows. This is a
    simplification -- the true rate moved about 1% over the data's
    collection window (2026-09-03 to 09-08) -- documented here rather
    than silently assumed.
"""

import pandas as pd

USD_TO_INR = 94.50  # flat rate, see module docstring

SRC_A_PATH = "/Users/VyomeshJoshi/Downloads/fare_data.csv"
SRC_B_PATH = "/Users/VyomeshJoshi/Downloads/fare_data_duffel.csv"
OUT_PATH = "/Users/VyomeshJoshi/Downloads/fare_data_merged_clean.csv"


def clean_source_a(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    before = len(df)
    df = df.drop_duplicates().copy()
    after = len(df)
    print(f"fare_data.csv: {before} rows -> {after} after dropping exact duplicates "
          f"({before - after} removed)")

    df["original_price"] = df["price_raw"]
    df["fare_inr"] = (
        df["price_raw"].str.replace("\u20b9", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
        .round(0)
    )
    df["original_currency"] = "INR"
    df["source"] = "fare_data"
    df["base_fare_inr"] = pd.NA
    df["taxes_inr"] = pd.NA
    return df


def clean_source_b(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"fare_data_duffel.csv: {len(df)} rows, kept as-is (no deduplication -- "
          f"see module docstring)")

    df["original_price"] = df["price_raw"]
    df["original_currency"] = df["currency"]
    df["fare_inr"] = (df["price_raw"] * USD_TO_INR).round(0)
    df["base_fare_inr"] = (df["base_fare"] * USD_TO_INR).round(0)
    df["taxes_inr"] = (df["taxes"] * USD_TO_INR).round(0)
    df["source"] = "duffel"
    return df


def main():
    a = clean_source_a(SRC_A_PATH)
    b = clean_source_b(SRC_B_PATH)

    cols = ["collected_on", "origin", "destination", "travel_date", "days_ahead",
            "fare_inr", "base_fare_inr", "taxes_inr", "source",
            "original_price", "original_currency"]

    merged = pd.concat([a[cols], b[cols]], ignore_index=True)
    merged = merged.sort_values(
        ["origin", "destination", "collected_on", "days_ahead"]
    ).reset_index(drop=True)

    merged.to_csv(OUT_PATH, index=False)

    print(f"\nMerged: {len(merged)} rows -> {OUT_PATH}")
    print("\nRows by source:")
    print(merged["source"].value_counts())
    print("\nFare (INR) summary by source:")
    print(merged.groupby("source")["fare_inr"].describe()[["min", "50%", "mean", "max"]])
    print("\nDate range covered (collected_on):", merged["collected_on"].min(), "to", merged["collected_on"].max())
    print("Routes:", sorted(merged[["origin", "destination"]].drop_duplicates().apply(tuple, axis=1).tolist()))


if __name__ == "__main__":
    main()
