# Monitoring Report — Drift Detection & Dashboard

## Drift Detection Method
**Population Stability Index (PSI)** compares feature distributions between training baseline and recent data window.

| PSI Range | Status | Action |
|-----------|--------|--------|
| < 0.1 | OK | No action needed |
| 0.1 – 0.2 | WARNING | Investigate feature drift |
| > 0.2 | ALERT | Trigger retraining |

## Current Drift Status
| Feature | PSI | Status |
|---------|-----|--------|
| AQI_lag1 | 0.1129 | ⚠️ WARNING |
| AQI_lag3_avg | 0.2058 | 🚨 ALERT |
| PM2.5_lag1 | 0.1129 | ⚠️ WARNING |
| PM10_lag1 | 0.1129 | ⚠️ WARNING |

**Retraining needed:** Yes (AQI_lag3_avg exceeds ALERT threshold)

## Dashboard Pages
| Page | Features |
|------|----------|
| 📊 Dashboard | Key metrics, historical trends, AQI distribution |
| 🔮 Predict AQI | Form-based prediction via API |
| 📈 Model Performance | Model comparison charts, ranking table |
| ⚠️ Drift Monitor | PSI per feature with thresholds, retraining decision |
| ⚙️ Settings | Pipeline info, commands reference |

## Dashboard Commands
```bash
streamlit run dashboard/dashboard.py --server.port 8501
```
