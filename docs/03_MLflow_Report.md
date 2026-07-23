# MLflow Report — Experiment Tracking

## Experiment: AQI_Forecasting
**Status:** 6 models trained, best model: LinearRegression

## Model Performance Comparison
| Model | MAE | RMSE | R² |
|-------|-----|------|-----|
| **LinearRegression** | **14.680** | **22.978** | **0.9196** |
| Ridge | 14.681 | 22.979 | 0.9196 |
| GradientBoosting | 14.718 | 23.070 | 0.9190 |
| LightGBM | 14.965 | 23.581 | 0.9154 |
| RandomForest | 15.147 | 23.591 | 0.9153 |
| DecisionTree | 16.186 | 27.504 | 0.8849 |

## Best Model: LinearRegression
| Metric | Value |
|--------|-------|
| R² Score | 0.9196 |
| MAE | 14.68 |
| RMSE | 22.98 |

## Hyperparameters (Best Model)
- Default sklearn LinearRegression parameters
- Feature scaling: StandardScaler
- Training split: 80/20
- Features: 10 lag + calendar + 5 one-hot city encodings

## MLflow Commands
```bash
mlflow ui                    # Launch tracking UI (port 5000)
mlflow experiments list      # List all experiments
mlflow runs list --experiment-id 1  # List runs
```
