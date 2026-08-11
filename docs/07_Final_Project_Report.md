# Final Project Report — AQI Forecasting MLOps Pipeline

## Abstract

Air pollution is a major public-health and economic challenge in Indian cities. This
project builds an end-to-end MLOps pipeline for next-day Air Quality Index (AQI)
forecasting for five Indian cities — Delhi, Mumbai, Chennai, Hyderabad, and Bangalore.
Historical daily pollutant data (2018–2024) is preprocessed with lag and calendar
features, six regression models are benchmarked, and the best model (Linear
Regression, R² = 0.9196, MAE = 14.68) is deployed behind a FastAPI service. The
system is productionised with DVC data versioning, MLflow experiment tracking,
automated CI/CD, Docker containerisation, PSI-based drift monitoring, a Streamlit
monitoring dashboard, and weekly scheduled retraining.

## 1. Introduction

### 1.1 Problem Statement
Air quality in Indian metropolitan areas frequently crosses safe thresholds, causing
respiratory illness, reduced productivity, and premature mortality. A reliable
next-day AQI forecast lets citizens plan outdoor activity and lets administrators
take pre-emptive action (e.g., traffic restrictions, school closures).

### 1.2 Objectives
- Build a reproducible ML pipeline from raw pollutant data to deployable model.
- Forecast next-day AQI per city with lagged + calendar features.
- Compare 6 regression models and select the best by validation metrics.
- Productionise with versioning, experiment tracking, testing, Docker, CI/CD,
  monitoring, and automated retraining.

### 1.3 Scope
- 5 Indian cities, daily AQI/PM2.5/PM10 (plus NO2, SO2, CO, O3 collected but not
  used as model features).
- 2018–2024 daily observations (~24,900 records after cleaning).
- Next-day (t+1) forecast horizon only.

## 2. Methodology

### 2.1 Data Pipeline (DVC)
```
raw CSVs (per city) → merge → impute (ffill/bfill + median) → dedupe
  → calendar features (Month, DayOfWeek, DayOfYear, IsWeekend)
  → lag features (AQI_lag1, AQI_lag3_avg, PM2.5_lag1/3, PM10_lag1/3)
  → clean_features.csv
```
No same-day leakage: all lag features are computed from *previous* days only.

### 2.2 Modelling (MLflow)
6 models trained on an 80/20 time-ordered split, scaled where required:

| Model | R² | MAE | RMSE |
|-------|----|----|----|
| **Linear Regression** | **0.9196** | **14.68** | **22.5** |
| Ridge | 0.9196 | 14.67 | 22.5 |
| Gradient Boosting | 0.9081 | 17.39 | 25.5 |
| Random Forest | 0.9079 | 17.34 | 25.6 |
| LightGBM | 0.9051 | 17.68 | 26.0 |
| Decision Tree | 0.8644 | 20.84 | 31.2 |

Linear Regression wins on R² (0.9196) with a 14.68 MAE — an average error of
~15 AQI points, within one AQI band.

### 2.3 Deployment (FastAPI + Docker)
- `/predict` — single-city next-day forecast
- `/predict/batch` — batch forecasts
- `/health`, `/model-info`, `/cities`
- Dockerised via `config/Dockerfile`, orchestrated with `docker-compose.yml`
  (api + dashboard + mlflow).

### 2.4 Monitoring (PSI)
Population Stability Index compares the last 30 days of features against the
training baseline. PSI < 0.1 OK, 0.1–0.2 WARNING, ≥ 0.2 ALERT → `retraining_needed`.

### 2.5 CI/CD (GitHub Actions)
5 jobs: lint+tests → model validation gate (R² ≥ 0.85, MAE ≤ 20) → docker build
+ smoke test → deploy (master) → weekly drift check + retraining trigger.

## 3. Results

- Best model: Linear Regression — R² 0.9196, MAE 14.68, RMSE 22.5.
- All 6 models logged to MLflow with parameters and metrics (experiment
  `AQI_Forecasting`).
- 17 automated tests pass (preprocessing, training, prediction, API, drift).
- Drift monitor on latest data: `AQI_lag3_avg` PSI 0.2058 → ALERT,
  retraining_needed = True (demonstrates the retraining trigger works).
- Full pipeline reproducible via `dvc repro` (preprocess → train → monitor).
- API health endpoint verified inside Docker container (CI smoke test).

## 4. Conclusion

The project demonstrates a complete end-to-end MLOps lifecycle: reproducible data
pipeline (DVC), experiment tracking (MLflow), quality gates and automated
deployment (GitHub Actions), containerisation (Docker), and continuous monitoring
with automatic retraining (PSI + scheduled CI job). The deployed model predicts
next-day AQI within ~15 points, which is actionable for the public and for city
administration. The architecture is generic and can be extended to more cities,
pollutants, longer horizons, and cloud deployment (AWS/GCP/Azure) without
architectural change.

## 5. Future Work

- Cloud deployment (ECS/GKE) with load balancing for scalability.
- Longer forecast horizons (3/7-day) and deep learning baselines (LSTM).
- Model registry promotion (staging → production) with MLflow.
- Ground-truth feedback loop: score live predictions as ground truth arrives.
