"""
preprocess.py — merge, clean, and feature-engineer AQI data for all 5 cities.
Run directly: python src/preprocess.py
"""
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CITIES = ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Bangalore"]
POLLUTANT_COLS = ["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]


def load_and_merge() -> pd.DataFrame:
    frames = []
    for city in CITIES:
        df = pd.read_csv(os.path.join(DATA_DIR, f"{city}.csv"))
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.columns = [c.strip() for c in df.columns]
        df["City"] = city
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)
    raw["Date"] = pd.to_datetime(raw["Date"], format="%d/%m/%y", errors="coerce")
    raw = raw.sort_values(["City", "Date"]).reset_index(drop=True)
    return raw


def clean_and_engineer(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.dropna(subset=["Date"]).drop_duplicates(subset=["City", "Date"]).copy()
    # Impute pollutants city-wise
    for col in POLLUTANT_COLS:
        df[col] = df.groupby("City")[col].transform(lambda s: s.ffill().bfill())
        df[col] = df[col].fillna(df[col].median())
    # Calendar features
    df["Month"]     = df["Date"].dt.month
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["DayOfYear"] = df["Date"].dt.dayofyear
    df["IsWeekend"] = (df["DayOfWeek"] >= 5).astype(int)
    # Lag features (no same-day leakage)
    df = df.sort_values(["City", "Date"])
    for col in ["AQI", "PM2.5", "PM10"]:
        df[f"{col}_lag1"]    = df.groupby("City")[col].shift(1)
        df[f"{col}_lag3_avg"]= df.groupby("City")[col].transform(
            lambda s: s.shift(1).rolling(3).mean())
    df = df.dropna(subset=["AQI_lag1", "PM2.5_lag1", "AQI_lag3_avg"])
    df.to_csv(os.path.join(DATA_DIR, "clean_features.csv"), index=False)
    print(f"Clean dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


if __name__ == "__main__":
    raw = load_and_merge()
    clean_and_engineer(raw)
    print("Preprocessing complete.")
