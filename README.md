# AQI Forecast — Indian Cities

Next-day Air Quality Index forecasting for 5 Indian cities with an MLOps pipeline.

**Cities:** Bangalore, Chennai, Delhi, Hyderabad, Mumbai  
**Data:** 2018–2024 daily AQI, PM2.5, PM10  
**Best Model:** Linear Regression (R² 0.9196, MAE 14.68)

## Pipeline

| Stage | Description |
|-------|-------------|
| `preprocess` | Merge CSVs, impute, engineer lag/calendar features |
| `train` | Train 6 models, log to MLflow, persist best model |
| `monitor` | PSI drift detection on latest data |

## Quick Start

```bash
make install     # pip install -r config/requirements.txt
make dvc-repro   # dvc repro (runs full pipeline)
make run-api     # uvicorn src.app:app --port 8000
make run-dash    # streamlit run dashboard/dashboard.py
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| FastAPI | 8000 | `/predict`, `/predict/batch`, `/health`, `/model-info`, `/cities` |
| Streamlit | 8501 | 5-tab dashboard (overview, cities, model, monitor, API test) |
| MLflow | 5001 | Experiment tracking with model comparison |

## Docker

```bash
docker-compose up --build
```

## CI/CD

GitHub Actions on push/PR: lint → test → build.

## Tech Stack

Python, FastAPI, Streamlit, scikit-learn, MLflow, DVC, Docker, GitHub Actions
