# Monitoring Documentation — Drift Detection, Performance, Retraining

## 1. What We Monitor

| Concern | Metric / Method | Source |
|---------|-----------------|--------|
| Data drift | PSI (Population Stability Index) on 4 lag features | `src/monitor.py` |
| Model quality | R², MAE, RMSE on time-ordered test split | `src/train.py` → MLflow |
| Service health | `/health` liveness probe (Docker HEALTHCHECK + CI smoke test) | FastAPI |
| Pipeline health | DVC stage status (`dvc status` / `dvc repro`) | DVC |

## 2. Drift Detection with PSI

**Population Stability Index** measures how much the distribution of an input
feature has shifted from the training baseline:

```
PSI = Σ (actual% − expected%) × ln(actual% / expected%)
```

Interpretation thresholds (industry standard):
| PSI | Status | Action |
|-----|--------|--------|
| < 0.10 | OK | None |
| 0.10 – 0.20 | WARNING | Investigate |
| ≥ 0.20 | ALERT | Retrain |

`src/monitor.py`:
- Baseline = first 80% of historical data (matches training split).
- Recent window = last 30 days (proxy for live traffic).
- Monitored features: `AQI_lag1`, `AQI_lag3_avg`, `PM2.5_lag1`, `PM10_lag1`.
- Writes `data/drift_report.json`:
```json
{
  "recent_window_days": 30,
  "n_recent_records": 1400,
  "feature_drift": {
    "AQI_lag1":     {"PSI": 0.0512, "status": "OK"},
    "AQI_lag3_avg": {"PSI": 0.2058, "status": "ALERT"},
    "PM2.5_lag1":   {"PSI": 0.0420, "status": "OK"},
    "PM10_lag1":    {"PSI": 0.0788, "status": "OK"}
  },
  "retraining_needed": true,
  "alert_features": ["AQI_lag3_avg"]
}
```

### Sample run
```
AQI_lag1              PSI=0.0512  [OK]
AQI_lag3_avg          PSI=0.2058  [ALERT]
PM2.5_lag1            PSI=0.0420  [OK]
PM10_lag1             PSI=0.0788  [OK]

Retraining needed: True
Drift report saved to data\drift_report.json
```
The `AQI_lag3_avg` ALERT demonstrates the detection path triggering
`retraining_needed = True`.

## 3. Retraining Workflow

1. **Weekly schedule** — GitHub Actions cron (Mon 02:00 UTC) runs `drift-check`.
2. **Drift check** — `src/monitor.py` computes PSI and writes the report.
3. **Decision** — if any feature PSI ≥ 0.20, `retraining_needed=true` →
   retraining job runs `src/train.py` (all 6 models, logged to MLflow).
4. **Gate** — `validate-model` enforces R² ≥ 0.85 / MAE ≤ 20 before the new
   model artifact replaces the deployed one.
5. **Deploy** — rebuilt Docker image with the fresh model is deployed.

Manual retraining is the same path:
```bash
dvc repro            # preprocess → train → monitor
python src/monitor.py   # or dvc stage run monitor
```

## 4. Dashboard (Streamlit, port 8501)

Five tabs:
1. **Dashboard** — city AQI trends, distribution by category.
2. **Predict AQI** — interactive forecast form calling the API.
3. **Model Performance** — leaderboard from `data/model_results.csv`.
4. **Drift Monitor** — PSI per feature with OK/WARNING/ALERT badges and
   `retraining_needed` banner.
5. **Settings** — API URL, model info.

## 5. MLflow Experiment Tracking (port 5000/5001)

Every training run logs:
- Parameters: model type, train/test size, feature count.
- Metrics: MAE, RMSE, R².
- Artifact: serialised model per run (6 runs per training cycle).

The experiment `AQI_Forecasting` shows all historical training cycles side by
side — enabling regression detection across retrains.