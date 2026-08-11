# User Manual — AQI Forecast MLOps Pipeline

## 1. Introduction

This manual covers installation, usage, and troubleshooting for the AQI
next-day forecasting system (API + dashboard + MLflow).

## 2. Installation

### Prerequisites
- Python 3.11+ (developed on 3.13)
- Git, Docker Desktop (optional, for containerised run)
- Windows / macOS / Linux

### 2.1 Clone & Install
```bash
git clone https://github.com/rushdarshan/aqi-forecast-mlop.git
cd aqi-forecast-mlop
pip install -r config/requirements.txt
```

### 2.2 (Optional) Make shortcuts
```bash
make install      # pip install -r config/requirements.txt
```

## 3. Running the Pipeline

### 3.1 Reproduce the ML pipeline (DVC)
```bash
dvc repro
```
Runs: preprocess (merge + feature engineering) → train (6 models + MLflow) →
monitor (PSI drift). Outputs:
- `data/clean_features.csv`
- `data/model_results.csv`
- `models/best_model.pkl`, `models/scaler.pkl`, `models/model_meta.json`
- `data/drift_report.json`

Status check: `dvc status` (must show "Data and pipelines are up to date").

### 3.2 Start services

**Option A — Docker (recommended):**
```bash
docker-compose up --build -d
```
| Service | URL |
|---------|-----|
| API | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |
| MLflow | http://localhost:5000 |

**Option B — Manual (3 terminals):**
```bash
uvicorn src.app:app --port 8000
streamlit run dashboard/dashboard.py
mlflow server --host 127.0.0.1 --port 5001 --workers 1   # --workers 1 required on Windows
```

## 4. Usage

### 4.1 API — single prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"city":"Mumbai","forecast_date":"2025-01-15","aqi_yesterday":120,
       "aqi_3day_avg":118,"pm25_yesterday":54.2,"pm25_3day_avg":52.8,
       "pm10_yesterday":98.6,"pm10_3day_avg":95.1}'
```
Response: `{"city":"Mumbai","forecast_date":"2025-01-15","predicted_aqi":...,
"aqi_category":"...","model_used":"LinearRegression","r2_score":0.9196}`

### 4.2 API — batch prediction
`POST /predict/batch` with `{"requests": [ {…}, {…} ]}` — same fields per item.

### 4.3 API — health & info
```bash
curl http://localhost:8000/health
curl http://localhost:8000/model-info
curl http://localhost:8000/cities
```

### 4.4 Dashboard
1. Open http://localhost:8501.
2. **Predict AQI** tab: pick city/date, enter yesterday's AQI & PM values, hit
   Predict.
3. **Drift Monitor** tab: see PSI per feature and the retraining banner.
4. **Model Performance** tab: leaderboard of all 6 models.

### 4.5 MLflow UI
Open http://localhost:5000 (or :5001), experiment `AQI_Forecasting` → runs with
metrics/params/artifacts.

## 5. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `dvc push` fails: "no remote specified" | No DVC remote configured | `dvc remote add -d myremote <path>` |
| `dvc commit` fails: "output already tracked by SCM" | Output file tracked by Git | `git rm -r --cached <file>` then `dvc commit -f` |
| MLflow UI crashes on Windows | Port/worker binding issue | `mlflow server --workers 1` |
| API returns 500 on /predict | Feature column order mismatch | Check `FEATURE_COLS` in `app.py` matches `train.py` |
| Docker healthcheck failing | Model files missing in image | Ensure `models/` exists before `docker-compose up --build` |
| Streamlit can't reach API | API not running / wrong port | Check Settings tab API URL; start API first |
| DVC "dependency does not exist" (config\src\...) | Stale dvc.yaml path history | Delete `config/dvc.yaml`, re-run `dvc repro` from repo root |
| Tests fail on fresh clone | `data/` CSVs missing | `dvc pull` (or keep city CSVs in repo) + `python src/preprocess.py` |

## 6. Common Workflows

```bash
# Full retrain + redeploy
dvc repro
docker-compose up --build -d

# Run tests only
pytest src/test_pipeline.py -v

# Check drift manually
python src/monitor.py
```