import streamlit as st
import pandas as pd
import calendar
import plotly.express as px
import joblib

from pathlib import Path

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FORESIGHT Inventory Intelligence",
    page_icon=None,
    layout="wide"
)


# ============================================================
# PAGE TITLE
# ============================================================

st.title("NorthBay Living - Demand & Inventory Intelligence")

st.caption(
    "Demand forecasting and inventory decision support"
)


# ============================================================
# LOAD INVENTORY DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR.parent / "data" / "inventory_risk_report.csv"

inventory = None

if DATA_FILE.exists():

    try:
        inventory = pd.read_csv(DATA_FILE)

    except Exception as e:

        st.error(
            f"Unable to load inventory data: {e}"
        )

else:

    st.warning(
        "Inventory data file was not found."
    )

    st.info(
        f"Expected file location: {DATA_FILE}"
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* KPI cards */

    .kpi-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        min-height: 110px;
    }

    .kpi-title {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
    }


    /* Forecast result */

    .forecast-result {
    background-color: #d9f5df;
    border: 1px solid #a7dfb2;
    border-radius: 5px;
    padding: 22px;
    margin-top: 20px;
    margin-bottom: 20px;
}

    .forecast-label {
        font-size: 15px;
        color: #356b42;
        margin-bottom: 5px;
    }

    .forecast-value {
    font-size: 15px;
    font-weight: 400;
    color: #245c32;
}


    /* Section headings */

    .section-title {
        margin-top: 15px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 1. KPI VALUES
# ============================================================

st.header("KPI Values")

if inventory is not None:

    required_columns = [
        "StockCode",
        "Description",
        "Risk_Status",
        "Sales_At_Risk",
        "Recommended_Order_Qty",
        "Capital_Locked"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in inventory.columns
    ]

    if missing_columns:

        st.error(
            "The inventory file is missing the following columns: "
            + ", ".join(missing_columns)
        )

        inventory_valid = False

    else:

        inventory_valid = True

        # Clean columns

        inventory["Risk_Status"] = (
            inventory["Risk_Status"]
            .astype(str)
            .str.strip()
        )

        inventory["Sales_At_Risk"] = pd.to_numeric(
            inventory["Sales_At_Risk"],
            errors="coerce"
        ).fillna(0)

        inventory["Recommended_Order_Qty"] = pd.to_numeric(
            inventory["Recommended_Order_Qty"],
            errors="coerce"
        ).fillna(0)

        inventory["Capital_Locked"] = pd.to_numeric(
            inventory["Capital_Locked"],
            errors="coerce"
        ).fillna(0)


else:

    inventory_valid = False


if inventory_valid:

    total_skus = inventory[
        "StockCode"
    ].nunique()

    stockout_risk = (
        inventory["Risk_Status"]
        == "Stockout Risk"
    ).sum()

    overstock = (
        inventory["Risk_Status"]
        == "Overstock"
    ).sum()

    sales_at_risk = inventory[
        "Sales_At_Risk"
    ].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Total SKUs</div>
                <div class="kpi-value">{total_skus:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Stockout Risk</div>
                <div class="kpi-value">{stockout_risk:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Overstock</div>
                <div class="kpi-value">{overstock:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Sales At Risk</div>
                <div class="kpi-value">{sales_at_risk:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:

    st.info(
        "Inventory KPIs will appear when the inventory data is available."
    )


st.divider()


# ============================================================
# 2. INVENTORY DECISION
# ============================================================

st.header("Inventory Decision")

if inventory_valid:

    descriptions = (
        inventory["Description"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if descriptions:

        selected_product = st.selectbox(
            "Select Product",
            descriptions
        )

        selected = inventory[
            inventory["Description"].astype(str)
            == selected_product
        ]

        st.dataframe(
            selected,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No product descriptions are available."
        )

else:

    st.info(
        "Inventory decision data is unavailable."
    )


st.divider()


# ============================================================
# 3. INVENTORY RISK DISTRIBUTION
# ============================================================

st.header("Inventory Risk Distribution")

if inventory_valid:

    risk = (
        inventory["Risk_Status"]
        .value_counts()
        .reset_index()
    )

    risk.columns = [
        "Risk",
        "Count"
    ]

    fig = px.bar(
        risk,
        x="Risk",
        y="Count",
        text="Count"
    )

    fig.update_layout(
        title="Inventory Risk Distribution",
        xaxis_title="Risk Status",
        yaxis_title="Number of Products",
        showlegend=False
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "Risk distribution will appear when inventory data is available."
    )


st.divider()


# ============================================================
# 4. PRIORITY ORDER LIST
# ============================================================

st.header("Priority Order List")

if inventory_valid:

    reorder_list = inventory[
        inventory["Risk_Status"]
        == "Stockout Risk"
    ][
        [
            "StockCode",
            "Description",
            "Recommended_Order_Qty"
        ]
    ].copy()

    if not reorder_list.empty:

        st.dataframe(
            reorder_list,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No products currently require urgent reordering."
        )

else:

    st.info(
        "Priority order information is unavailable."
    )


st.divider()


# ============================================================
# 5. MARKDOWN CLEARANCE LIST
# ============================================================

st.header("Markdown Clearance List")

if inventory_valid:

    clearance_list = inventory[
        inventory["Risk_Status"]
        == "Overstock"
    ][
        [
            "StockCode",
            "Description",
            "Capital_Locked"
        ]
    ].copy()

    if not clearance_list.empty:

        st.dataframe(
            clearance_list,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No products are currently classified as overstock."
        )

else:

    st.info(
        "Markdown clearance information is unavailable."
    )


st.divider()


# ============================================================
# LOAD DEMAND FORECASTING MODEL
# ============================================================

MODEL_FILE = (
    BASE_DIR.parent
    / "models"
    / "foresight_forecast_model.pkl"
)

FORECAST_DATA_FILE = (
    BASE_DIR.parent
    / "data"
    / "forecast_dataset.csv"
)

forecast_model = None
forecast_features = [
    "Unit_Price",
    "Year",
    "Month",
    "Quarter",
    "Week",
    "Demand_Lag_1",
    "Demand_Lag_2",
    "Rolling_Mean_2"
]

forecast_history = None


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

if MODEL_FILE.exists():

    try:

        model_package = joblib.load(
            MODEL_FILE
        )

        # Model saved from Google Colab
        forecast_model = model_package["model"]

        # Use the features saved with the model if available
        saved_features = model_package.get(
            "features",
            forecast_features
        )

        if saved_features:
            forecast_features = saved_features

    except Exception as e:

        st.error(
            f"Unable to load forecasting model: {e}"
        )

else:

    st.warning(
        "Demand forecasting model was not found."
    )

    st.info(
        f"Expected file: {MODEL_FILE}"
    )


# ============================================================
# LOAD FORECAST DATASET
# ============================================================

if FORECAST_DATA_FILE.exists():

    try:

        forecast_history = pd.read_csv(
            FORECAST_DATA_FILE
        )

    except Exception as e:

        st.error(
            f"Unable to load forecast dataset: {e}"
        )

else:

    st.warning(
        "Forecast dataset was not found."
    )

    st.info(
        f"Expected file: {FORECAST_DATA_FILE}"
    )


# ============================================================
# 6. DEMAND FORECAST SIMULATOR
# ============================================================

st.header("Demand Forecast Simulator")

st.write(
    "Enter the forecast parameters and generate the expected demand."
)


# ============================================================
# FORECAST PRODUCTS
# ============================================================

if inventory_valid:

    forecast_products = (
        inventory["Description"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

else:

    forecast_products = []


if forecast_products:

    product_options = {}

    # Minimum historical weeks required
    required_weeks = 2

    for product_name in forecast_products:

        available_weeks = 0

        # ----------------------------------------------------
        # FIND PRODUCT HISTORY
        # ----------------------------------------------------

        if forecast_history is not None:

            history_product = forecast_history.copy()

            # Match using Description
            if "Description" in history_product.columns:

                history_product["Description"] = (
                    history_product["Description"]
                    .astype(str)
                    .str.strip()
                )

                history_product = history_product[
                    history_product["Description"]
                    == product_name
                ]

            # Otherwise match using StockCode
            elif "StockCode" in history_product.columns:

                inventory_product = inventory[
                    inventory["Description"]
                    .astype(str)
                    .str.strip()
                    == product_name
                ]

                if not inventory_product.empty:

                    stock_code = str(
                        inventory_product.iloc[0]["StockCode"]
                    )

                    history_product["StockCode"] = (
                        history_product["StockCode"]
                        .astype(str)
                        .str.strip()
                    )

                    history_product = history_product[
                        history_product["StockCode"]
                        == stock_code
                    ]

            # ------------------------------------------------
            # COUNT AVAILABLE WEEKS
            # ------------------------------------------------

            if not history_product.empty:

                if "Date" in history_product.columns:

                    dates = pd.to_datetime(
                        history_product["Date"],
                        errors="coerce"
                    ).dropna()

                    available_weeks = int(
                        dates.dt.to_period("W").nunique()
                    )

                elif "Week" in history_product.columns:

                    available_weeks = int(
                        history_product["Week"]
                        .nunique()
                    )

        # ----------------------------------------------------
        # AVAILABILITY MARK
        # ----------------------------------------------------

        if available_weeks >= required_weeks:

            label = (
                f"{product_name} - "
                f"✅ Available ({available_weeks} weeks)"
            )

        else:

            label = (
                f"{product_name} - "
                f"❌ Not Available ({available_weeks} weeks)"
            )

        product_options[label] = product_name


    # ========================================================
    # FORECAST PRODUCT
    # ========================================================

    selected_product_label = st.selectbox(
        "Forecast Product",
        options=list(product_options.keys()),
        key="df_simulator_product_select_01"
    )

    product = product_options[
        selected_product_label
    ]

else:

    st.warning(
        "No products are available for forecasting."
    )

    product = None


# ============================================================
# FORECAST YEAR
# ============================================================

forecast_year = st.number_input(
    "Forecast Year",
    min_value=2020,
    max_value=2100,
    value=2030,
    step=1,
    key="df_simulator_year_01"
)


# ============================================================
# FORECAST MONTH
# ============================================================

month_names = list(
    calendar.month_name
)[1:]

forecast_month = st.selectbox(
    "Forecast Month",
    options=range(1, 13),
    format_func=lambda x:
        f"{x} - {month_names[x - 1]}",
    index=3,
    key="df_simulator_month_01"
)


# ============================================================
# WEEK OF MONTH
# ============================================================

week_of_month = st.selectbox(
    "Week of Month",
    [1, 2, 3, 4, 5],
    index=2,
    key="df_simulator_week_01"
)


# ============================================================
# UNIT PRICE
# ============================================================

unit_price = st.number_input(
    "Unit Price",
    min_value=0.0,
    value=1.55,
    step=0.01,
    format="%.2f",
    key="df_simulator_price_01"
)


st.write("")


# ============================================================
# GENERATE FORECAST BUTTON
# ============================================================

generate_forecast = st.button(
    "Generate Forecast",
    key="df_simulator_generate_01"
)


# ============================================================
# FORECAST
# ============================================================

if generate_forecast and product is not None:

    # --------------------------------------------------------
    # CHECK MODEL
    # --------------------------------------------------------

    if forecast_model is None:

        st.error(
            "Demand forecasting model is not loaded."
        )

        st.stop()


    # --------------------------------------------------------
    # CHECK FORECAST HISTORY
    # --------------------------------------------------------

    if forecast_history is None:

        st.error(
            "Forecast history dataset is not loaded."
        )

        st.stop()


    try:

        # ====================================================
        # COPY FORECAST HISTORY
        # ====================================================

        history = forecast_history.copy()


        # ====================================================
        # FIND SELECTED PRODUCT HISTORY
        # ====================================================

        if "Description" in history.columns:

            history["Description"] = (
                history["Description"]
                .astype(str)
                .str.strip()
            )

            product_history = history[
                history["Description"] == product
            ].copy()

        elif "StockCode" in history.columns:

            selected_inventory = inventory[
                inventory["Description"]
                .astype(str)
                .str.strip()
                == product
            ]

            if selected_inventory.empty:

                st.error(
                    "Selected product could not be matched "
                    "to the forecast history."
                )

                st.stop()

            stock_code = str(
                selected_inventory.iloc[0]["StockCode"]
            )

            history["StockCode"] = (
                history["StockCode"]
                .astype(str)
                .str.strip()
            )

            product_history = history[
                history["StockCode"] == stock_code
            ].copy()

        else:

            st.error(
                "Forecast dataset must contain either "
                "'Description' or 'StockCode'."
            )

            st.stop()


        # ====================================================
        # CHECK PRODUCT HISTORY
        # ====================================================

        if product_history.empty:

            st.error(
                f"No historical demand data was found "
                f"for '{product}'."
            )

            st.stop()


        # ====================================================
        # CONVERT DATE
        # ====================================================

        if "Date" in product_history.columns:

            product_history["Date"] = pd.to_datetime(
                product_history["Date"],
                errors="coerce"
            )

            product_history = (
                product_history
                .dropna(subset=["Date"])
                .sort_values("Date")
            )


        # ====================================================
        # CONVERT UNITS SOLD
        # ====================================================

        if "Units_Sold" not in product_history.columns:

            st.error(
                "Forecast dataset does not contain "
                "'Units_Sold'."
            )

            st.stop()


        product_history["Units_Sold"] = pd.to_numeric(
            product_history["Units_Sold"],
            errors="coerce"
        )

        product_history = product_history.dropna(
            subset=["Units_Sold"]
        )


        # ====================================================
        # REQUIRE TWO HISTORICAL DEMAND VALUES
        # ====================================================

        if len(product_history) < 2:

            st.error(
                f"'{product}' has only "
                f"{len(product_history)} valid historical "
                "demand record(s). "
                "At least 2 are required for forecasting."
            )

            st.stop()


        # ====================================================
        # DEMAND LAG 1
        # ====================================================

        demand_lag_1 = float(
            product_history["Units_Sold"].iloc[-1]
        )


        # ====================================================
        # DEMAND LAG 2
        # ====================================================

        demand_lag_2 = float(
            product_history["Units_Sold"].iloc[-2]
        )


        # ====================================================
        # ROLLING MEAN 2
        # ====================================================

        rolling_mean_2 = (
            demand_lag_1 +
            demand_lag_2
        ) / 2


        # ====================================================
        # CALCULATE WEEK OF YEAR
        # ====================================================

        days_before_month = sum(
            calendar.monthrange(
                int(forecast_year),
                month
            )[1]
            for month in range(
                1,
                int(forecast_month)
            )
        )

        week_of_year = (
            days_before_month // 7
        ) + int(week_of_month)


        # ====================================================
        # CALCULATE QUARTER
        # ====================================================

        quarter = (
            (int(forecast_month) - 1) // 3
        ) + 1


        # ====================================================
        # CREATE MODEL INPUT
        # ====================================================

        forecast_input = pd.DataFrame(
            [
                {
                    "Unit_Price": float(
                        unit_price
                    ),

                    "Year": int(
                        forecast_year
                    ),

                    "Month": int(
                        forecast_month
                    ),

                    "Quarter": int(
                        quarter
                    ),

                    "Week": int(
                        week_of_year
                    ),

                    "Demand_Lag_1": float(
                        demand_lag_1
                    ),

                    "Demand_Lag_2": float(
                        demand_lag_2
                    ),

                    "Rolling_Mean_2": float(
                        rolling_mean_2
                    )
                }
            ]
        )


        # ====================================================
        # CHECK MODEL FEATURES
        # ====================================================

        missing_features = [
            feature
            for feature in forecast_features
            if feature not in forecast_input.columns
        ]

        if missing_features:

            st.error(
                "The forecasting model requires these "
                "features, but they are missing: "
                + ", ".join(missing_features)
            )

            st.stop()


        # ====================================================
        # SELECT EXACT TRAINING FEATURES
        # ====================================================

        forecast_input = forecast_input[
            forecast_features
        ]


        # ====================================================
        # MODEL PREDICTION
        # ====================================================

        prediction = forecast_model.predict(
            forecast_input
        )


        # ====================================================
        # GET FORECAST VALUE
        # ====================================================

        forecast_demand = float(
            prediction[0]
        )


        # ====================================================
        # PREVENT NEGATIVE FORECAST
        # ====================================================

        forecast_demand = max(
            0,
            forecast_demand
        )


        # ====================================================
        # FORECAST RESULT
        # ====================================================

        st.markdown(
            f"""
            <div class="forecast-result">
                <div class="forecast-value">
                    Forecast Demand:
                    {forecast_demand:,.0f} units
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # FORECAST SUMMARY
        # ====================================================

        st.subheader(
            "Forecast Summary"
        )

        summary = pd.DataFrame(
            [
                {
                    "Product Name": product,

                    "Forecast Year": int(
                        forecast_year
                    ),

                    "Month": (
                        f"{forecast_month} - "
                        f"{month_names[forecast_month - 1]}"
                    ),

                    "Week of Month": int(
                        week_of_month
                    ),

                    "Week of Year": int(
                        week_of_year
                    ),

                    "Quarter": f"Q{quarter}",

                    "Unit Price": round(
                        float(unit_price),
                        2
                    ),

                    "Forecast Demand": round(
                        forecast_demand
                    )
                }
            ]
        )


        # ====================================================
        # SUMMARY TABLE
        # ====================================================

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                column: st.column_config.Column(
                    alignment="center"
                )
                for column in summary.columns
            }
        )


    except Exception as e:

        st.error(
            f"Unable to generate forecast: {e}"
        )
