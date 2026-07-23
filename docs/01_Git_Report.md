# Technical Implementation Report — Git & Version Control

## Repository Structure
```
AQI_Forecast/
├── src/              # Core pipeline modules
│   ├── preprocess.py # Data merging, cleaning, feature engineering
│   ├── train.py      # Model training with MLflow tracking
│   ├── monitor.py    # PSI-based drift detection
│   ├── app.py        # FastAPI REST API
│   └── test_pipeline.py  # Unit & integration tests
├── dashboard/        # Streamlit monitoring dashboard
├── config/           # Docker, DVC, CI/CD configuration
├── models/           # Trained model artifacts
├── data/             # Raw and processed datasets
└── docs/             # Documentation reports
```

## Branch Strategy
| Branch | Purpose |
|--------|---------|
| `master` | Production-ready code, reviewed and tested |
| `develop` | Active development branch, feature integration |

Workflow: Feature branches → `develop` → `master` (via PR with CI gate).

## Commit History
```
8be74fe feat: AQI forecasting MLOps pipeline - API, dashboard, drift monitoring, Docker, CI/CD
```

## Key Git Commands
```bash
git init
git add -A
git commit -m "feat: initial pipeline"
git checkout -b develop
git remote add origin <repo-url>
git push -u origin master
```
