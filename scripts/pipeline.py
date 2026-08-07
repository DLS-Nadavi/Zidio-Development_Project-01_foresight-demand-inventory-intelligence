"""
FORESIGHT batch pipeline.
Run this offline to (re)generate all model artifacts and CSV reports
consumed by the Streamlit dashboard and FastAPI service.

Usage:
    python scripts/pipeline.py
"""

import os
import sys

import joblib
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core

RAW_DATA_PATH = "/dataset 2010_2011.csv"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("Loading raw data...")
    raw_df = pd.read_csv(RAW_DATA_PATH, encoding="latin1")
    print("Raw shape:", raw_df.shape)

    results = core.run_full_pipeline(raw_df)

    print("Seasonal Naive:", results["baseline_results"])
    print("XGBoost:", results["model_results"])
    print(results["comparison"])
    print(results["inventory"]["Risk_Status"].value_counts())

    # Save artifacts
    results["sales_daily"].to_csv(os.path.join(DATA_DIR, "sales_daily_clean.csv"), index=False)
    results["weekly_sales"].to_csv(os.path.join(DATA_DIR, "forecast_dataset.csv"), index=False)
    results["inventory"].to_csv(os.path.join(DATA_DIR, "inventory_risk_report.csv"), index=False)
    results["comparison"].to_csv(os.path.join(DATA_DIR, "forecast_model_results.csv"), index=False)

    joblib.dump(
        {"model": results["model"], "features": core.FEATURES},
        os.path.join(MODELS_DIR, "foresight_forecast_model.pkl"),
    )

    print("Pipeline completed successfully. Artifacts written to:", DATA_DIR, "and", MODELS_DIR)


if __name__ == "__main__":
    main()
