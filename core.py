"""
FORESIGHT core pipeline functions.
Shared by scripts/pipeline.py (batch training) and app/dashboard.py (interactive app).
"""

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

FEATURES = [
    "Unit_Price", "Year", "Month", "Quarter", "Week",
    "Demand_Lag_1", "Demand_Lag_2", "Rolling_Mean_2",
]


# ------------------------------------------------------------------
# Data cleaning & aggregation
# ------------------------------------------------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df = df.dropna(subset=["Description"])
    if "Customer ID" in df.columns:
        df["Customer ID"] = df["Customer ID"].fillna(0).astype(int)
    df = df.drop_duplicates()
    if "Invoice" in df.columns:
        df = df[~df["Invoice"].astype(str).str.startswith("C")]
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]
    df["Revenue"] = df["Quantity"] * df["Price"]
    df["Date"] = pd.to_datetime(df["InvoiceDate"].dt.date)
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    return df


def make_sales_daily(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Date", "StockCode", "Description"])
        .agg(
            Units_Sold=("Quantity", "sum"),
            Revenue=("Revenue", "sum"),
            Unit_Price=("Price", "mean"),
        )
        .reset_index()
    )


def make_weekly_sales(sales_daily: pd.DataFrame) -> pd.DataFrame:
    return (
        sales_daily.set_index("Date")
        .groupby(["StockCode", "Description"])
        .resample("W")
        .agg(
            Units_Sold=("Units_Sold", "sum"),
            Revenue=("Revenue", "sum"),
            Unit_Price=("Unit_Price", "mean"),
        )
        .reset_index()
    )


# ------------------------------------------------------------------
# Forecasting features & model
# ------------------------------------------------------------------
def add_model_features(weekly_sales: pd.DataFrame) -> pd.DataFrame:
    weekly_sales = weekly_sales.sort_values(["StockCode", "Date"]).reset_index(drop=True)

    weekly_sales["Year"] = weekly_sales["Date"].dt.year
    weekly_sales["Month"] = weekly_sales["Date"].dt.month
    weekly_sales["Quarter"] = weekly_sales["Date"].dt.quarter
    weekly_sales["Week"] = weekly_sales["Date"].dt.isocalendar().week.astype(int)
    weekly_sales["Day"] = weekly_sales["Date"].dt.day
    weekly_sales["DayOfWeek"] = weekly_sales["Date"].dt.dayofweek

    for lag in [1, 2]:
        weekly_sales[f"Demand_Lag_{lag}"] = (
            weekly_sales.groupby("StockCode")["Units_Sold"].shift(lag)
        )

    weekly_sales["Rolling_Mean_2"] = (
        weekly_sales.groupby("StockCode")["Units_Sold"]
        .shift(1)
        .rolling(4)
        .mean()
        .reset_index(level=0, drop=True)
    )

    weekly_sales["Naive_Forecast"] = (
        weekly_sales.groupby("StockCode")["Units_Sold"].shift(52)
    )

    return weekly_sales.dropna().reset_index(drop=True)


def time_based_split(weekly_sales: pd.DataFrame, train_frac: float = 0.8):
    weekly_sales = weekly_sales.sort_values("Date").reset_index(drop=True)
    split_index = int(len(weekly_sales) * train_frac)
    return weekly_sales.iloc[:split_index], weekly_sales.iloc[split_index:]


def calculate_metrics(actual, prediction) -> dict:
    actual = np.asarray(actual, dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    wape = np.sum(np.abs(actual - prediction)) / np.sum(np.abs(actual))
    rmse = np.sqrt(np.mean((prediction - actual) ** 2))
    bias = np.mean(prediction - actual)
    return {"WAPE": round(float(wape), 4), "RMSE": round(float(rmse), 2), "Bias": round(float(bias), 4)}


def train_xgb(X_train, y_train, **kwargs) -> XGBRegressor:
    params = dict(n_estimators=500, learning_rate=0.05, max_depth=6,
                  subsample=0.8, colsample_bytree=0.8, random_state=42)
    params.update(kwargs)
    model = XGBRegressor(**params)
    model.fit(X_train, y_train)
    return model


# ------------------------------------------------------------------
# Inventory risk engine
# ------------------------------------------------------------------
def build_inventory_profile(sales_daily: pd.DataFrame) -> pd.DataFrame:
    return (
        sales_daily.groupby(["StockCode", "Description"])
        .agg(
            Total_Units_Sold=("Units_Sold", "sum"),
            Total_Revenue=("Revenue", "sum"),
            Average_Price=("Unit_Price", "mean"),
            Active_Days=("Date", "nunique"),
        )
        .reset_index()
    )


def simulate_inventory_snapshot(inventory: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Simulated on-hand/on-order snapshot. Replace with a real inventory feed in production."""
    inventory = inventory.copy()
    rng = np.random.default_rng(seed)
    inventory["On_Hand_Units"] = rng.integers(20, 500, size=len(inventory))
    inventory["On_Order_Units"] = rng.integers(0, 200, size=len(inventory))
    inventory["Lead_Time_Days"] = rng.integers(3, 21, size=len(inventory))
    return inventory


def add_risk_engine(inventory: pd.DataFrame, weekly_sales: pd.DataFrame, service_factor: float = 0.2) -> pd.DataFrame:
    inventory = inventory.copy()

    inventory["Daily_Demand"] = inventory["Total_Units_Sold"] / inventory["Active_Days"]
    inventory["Weekly_Demand"] = inventory["Daily_Demand"] * 7
    inventory["Safety_Stock"] = inventory["Weekly_Demand"] * service_factor
    inventory["Reorder_Point"] = (
        inventory["Daily_Demand"] * inventory["Lead_Time_Days"] + inventory["Safety_Stock"]
    )

    future_forecast = (
        weekly_sales.sort_values(["StockCode", "Date"])
        .groupby(["StockCode", "Description"])
        .tail(8)
        .groupby(["StockCode", "Description"])["Units_Sold"]
        .mean()
        .reset_index()
        .rename(columns={"Units_Sold": "Forecast_8_Week_Demand"})
    )
    inventory = inventory.merge(future_forecast, on=["StockCode", "Description"], how="left")
    inventory["Forecast_8_Week_Demand"] = inventory["Forecast_8_Week_Demand"].fillna(0)

    def risk_status(row):
        available = row["On_Hand_Units"] + row["On_Order_Units"]
        if available < row["Forecast_8_Week_Demand"] + row["Safety_Stock"]:
            return "Stockout Risk"
        elif row["On_Hand_Units"] > row["Forecast_8_Week_Demand"] * 2:
            return "Overstock"
        return "Healthy"

    def recommended_action(row):
        if row["Risk_Status"] == "Stockout Risk":
            return "Reorder Now"
        elif row["Risk_Status"] == "Overstock":
            return "Markdown / Clear"
        return "No Action"

    inventory["Risk_Status"] = inventory.apply(risk_status, axis=1)
    inventory["Recommended_Action"] = inventory.apply(recommended_action, axis=1)

    inventory["Recommended_Order_Qty"] = (
        inventory["Forecast_8_Week_Demand"] + inventory["Safety_Stock"] - inventory["On_Hand_Units"]
    ).clip(lower=0).round()

    inventory["Sales_At_Risk"] = np.where(
        inventory["Risk_Status"] == "Stockout Risk",
        inventory["Forecast_8_Week_Demand"] * inventory["Average_Price"],
        0,
    )
    inventory["Capital_Locked"] = np.where(
        inventory["Risk_Status"] == "Overstock",
        (inventory["On_Hand_Units"] - inventory["Forecast_8_Week_Demand"]) * inventory["Average_Price"],
        0,
    )

    inventory["Stockout_Score"] = (
        inventory["Forecast_8_Week_Demand"] / (inventory["On_Hand_Units"] + inventory["On_Order_Units"] + 1)
    )
    inventory["Overstock_Score"] = inventory["On_Hand_Units"] / (inventory["Forecast_8_Week_Demand"] + 1)

    return inventory


def run_full_pipeline(raw_df: pd.DataFrame):
    """Runs cleaning -> aggregation -> forecasting model -> inventory risk engine.
    Returns a dict of all key artifacts."""
    clean = clean_data(raw_df)
    sales_daily = make_sales_daily(clean)
    weekly_sales = make_weekly_sales(sales_daily)
    weekly_sales = add_model_features(weekly_sales)

    train, test = time_based_split(weekly_sales)
    X_train, y_train = train[FEATURES], train["Units_Sold"]
    X_test, y_test = test[FEATURES], test["Units_Sold"]

    baseline_results = calculate_metrics(test["Units_Sold"], test["Naive_Forecast"])

    model = train_xgb(X_train, y_train)
    forecast = np.maximum(model.predict(X_test), 0)
    model_results = calculate_metrics(y_test, forecast)

    comparison = pd.DataFrame({
        "Model": ["Seasonal Naive", "XGBoost"],
        "WAPE": [baseline_results["WAPE"], model_results["WAPE"]],
        "RMSE": [baseline_results["RMSE"], model_results["RMSE"]],
        "Bias": [baseline_results["Bias"], model_results["Bias"]],
    })

    inventory = build_inventory_profile(sales_daily)
    inventory = simulate_inventory_snapshot(inventory)
    inventory = add_risk_engine(inventory, weekly_sales)

    return {
        "clean": clean,
        "sales_daily": sales_daily,
        "weekly_sales": weekly_sales,
        "train": train,
        "test": test,
        "forecast": forecast,
        "model": model,
        "baseline_results": baseline_results,
        "model_results": model_results,
        "comparison": comparison,
        "inventory": inventory,
    }
