# AQI Forecast — Indian Cities

Next-day Air Quality Index forecasting using historical pollutant data and baseline ML models.

**Cities:** Bangalore, Chennai, Delhi, Hyderabad, Mumbai  
**Data:** 2018–2024 daily AQI, PM2.5, PM10, NO2, SO2, CO, O3  
**Approach:** Lagged features + calendar features, time-respecting train/test split, no target leakage.

## Pipeline

| Script | Purpose |
|--------|---------|
| `01_merge_clean.py` | Merge per-city CSVs, impute missing values, engineer lag/rolling features |
| `02_eda.py` | Generate EDA figures (trends, correlations, seasonality) |
| `03_baseline_models.py` | Train & evaluate 6 regressors, save comparison plots + results |

## Models

Linear Regression, Ridge, Decision Tree, Random Forest, Gradient Boosting, LightGBM.

## Usage

```bash
pip install pandas numpy matplotlib seaborn scikit-learn lightgbm
cd code
python 01_merge_clean.py
python 02_eda.py
python 03_baseline_models.py
```

## Results

Figures and result summaries are written to `figures/` and `data/`.
