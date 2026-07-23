"""
train.py — train 6 regression models with MLflow experiment tracking.
Run: python src/train.py
"""
import os, json, pickle
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb

DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURE_COLS = [
    "Month", "DayOfWeek", "DayOfYear", "IsWeekend",
    "AQI_lag1", "AQI_lag3_avg",
    "PM2.5_lag1", "PM2.5_lag3_avg",
    "PM10_lag1",  "PM10_lag3_avg",
    "City_Bangalore", "City_Chennai",
    "City_Delhi", "City_Hyderabad", "City_Mumbai",
]
TARGET = "AQI"

MODELS = {
    "LinearRegression":   (LinearRegression(), True),
    "Ridge":              (Ridge(alpha=1.0), True),
    "DecisionTree":       (DecisionTreeRegressor(max_depth=8, random_state=42), False),
    "RandomForest":       (RandomForestRegressor(n_estimators=200, max_depth=12,
                                                  random_state=42, n_jobs=-1), False),
    "GradientBoosting":   (GradientBoostingRegressor(n_estimators=200, max_depth=4,
                                                      random_state=42), False),
    "LightGBM":           (lgb.LGBMRegressor(n_estimators=300, max_depth=6,
                                              learning_rate=0.05, random_state=42,
                                              verbose=-1), False),
}


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_features.csv"), parse_dates=["Date"])
    df = pd.get_dummies(df, columns=["City"], prefix="City")
    df = df.sort_values("Date")
    split = int(len(df) * 0.8)
    train, test = df.iloc[:split], df.iloc[split:]
    X_train = train[FEATURE_COLS].fillna(0)
    y_train = train[TARGET]
    X_test  = test[FEATURE_COLS].fillna(0)
    y_test  = test[TARGET]
    return X_train, X_test, y_train, y_test


def train_all():
    X_train, X_test, y_train, y_test = load_data()
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)

    mlflow.set_experiment("AQI_Forecasting")
    results = []

    for name, (model, needs_scale) in MODELS.items():
        with mlflow.start_run(run_name=name):
            Xtr = X_tr_sc if needs_scale else X_train
            Xte = X_te_sc if needs_scale else X_test
            model.fit(Xtr, y_train)
            preds = model.predict(Xte)

            mae  = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            r2   = r2_score(y_test, preds)

            # Log params
            mlflow.log_param("model_type", name)
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size",  len(X_test))
            mlflow.log_param("n_features",  len(FEATURE_COLS))

            # Log metrics
            mlflow.log_metric("MAE",  mae)
            mlflow.log_metric("RMSE", rmse)
            mlflow.log_metric("R2",   r2)

            # Log model artifact
            trusted = ["collections.OrderedDict","lightgbm.basic.Booster","lightgbm.sklearn.LGBMRegressor"]
            mlflow.sklearn.log_model(model, artifact_path="model", skops_trusted_types=trusted)

            results.append({"model": name, "MAE": round(mae,3),
                             "RMSE": round(rmse,3), "R2": round(r2,4)})
            print(f"{name:22s}  MAE={mae:7.3f}  RMSE={rmse:7.3f}  R2={r2:.4f}")

    results_df = pd.DataFrame(results).sort_values("R2", ascending=False)
    results_df.to_csv(os.path.join(DATA_DIR, "model_results.csv"), index=False)

    # Save best model + scaler
    best = results_df.iloc[0]["model"]
    best_model, needs_scale = MODELS[best]
    with open(os.path.join(MODEL_DIR, "best_model.pkl"), "wb") as f:
        pickle.dump(best_model, f)
    with open(os.path.join(MODEL_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler if needs_scale else None, f)
    with open(os.path.join(MODEL_DIR, "model_meta.json"), "w") as f:
        json.dump({"best_model": best, "needs_scale": needs_scale,
                   "features": FEATURE_COLS,
                   "metrics": results_df.iloc[0].to_dict()}, f, indent=2)

    print(f"\nBest model: {best}  |  R2={results_df.iloc[0]['R2']}")
    print("All models trained and logged to MLflow.")
    return results_df


if __name__ == "__main__":
    train_all()
