import pandas as pd
import numpy as np
import glob, os

DATA_DIR = "data"
cities = ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Bangalore"]

frames = []
for c in cities:
    df = pd.read_csv(os.path.join(DATA_DIR, f"{c}.csv"))
    # drop fully-empty trailing unnamed columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = [col.strip() for col in df.columns]
    df["City"] = c  # normalize city label (source file used Bangalore/Hyderabad spellings already)
    frames.append(df)

raw = pd.concat(frames, ignore_index=True)
print("Raw shape:", raw.shape)
print(raw.dtypes)

# Parse date (format dd/mm/yy)
raw["Date"] = pd.to_datetime(raw["Date"], format="%d/%m/%y", errors="coerce")
print("Unparsed dates:", raw["Date"].isna().sum())

# Sort
raw = raw.sort_values(["City", "Date"]).reset_index(drop=True)

# Save raw merged (pre-cleaning) for the Dataset Report
raw.to_csv("data/merged_raw.csv", index=False)

# ---- Data quality summary (for Dataset Report) ----
pollutant_cols = ["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
quality = pd.DataFrame({
    "missing_count": raw[pollutant_cols].isna().sum(),
    "missing_pct": (raw[pollutant_cols].isna().sum() / len(raw) * 100).round(2),
    "min": raw[pollutant_cols].min(),
    "max": raw[pollutant_cols].max(),
    "mean": raw[pollutant_cols].mean().round(2),
    "std": raw[pollutant_cols].std().round(2),
})
quality.to_csv("data/quality_report.csv")
print(quality)

# date range per city
ranges = raw.groupby("City")["Date"].agg(["min", "max", "count"])
ranges.to_csv("data/city_date_ranges.csv")
print(ranges)

# ---- Cleaning ----
clean = raw.dropna(subset=["Date"]).copy()
clean = clean.drop_duplicates(subset=["City", "Date"])

# Impute missing pollutant values: city-wise forward fill then median fallback
for col in pollutant_cols:
    clean[col] = clean.groupby("City")[col].transform(lambda s: s.ffill().bfill())
    clean[col] = clean[col].fillna(clean[col].median())

# Feature engineering: calendar features
clean["Year"] = clean["Date"].dt.year
clean["Month"] = clean["Date"].dt.month
clean["Day"] = clean["Date"].dt.day
clean["DayOfWeek"] = clean["Date"].dt.dayofweek
clean["DayOfYear"] = clean["Date"].dt.dayofyear
clean["IsWeekend"] = (clean["DayOfWeek"] >= 5).astype(int)

# Lag features per city (previous day pollutant values -> used for next-day AQI forecasting)
clean = clean.sort_values(["City", "Date"])
for col in ["AQI", "PM2.5", "PM10"]:
    clean[f"{col}_lag1"] = clean.groupby("City")[col].shift(1)
    clean[f"{col}_lag3_avg"] = clean.groupby("City")[col].transform(lambda s: s.shift(1).rolling(3).mean())

clean = clean.dropna(subset=["AQI_lag1", "PM2.5_lag1", "PM10_lag1", "AQI_lag3_avg"])

clean.to_csv("data/clean_features.csv", index=False)
print("Clean shape:", clean.shape)
print(clean.head())
