
from fastapi import FastAPI
import pandas as pd
import joblib

app = FastAPI(
    title="FORESIGHT Forecast API"
)

bundle = joblib.load(
    "foresight/models/foresight_forecast_model.pkl"
)

model = bundle["model"]
features = bundle["features"]


@app.get("/")
def home():
    return {
        "service": "NorthBay Living Forecast API",
        "status": "running"
    }


@app.post("/predict")
def predict(data: dict):
    input_df = pd.DataFrame(
        [data]
    )

    input_df = input_df[features]

    prediction = model.predict(
        input_df
    )

    forecast_value = float(
        max(prediction[0], 0)
    )

    return {
        "forecast": forecast_value,
        "status": "Forecast Generated"
    }
