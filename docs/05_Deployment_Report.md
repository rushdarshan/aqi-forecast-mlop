# Deployment Report — Docker & API

## API Documentation

### FastAPI Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check + model status |
| `/model-info` | GET | Model metadata and metrics |
| `/predict` | POST | Next-day AQI forecast |
| `/cities` | GET | List supported cities |

### Sample Prediction Request
```json
POST /predict
{
  "city": "Delhi",
  "forecast_date": "2026-07-23",
  "aqi_yesterday": 180,
  "aqi_3day_avg": 175,
  "pm25_yesterday": 95,
  "pm25_3day_avg": 90,
  "pm10_yesterday": 200,
  "pm10_3day_avg": 195
}
```

### Sample Response
```json
{
  "city": "Delhi",
  "forecast_date": "2026-07-23",
  "predicted_aqi": 165.3,
  "aqi_category": "Moderate",
  "model_used": "LinearRegression",
  "r2_score": 0.9196
}
```

## Docker Configuration

### Services (docker-compose.yml)
| Service | Port | Description |
|---------|------|-------------|
| api | 8000 | FastAPI prediction API |
| dashboard | 8501 | Streamlit monitoring dashboard |
| mlflow | 5000 | MLflow experiment tracking |

### Docker Commands
```bash
# Build and start all services
docker-compose up --build

# Build individual images
docker build -f config/Dockerfile -t aqi-api .
docker build -f config/Dockerfile.dashboard -t aqi-dashboard .

# Run API container
docker run -d -p 8000:8000 aqi-api
```

### Health Check
```bash
curl http://localhost:8000/health
# {"status":"ok","model_loaded":true,"model_type":"LinearRegression"}
```
