import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import json

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb

clean = pd.read_csv("data/clean_features.csv", parse_dates=["Date"])

# NOTE: same-day pollutant columns (PM2.5, PM10, NO2, SO2, CO, O3) are excluded
# from the feature set. In this dataset they are mathematically back-calculated
# FROM the AQI value itself (reverse-engineered AQI-to-pollutant formulas per the
# source documentation), so including them causes target leakage (same-day pollutants
# are a deterministic function of same-day AQI). For a genuine *forecasting* task -
# predicting tomorrow's AQI using only information available today - we use lagged
# (previous-day / trailing 3-day average) pollutant and AQI values plus calendar
# features only.
feature_cols = [
    "Month", "DayOfWeek", "DayOfYear", "IsWeekend",
    "AQI_lag1", "AQI_lag3_avg", "PM2.5_lag1", "PM2.5_lag3_avg",
    "PM10_lag1", "PM10_lag3_avg"
]
target_col = "AQI"

# One-hot encode city (since AQI behavior differs structurally by city)
clean_enc = pd.get_dummies(clean, columns=["City"], prefix="City")
city_dummy_cols = [c for c in clean_enc.columns if c.startswith("City_")]
feature_cols_full = feature_cols + city_dummy_cols

X = clean_enc[feature_cols_full]
y = clean_enc[target_col]

# Time-respecting split: train on earlier 80%, test on most recent 20% (per overall timeline)
clean_enc = clean_enc.sort_values("Date")
split_idx = int(len(clean_enc) * 0.8)
X_sorted = clean_enc[feature_cols_full]
y_sorted = clean_enc[target_col]
X_train, X_test = X_sorted.iloc[:split_idx], X_sorted.iloc[split_idx:]
y_train, y_test = y_sorted.iloc[:split_idx], y_sorted.iloc[split_idx:]

print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression": Ridge(alpha=1.0),
    "Decision Tree": DecisionTreeRegressor(max_depth=8, random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42),
    "LightGBM": lgb.LGBMRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42, verbose=-1),
}

results = []
predictions = {}

for name, model in models.items():
    if name in ["Linear Regression", "Ridge Regression"]:
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    results.append({"Model": name, "MAE": round(mae, 3), "RMSE": round(rmse, 3), "R2": round(r2, 4)})
    predictions[name] = preds
    print(f"{name:20s}  MAE={mae:7.3f}  RMSE={rmse:7.3f}  R2={r2:.4f}")

results_df = pd.DataFrame(results).sort_values("R2", ascending=False)
results_df.to_csv("data/model_results.csv", index=False)
print("\n", results_df)

best_model_name = results_df.iloc[0]["Model"]
print(f"\nBest baseline model: {best_model_name}")

# ---- Plots ----
# 1. Model comparison bar chart
plt.figure(figsize=(9, 5))
plot_df = results_df.melt(id_vars="Model", value_vars=["MAE", "RMSE"], var_name="Metric", value_name="Value")
sns.barplot(data=plot_df, x="Model", y="Value", hue="Metric")
plt.xticks(rotation=20)
plt.title("Baseline Model Comparison (Lower is Better)")
plt.tight_layout()
plt.savefig("figures/08_model_comparison.png")
plt.close()

# 2. R2 comparison
plt.figure(figsize=(8, 5))
sns.barplot(data=results_df, x="Model", y="R2", hue="Model", palette="viridis", legend=False)
plt.xticks(rotation=20)
plt.title("Baseline Model R² Comparison")
plt.tight_layout()
plt.savefig("figures/09_r2_comparison.png")
plt.close()

# 3. Actual vs predicted for best model
best_preds = predictions[best_model_name]
plt.figure(figsize=(7, 7))
plt.scatter(y_test, best_preds, alpha=0.3, s=10)
lims = [min(y_test.min(), best_preds.min()), max(y_test.max(), best_preds.max())]
plt.plot(lims, lims, "r--", linewidth=1)
plt.xlabel("Actual AQI")
plt.ylabel("Predicted AQI")
plt.title(f"Actual vs Predicted AQI — {best_model_name}")
plt.tight_layout()
plt.savefig("figures/10_actual_vs_predicted.png")
plt.close()

# 4. Feature importance (for tree-based best model, or fallback to RF)
importance_model = models["Random Forest"]
importances = pd.Series(importance_model.feature_importances_, index=feature_cols_full).sort_values(ascending=False).head(12)
plt.figure(figsize=(8, 6))
sns.barplot(x=importances.values, y=importances.index, hue=importances.index, palette="mako", legend=False)
plt.title("Top Feature Importances (Random Forest)")
plt.tight_layout()
plt.savefig("figures/11_feature_importance.png")
plt.close()

summary = {
    "train_size": len(X_train),
    "test_size": len(X_test),
    "features_used": feature_cols_full,
    "best_model": best_model_name,
    "best_metrics": results_df.iloc[0].to_dict(),
    "all_results": results,
}
with open("data/baseline_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nDone. Figures + results saved.")
