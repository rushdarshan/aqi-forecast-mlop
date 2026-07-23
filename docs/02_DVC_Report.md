# DVC Documentation — Data & Pipeline Versioning

## Pipeline Stages

```
preprocess ──► train ──► monitor
```

### Stage 1: preprocess
- **Command:** `python src/preprocess.py`
- **Dependencies:** `data/Delhi.csv`, `data/Mumbai.csv`, `data/Chennai.csv`, `data/Hyderabad.csv`, `data/Bangalore.csv`
- **Outputs:** `data/merged_raw.csv`, `data/clean_features.csv`

### Stage 2: train
- **Command:** `python src/train.py`
- **Dependencies:** `data/clean_features.csv`
- **Outputs:** `models/best_model.pkl`, `models/scaler.pkl`, `models/model_meta.json`
- **Metrics:** `data/model_results.csv`

### Stage 3: monitor
- **Command:** `python src/monitor.py`
- **Dependencies:** `data/clean_features.csv`
- **Outputs:** `data/drift_report.json`

## DVC Commands
```bash
dvc init                          # Initialize DVC
dvc repro                         # Reproduce full pipeline
dvc pipeline show                 # Visualize pipeline stages
dvc metrics show                  # Show tracked metrics
dvc push                          # Push data to remote storage
```

## Reproduce Output
```bash
$ dvc repro
Running stage 'preprocess': 12027 rows, 19 columns
Running stage 'train':      LinearRegression  R2=0.9196  (best)
Running stage 'monitor':    Drift ALERT on AQI_lag3_avg (PSI=0.2058)
```

## Dataset Versions
| Dataset | Records | Features | Version |
|---------|---------|----------|---------|
| merged_raw.csv | 12,042 | 9 | v1 |
| clean_features.csv | 12,027 | 19 | v1 |
