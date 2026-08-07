"""
FORESIGHT Forecast API
Serves demand predictions from the trained model saved by scripts/pipeline.py.
Run: uvicorn service.api:app --reload
"""

import os

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "foresight_forecast_model.pkl",
)

app = FastAPI(title="FORESIGHT Forecast API")

_bundle = None


def get_bundle():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(status_code=503, detail="Model not found. Run scripts/pipeline.py first.")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


@app.get("/")
def home():
    return {"service": "NorthBay Living Forecast API", "status": "running"}


@app.post("/predict")
def predict(data: dict):
    bundle = get_bundle()
    model = bundle["model"]
    features = bundle["features"]

    missing = [f for f in features if f not in data]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing features: {missing}")

    input_df = pd.DataFrame([data])[features]
    prediction = model.predict(input_df)
    forecast_value = float(max(prediction[0], 0))
    return {"forecast": forecast_value, "status": "Forecast Generated"}
