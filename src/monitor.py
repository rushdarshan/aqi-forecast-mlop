"""
monitor.py — data drift detection using Population Stability Index (PSI).
Compares incoming feature distributions against training baseline.
Run: python src/monitor.py
"""
import os, json
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MONITOR_FEATURES = ["AQI_lag1", "AQI_lag3_avg", "PM2.5_lag1", "PM10_lag1"]
PSI_THRESHOLD_WARN   = 0.1   # slight drift
PSI_THRESHOLD_ALERT  = 0.2   # significant drift → trigger retraining


def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Compute Population Stability Index between two distributions."""
    breakpoints = np.quantile(expected, np.linspace(0, 1, bins + 1))
    breakpoints[0], breakpoints[-1] = -np.inf, np.inf

    expected_pct = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_pct   = np.histogram(actual,   bins=breakpoints)[0] / len(actual)

    # Avoid division by zero / log(0)
    expected_pct = np.where(expected_pct == 0, 1e-6, expected_pct)
    actual_pct   = np.where(actual_pct   == 0, 1e-6, actual_pct)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(psi)


def run_drift_check(recent_window_days: int = 30) -> dict:
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_features.csv"),
                     parse_dates=["Date"])
    df = df.sort_values("Date")

    # Training baseline = first 80%
    split = int(len(df) * 0.8)
    train_df = df.iloc[:split]

    # Recent window = last N days of the full dataset (proxy for "live" data)
    cutoff = df["Date"].max() - pd.Timedelta(days=recent_window_days)
    recent_df = df[df["Date"] >= cutoff]

    if len(recent_df) < 20:
        print("Not enough recent data for drift check.")
        return {}

    results = {}
    alerts  = []
    for feat in MONITOR_FEATURES:
        psi = compute_psi(train_df[feat].dropna().values,
                          recent_df[feat].dropna().values)
        status = ("OK" if psi < PSI_THRESHOLD_WARN else
                  "WARNING" if psi < PSI_THRESHOLD_ALERT else "ALERT")
        results[feat] = {"PSI": round(psi, 4), "status": status}
        print(f"{feat:20s}  PSI={psi:.4f}  [{status}]")
        if status == "ALERT":
            alerts.append(feat)

    summary = {
        "recent_window_days": recent_window_days,
        "n_recent_records":   len(recent_df),
        "feature_drift":      results,
        "retraining_needed":  len(alerts) > 0,
        "alert_features":     alerts,
    }
    out_path = os.path.join(DATA_DIR, "drift_report.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nRetraining needed: {summary['retraining_needed']}")
    print(f"Drift report saved to {out_path}")
    return summary


if __name__ == "__main__":
    run_drift_check()
