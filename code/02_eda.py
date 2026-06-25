import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("figures", exist_ok=True)
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120

raw = pd.read_csv("data/merged_raw.csv", parse_dates=["Date"])
clean = pd.read_csv("data/clean_features.csv", parse_dates=["Date"])
pollutant_cols = ["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

# 1. Missing values heatmap (on raw, before cleaning)
plt.figure(figsize=(8, 5))
sns.heatmap(raw[pollutant_cols].isna(), cbar=False, yticklabels=False, cmap="Reds")
plt.title("Missing Value Pattern Across Pollutant Columns (Raw Data)")
plt.tight_layout()
plt.savefig("figures/01_missing_values_heatmap.png")
plt.close()

# 2. AQI distribution per city (boxplot)
plt.figure(figsize=(9, 5))
sns.boxplot(data=clean, x="City", y="AQI", hue="City", palette="Set2", legend=False)
plt.title("AQI Distribution by City")
plt.tight_layout()
plt.savefig("figures/02_aqi_boxplot_by_city.png")
plt.close()

# 3. Time series of AQI per city (monthly average)
ts = clean.copy()
ts["YearMonth"] = ts["Date"].dt.to_period("M").dt.to_timestamp()
monthly = ts.groupby(["YearMonth", "City"])["AQI"].mean().reset_index()
plt.figure(figsize=(12, 5))
sns.lineplot(data=monthly, x="YearMonth", y="AQI", hue="City")
plt.title("Monthly Average AQI Trend by City (2018-2024)")
plt.ylabel("Average AQI")
plt.tight_layout()
plt.savefig("figures/03_aqi_monthly_trend.png")
plt.close()

# 4. Correlation heatmap among pollutants and AQI
plt.figure(figsize=(7, 6))
corr = clean[pollutant_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Matrix: AQI vs Pollutants")
plt.tight_layout()
plt.savefig("figures/04_correlation_heatmap.png")
plt.close()

# 5. Outlier check - AQI distribution histogram
plt.figure(figsize=(8, 5))
sns.histplot(clean["AQI"], bins=50, kde=True, color="indianred")
plt.title("AQI Distribution (All Cities Combined)")
plt.tight_layout()
plt.savefig("figures/05_aqi_histogram.png")
plt.close()

# 6. Seasonal pattern - average AQI by month
plt.figure(figsize=(8, 5))
sns.barplot(data=clean, x="Month", y="AQI", hue="City", errorbar=None)
plt.title("Average AQI by Month (Seasonality)")
plt.tight_layout()
plt.savefig("figures/06_seasonality_by_month.png")
plt.close()

# 7. Weekday vs Weekend AQI
plt.figure(figsize=(7, 5))
sns.boxplot(data=clean, x="IsWeekend", y="AQI", hue="IsWeekend", palette="pastel", legend=False)
plt.xticks([0, 1], ["Weekday", "Weekend"])
plt.title("AQI: Weekday vs Weekend")
plt.tight_layout()
plt.savefig("figures/07_weekday_weekend.png")
plt.close()

print("EDA figures generated:", os.listdir("figures"))

# ponytail: outlier_summary JSON was written but never consumed — removed.
