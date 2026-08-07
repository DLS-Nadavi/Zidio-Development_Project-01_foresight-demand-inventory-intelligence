
# Project FORESIGHT

## NorthBay Living Demand & Inventory Intelligence

## Objective

Predict SKU demand, identify inventory risk,
and recommend business actions.

## ML Model

**Model:** XGBoost Regressor

**Baseline:** Seasonal Naive Forecast

### Performance

| Model | WAPE | RMSE |
|---|---:|---:|
| XGBoost | 20.15% | 43.72 |
| Seasonal Naive | 86.48% | 157.14 |

## Pipeline

Raw Data
↓
Cleaning
↓
Feature Engineering
↓
Demand Forecast Model
↓
Inventory Risk Engine
↓
Dashboard + API

## Outputs

- Demand Forecast
- Stockout Risk
- Overstock Risk
- Reorder Quantity
- Sales At Risk
- Capital Locked

## Run Dashboard

```bash
streamlit run app/dashboard.py

## Run API
uvicorn service.api:app --reload
