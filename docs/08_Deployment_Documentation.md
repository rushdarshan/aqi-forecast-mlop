# Deployment Documentation

## 1. Deployment Architecture

```
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│  Streamlit  │──▶│   FastAPI    │──▶│  MLflow      │
│  Dashboard  │   │   (port 8000)│   │  (port 5000) │
│  (port 8501)│   │              │   │  (sqlite db) │
└─────────────┘   └──────┬───────┘   └──────────────┘
                         │
                    models/best_model.pkl
                    models/scaler.pkl
                    models/model_meta.json
```

Three services run under Docker Compose:
- **api** — FastAPI prediction server (port 8000)
- **dashboard** — Streamlit 5-tab monitoring UI (port 8501)
- **mlflow** — experiment tracking server (port 5000)

## 2. Docker Configuration

### 2.1 Dockerfile (`config/Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip
COPY src/ ./src/
COPY dashboard/ ./dashboard/
COPY models/ ./models/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```
Notes:
- `curl` is installed for the health check.
- Computed directly inside the container and passes a `curl /health` smoke test
  during CI (docker-build job).

### 2.2 docker-compose.yml
| Service | Image/Build | Port | Volumes |
|---------|-------------|------|---------|
| api | build: config/Dockerfile | 8000 | ./models, ./data (read-only) |
| dashboard | build: config/Dockerfile, `streamlit run` override | 8501 | ./models, ./data (read-only) |
| mlflow | ghcr.io/mlflow/mlflow:v2.13.0 | 5000 | mlflow_data volume (sqlite + artifacts) |

The dashboard waits for the API healthcheck (`depends_on: condition:
service_healthy`) before starting.

## 3. Deployment Steps

### 3.1 Local Deployment (Docker)
```bash
docker-compose up --build -d          # start all three services
curl http://localhost:8000/health     # {"status":"ok", ...}
docker-compose logs -f api            # follow API logs
docker-compose down                   # stop
```

### 3.2 Manual Deployment (without Docker)
```bash
# Terminal 1 — API
uvicorn src.app:app --host 0.0.0.0 --port 8000
# Terminal 2 — Dashboard
streamlit run dashboard/dashboard.py
# Terminal 3 — MLflow (Windows: --workers 1 required)
mlflow server --host 127.0.0.1 --port 5001 --workers 1
```

## 4. API Documentation

Interactive Swagger docs: `http://localhost:8000/docs`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness + model-loaded status |
| `/model-info` | GET | Best model name, features, metrics |
| `/cities` | GET | Supported city list |
| `/predict` | POST | Single next-day AQI forecast |
| `/predict/batch` | POST | Batch forecasts |

### Example: /predict
```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{
    "city": "Delhi",
    "forecast_date": "2025-01-15",
    "aqi_yesterday": 210,
    "aqi_3day_avg": 205,
    "pm25_yesterday": 92.5,
    "pm25_3day_avg": 88.2,
    "pm10_yesterday": 165.4,
    "pm10_3day_avg": 159.8
  }'
```
Response:
```json
{
  "city": "Delhi",
  "forecast_date": "2025-01-15",
  "predicted_aqi": 197.4,
  "aqi_category": "Moderate",
  "model_used": "LinearRegression",
  "r2_score": 0.9196
}
```

## 5. Deployment Screenshots

Screenshots of the live services are captured at review time:
1. `docker-compose ps` — all services healthy.
2. `curl http://localhost:8000/health` — API responding.
3. Dashboard Overview tab — city trend charts.
4. MLflow UI — experiment runs with metrics.
5. GitHub Actions — docker-build job passing.

## 6. Cloud Deployment (Roadmap)

The Dockerised services can be lifted to any cloud with minimal change:
- **AWS ECS/Fargate** or **GCP Cloud Run**: push `aqi-forecast-api` image to ECR /
  Artifact Registry, run service with healthcheck enabled.
- **Azure App Service**: deploy the container with port 8000 configured.
Production considerations: managed MLflow (or S3/GCS artifact store), secrets for
tracking URI, and a load balancer in front of the API for scale-out.