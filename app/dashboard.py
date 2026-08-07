
at the end.

Those are only for displaying code in ChatGPT. **They must not be inside your Python file.**

There is also another problem in your code: you created `forecast_tab` but then tried to use `inventory_tab`, which doesn't exist. Since you wanted everything in one order, we don't need tabs at all.

### Replace your entire `dashboard.py`

Delete everything currently in the file and paste **only the code below**. Do **not** include ` ```python ` or ` ``` `.

```python
import streamlit as st
import pandas as pd
import calendar
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FORESIGHT Inventory Intelligence",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("NorthBay Living - Demand & Inventory Intelligence")

st.caption(
    "Inventory risk monitoring and demand forecasting dashboard"
)


# ============================================================
# LOAD INVENTORY DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "inventory_risk_report.csv"

try:
    inventory = pd.read_csv(DATA_FILE)

except FileNotFoundError:
    st.error(
        "Inventory data file not found. "
        "Please make sure inventory_risk_report.csv "
        "is inside the data folder."
    )
    st.stop()


# ============================================================
# 1. KPI VALUES
# ============================================================

st.header("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_skus = inventory["StockCode"].nunique()

stockout_risk = (
    inventory["Risk_Status"] == "Stockout Risk"
).sum()

overstock = (
    inventory["Risk_Status"] == "Overstock"
).sum()

sales_at_risk = inventory["Sales_At_Risk"].sum()


col1.metric(
    "Total SKUs",
    total_skus
)

col2.metric(
    "Stockout Risk",
    stockout_risk
)

col3.metric(
    "Overstock",
    overstock
)

col4.metric(
    "Sales At Risk",
    f"{sales_at_risk:,.2f}"
)


st.divider()


# ============================================================
# 2. INVENTORY DECISION
# ============================================================

st.header("📦 Inventory Decision")

sku = st.selectbox(
    "Select Product",
    inventory["Description"].dropna().unique()
)

selected = inventory[
    inventory["Description"] == sku
]

st.subheader("Selected Product Information")

st.dataframe(
    selected,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# 3. INVENTORY RISK DISTRIBUTION
# ============================================================

st.header("📈 Inventory Risk Distribution")

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
    text="Count",
    title="Inventory Risk Distribution"
)

fig.update_layout(
    xaxis_title="Risk Status",
    yaxis_title="Number of Products"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.divider()


# ============================================================
# 4. PRIORITY REORDER LIST
# ============================================================

st.header("🚨 Priority Reorder List")

reorder_list = inventory[
    inventory["Risk_Status"] == "Stockout Risk"
][
    [
        "StockCode",
        "Description",
        "Recommended_Order_Qty"
    ]
]

if len(reorder_list) > 0:

    st.dataframe(
        reorder_list,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No products currently require urgent reordering."
    )


st.divider()


# ============================================================
# 5. MARKDOWN CLEARANCE LIST
# ============================================================

st.header("💰 Markdown Clearance List")

clearance_list = inventory[
    inventory["Risk_Status"] == "Overstock"
][
    [
        "StockCode",
        "Description",
        "Capital_Locked"
    ]
]

if len(clearance_list) > 0:

    st.dataframe(
        clearance_list,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No products are currently classified as overstock."
    )


st.divider()


# ============================================================
# 6. DEMAND FORECAST SIMULATOR
# ============================================================

st.header("🔮 Demand Forecast Simulator")

st.caption(
    "Enter the forecast parameters below."
)


# ------------------------------------------------------------
# Forecast Product
# ------------------------------------------------------------

forecast_products = list(
    inventory["Description"]
    .dropna()
    .unique()
)

if "10 COLOUR SPACEBOY PEN" not in forecast_products:

    forecast_products.insert(
        0,
        "10 COLOUR SPACEBOY PEN"
    )

product = st.selectbox(
    "Forecast Product",
    forecast_products
)

st.caption(
    "Available sales history: 2 weeks"
)


# ------------------------------------------------------------
# Forecast Year
# ------------------------------------------------------------

forecast_year = st.number_input(
    "Forecast Year",
    min_value=2020,
    max_value=2100,
    value=2030,
    step=1
)


# ------------------------------------------------------------
# Forecast Month
# ------------------------------------------------------------

month_names = list(
    calendar.month_name
)[1:]

forecast_month = st.selectbox(
    "Forecast Month",
    options=range(1, 13),
    format_func=lambda x:
        f"{x} - {month_names[x - 1]}",
    index=3
)


# ------------------------------------------------------------
# Week of Month
# ------------------------------------------------------------

week_of_month = st.selectbox(
    "Week of Month",
    [1, 2, 3, 4, 5],
    index=2
)


# ------------------------------------------------------------
# Unit Price
# ------------------------------------------------------------

unit_price = st.number_input(
    "Unit Price",
    min_value=0.0,
    value=1.55,
    step=0.01,
    format="%.2f"
)


st.markdown("---")


# ============================================================
# GENERATE FORECAST BUTTON
# ============================================================

if st.button("Generate Forecast"):

    # Temporary forecast value
    # Replace this later with the actual forecasting model.

    forecast_demand = 439


    # --------------------------------------------------------
    # Calculate Week of Year
    # --------------------------------------------------------

    days_before_month = sum(
        calendar.monthrange(
            forecast_year,
            m
        )[1]
        for m in range(
            1,
            forecast_month
        )
    )

    week_of_year = (
        days_before_month // 7
    ) + week_of_month


    # --------------------------------------------------------
    # Calculate Quarter
    # --------------------------------------------------------

    quarter = (
        (forecast_month - 1) // 3
    ) + 1


    # --------------------------------------------------------
    # Forecast Result
    # --------------------------------------------------------

    st.success(
        f"Forecast Demand: {forecast_demand} units"
    )


    # --------------------------------------------------------
    # Forecast KPI Values
    # --------------------------------------------------------

    fcol1, fcol2, fcol3, fcol4 = st.columns(4)

    fcol1.metric(
        "Forecast Demand",
        f"{forecast_demand} units"
    )

    fcol2.metric(
        "Unit Price",
        f"{unit_price:.2f}"
    )

    fcol3.metric(
        "Week of Year",
        week_of_year
    )

    fcol4.metric(
        "Quarter",
        f"Q{quarter}"
    )


    # --------------------------------------------------------
    # Forecast Summary
    # --------------------------------------------------------

    st.subheader("📋 Forecast Summary")

    summary = pd.DataFrame(
        [{
            "Product Name": product,
            "Forecast Year": forecast_year,
            "Month":
                f"{forecast_month} - "
                f"{month_names[forecast_month - 1]}",
            "Week of Month":
                week_of_month,
            "Week of Year":
                week_of_year,
            "Quarter":
                quarter,
            "Unit Price":
                round(unit_price, 2),
            "Forecast Demand":
                forecast_demand
        }]
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )
