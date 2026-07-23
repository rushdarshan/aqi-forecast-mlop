"""
app.py — FastAPI REST API for next-day AQI forecasting.
Run: uvicorn src.app:app --reload
"""
import os, json, pickle
import numpy as np
import pandas as pd
from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

app = FastAPI(
    title="AQI Forecast API",
    description="Next-day Air Quality Index forecasting for 5 Indian cities",
    version="2.0.0",
)

# Load model artifacts at startup
def load_artifacts():
    meta_path = os.path.join(MODEL_DIR, "model_meta.json")
    if not os.path.exists(meta_path):
        return None, None, None
    with open(meta_path) as f:
        meta = json.load(f)
    with open(os.path.join(MODEL_DIR, "best_model.pkl"), "rb") as f:
        model = pickle.load(f)
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    return model, scaler, meta

MODEL, SCALER, META = load_artifacts()

CITIES = ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Bangalore"]
CITY_COLS = [f"City_{c}" for c in CITIES]
FEATURE_COLS = [
    "Month", "DayOfWeek", "DayOfYear", "IsWeekend",
    "AQI_lag1", "AQI_lag3_avg",
    "PM2.5_lag1", "PM2.5_lag3_avg",
    "PM10_lag1",  "PM10_lag3_avg",
] + CITY_COLS


class PredictRequest(BaseModel):
    city: str
    forecast_date: date  # date to forecast AQI for (model uses previous day's data)
    aqi_yesterday: float
    aqi_3day_avg: float
    pm25_yesterday: float
    pm25_3day_avg: float
    pm10_yesterday: float
    pm10_3day_avg: float


class PredictResponse(BaseModel):
    city: str
    forecast_date: str
    predicted_aqi: float
    aqi_category: str
    model_used: str
    r2_score: float


def aqi_category(aqi: float) -> str:
    if aqi <= 50:   return "Good"
    if aqi <= 100:  return "Satisfactory"
    if aqi <= 200:  return "Moderate"
    if aqi <= 300:  return "Poor"
    if aqi <= 400:  return "Very Poor"
    return "Severe"


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL is not None,
            "model_type": META["best_model"] if META else None}


@app.get("/model-info")
def model_info():
    if META is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return META


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not trained yet")
    if req.city not in CITIES:
        raise HTTPException(status_code=400,
                            detail=f"City must be one of {CITIES}")

    target_date = req.forecast_date
    row = {
        "Month":      target_date.month,
        "DayOfWeek":  target_date.weekday(),
        "DayOfYear":  target_date.timetuple().tm_yday,
        "IsWeekend":  int(target_date.weekday() >= 5),
        "AQI_lag1":   req.aqi_yesterday,
        "AQI_lag3_avg": req.aqi_3day_avg,
        "PM2.5_lag1": req.pm25_yesterday,
        "PM2.5_lag3_avg": req.pm25_3day_avg,
        "PM10_lag1":  req.pm10_yesterday,
        "PM10_lag3_avg": req.pm10_3day_avg,
    }
    for city in CITIES:
        row[f"City_{city}"] = 1 if city == req.city else 0

    X = pd.DataFrame([row])[FEATURE_COLS]

    if SCALER is not None:
        X = SCALER.transform(X)

    pred = float(MODEL.predict(X)[0])
    pred = max(0, round(pred, 1))

    return PredictResponse(
        city=req.city,
        forecast_date=str(target_date),
        predicted_aqi=pred,
        aqi_category=aqi_category(pred),
        model_used=META["best_model"],
        r2_score=META["metrics"]["R2"],
    )


@app.get("/cities")
def cities():
    return {"cities": CITIES}
