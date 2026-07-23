"""
test_pipeline.py — unit and integration tests for the AQI pipeline.
Run: pytest src/test_pipeline.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np
from datetime import date
from src.preprocess import clean_and_engineer, load_and_merge
from src.monitor import compute_psi


# ============================================================
# 1. PREPROCESSING TESTS
# ============================================================
class TestPreprocessing:

    def test_merge_returns_dataframe(self):
        df = load_and_merge()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 10000

    def test_all_cities_present(self):
        df = load_and_merge()
        cities = df["City"].unique()
        for c in ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Bangalore"]:
            assert c in cities

    def test_date_parsed(self):
        df = load_and_merge()
        assert pd.api.types.is_datetime64_any_dtype(df["Date"])

    def test_no_missing_aqi_after_clean(self):
        raw = load_and_merge()
        clean = clean_and_engineer(raw)
        assert clean["AQI"].isna().sum() == 0

    def test_lag_features_exist(self):
        raw = load_and_merge()
        clean = clean_and_engineer(raw)
        for col in ["AQI_lag1", "AQI_lag3_avg", "PM2.5_lag1", "PM10_lag1"]:
            assert col in clean.columns

    def test_no_same_day_leakage(self):
        """Verify same-day pollutant columns are NOT used as features."""
        raw = load_and_merge()
        clean = clean_and_engineer(raw)
        leaky_cols = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
        feature_cols = [
            "Month", "DayOfWeek", "DayOfYear", "IsWeekend",
            "AQI_lag1", "AQI_lag3_avg", "PM2.5_lag1",
            "PM2.5_lag3_avg", "PM10_lag1", "PM10_lag3_avg"
        ]
        for col in leaky_cols:
            assert col not in feature_cols, f"{col} is a leaky feature!"

    def test_lag_values_are_previous_day(self):
        raw = load_and_merge()
        clean = clean_and_engineer(raw)
        delhi = clean[clean["City"] == "Delhi"].reset_index(drop=True)
        # AQI_lag1 on row i should equal AQI on row i-1
        for i in range(1, min(10, len(delhi))):
            assert abs(delhi.loc[i, "AQI_lag1"] - delhi.loc[i-1, "AQI"]) < 0.01

    def test_calendar_features_range(self):
        raw = load_and_merge()
        clean = clean_and_engineer(raw)
        assert clean["Month"].between(1, 12).all()
        assert clean["DayOfWeek"].between(0, 6).all()
        assert clean["IsWeekend"].isin([0, 1]).all()


# ============================================================
# 2. DRIFT MONITORING TESTS
# ============================================================
class TestMonitoring:

    def test_psi_identical_distributions(self):
        """PSI of a distribution against itself should be ~0."""
        arr = np.random.normal(100, 20, 1000)
        psi = compute_psi(arr, arr)
        assert psi < 0.05

    def test_psi_very_different_distributions(self):
        """PSI of very different distributions should exceed alert threshold."""
        expected = np.random.normal(100, 10, 1000)
        actual   = np.random.normal(300, 10, 1000)
        psi = compute_psi(expected, actual)
        assert psi > 0.2

    def test_psi_non_negative(self):
        arr1 = np.random.normal(80, 20, 800)
        arr2 = np.random.normal(90, 25, 800)
        assert compute_psi(arr1, arr2) >= 0


# ============================================================
# 3. MODEL VALIDATION GATE
# ============================================================
class TestModelGate:

    def test_best_model_meets_r2_threshold(self):
        """Trained best model must achieve R² >= 0.85 on test set."""
        result_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "model_results.csv")
        if not os.path.exists(result_path):
            pytest.skip("model_results.csv not found — run train.py first")
        results = pd.read_csv(result_path)
        best_r2 = results["R2"].max()
        assert best_r2 >= 0.85, (
            f"Best model R²={best_r2:.4f} is below the 0.85 production gate")

    def test_best_model_meets_mae_threshold(self):
        """Trained best model must achieve MAE <= 20."""
        result_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "model_results.csv")
        if not os.path.exists(result_path):
            pytest.skip("model_results.csv not found — run train.py first")
        results = pd.read_csv(result_path)
        best_mae = results["MAE"].min()
        assert best_mae <= 20, (
            f"Best model MAE={best_mae:.3f} exceeds the 20-point threshold")


# ============================================================
# 4. API INPUT VALIDATION TESTS
# ============================================================
class TestAPIValidation:

    def test_aqi_category_good(self):
        from src.app import aqi_category
        assert aqi_category(30) == "Good"

    def test_aqi_category_moderate(self):
        from src.app import aqi_category
        assert aqi_category(150) == "Moderate"

    def test_aqi_category_severe(self):
        from src.app import aqi_category
        assert aqi_category(450) == "Severe"

    def test_aqi_category_boundary(self):
        from src.app import aqi_category
        assert aqi_category(100) == "Satisfactory"
        assert aqi_category(101) == "Moderate"
