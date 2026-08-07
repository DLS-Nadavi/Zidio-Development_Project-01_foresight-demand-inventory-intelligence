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
    "Demand forecasting and inventory decision support"
)


# ============================================================
# LOAD INVENTORY DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "inventory_risk_report.csv"

try:
    inventory = pd.read_csv(DATA_FILE)

except FileNotFoundError:
    st.error(
        "Inventory data file not found. "
        "Please make sure the file exists at: "
        "data/inventory_risk_report.csv"
    )
    st.stop()


# ============================================================
# TABS
# ============================================================

forecast_tab, inventory_tab = st.tabs(
    [
        "Demand Forecast Simulator"
    ]
)


# ============================================================
# DEMAND FORECAST TAB
# ============================================================

with forecast_tab:

    st.header("Demand Forecast Simulator")

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    product = st.selectbox(
        "Forecast Product",
        ["10 COLOUR SPACEBOY PEN"]
    )

    st.caption(
        "Available sales history: 2 weeks"
    )

    # --------------------------------------------------------
    # Forecast Year
    # --------------------------------------------------------

    forecast_year = st.number_input(
        "Forecast Year",
        min_value=2020,
        max_value=2100,
        value=2030,
        step=1
    )

    # --------------------------------------------------------
    # Forecast Month
    # --------------------------------------------------------

    month_names = list(calendar.month_name)[1:]

    forecast_month = st.selectbox(
        "Forecast Month",
        options=range(1, 13),
        format_func=lambda x:
            f"{x} - {month_names[x - 1]}",
        index=3
    )

    # --------------------------------------------------------
    # Week of Month
    # --------------------------------------------------------

    week_of_month = st.selectbox(
        "Week of Month",
        [1, 2, 3, 4, 5],
        index=2
    )

    # --------------------------------------------------------
    # Unit Price
    # --------------------------------------------------------

    unit_price = st.number_input(
        "Unit Price",
        min_value=0.0,
        value=1.55,
        step=0.01,
        format="%.2f"
    )

    st.divider()

    # --------------------------------------------------------
    # Generate Forecast
    # --------------------------------------------------------

    if st.button("Generate Forecast"):

        # ----------------------------------------------------
        # TEMPORARY FORECAST
        # ----------------------------------------------------
        # Replace this with your actual forecasting model.
        # ----------------------------------------------------

        forecast_demand = 439

        # ----------------------------------------------------
        # Week of Year
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Quarter
        # ----------------------------------------------------

        quarter = (
            (forecast_month - 1) // 3
        ) + 1

        # ----------------------------------------------------
        # Forecast Result
        # ----------------------------------------------------

        st.success(
            f"Forecast Demand: {forecast_demand} units"
        )

        # ----------------------------------------------------
        # Forecast KPIs
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Forecast Demand",
            f"{forecast_demand} units"
        )

        col2.metric(
            "Unit Price",
            f"{unit_price:.2f}"
        )

        col3.metric(
            "Week of Year",
            week_of_year
        )

        col4.metric(
            "Quarter",
            f"Q{quarter}"
        )

        # ----------------------------------------------------
        # Forecast Summary
        # ----------------------------------------------------

        st.subheader(
            "📊 Forecast Summary"
        )

        summary = pd.DataFrame(
            [
                {
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
                }
            ]
        )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# INVENTORY INTELLIGENCE TAB
# ============================================================

with inventory_tab:

    st.header(
        "Inventory Intelligence"
    )

    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total SKUs",
        inventory["StockCode"].nunique()
    )

    col2.metric(
        "Stockout Risk",
        (
            inventory["Risk_Status"]
            == "Stockout Risk"
        ).sum()
    )

    col3.metric(
        "Overstock",
        (
            inventory["Risk_Status"]
            == "Overstock"
        ).sum()
    )

    col4.metric(
        "Sales At Risk",
        round(
            inventory["Sales_At_Risk"].sum(),
            2
        )
    )

    st.divider()

    # --------------------------------------------------------
    # SKU FILTER
    # --------------------------------------------------------

    sku = st.selectbox(
        "Select Product",
        inventory["Description"].unique()
    )

    selected = inventory[
        inventory["Description"] == sku
    ]

    # --------------------------------------------------------
    # INVENTORY DECISION
    # --------------------------------------------------------

    st.subheader(
        "📦 Inventory Decision"
    )

    st.dataframe(
        selected,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # RISK GRAPH
    # --------------------------------------------------------

    st.subheader(
        "📊 Inventory Risk Distribution"
    )

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
        title="Inventory Risk Distribution",
        text="Count"
    )

    fig.update_layout(
        xaxis_title="Risk Status",
        yaxis_title="Number of Products"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # PRIORITY REORDER LIST
    # --------------------------------------------------------

    st.subheader(
        "🚨 Priority Reorder List"
    )

    reorder_list = inventory[
        inventory["Risk_Status"]
        == "Stockout Risk"
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

    # --------------------------------------------------------
    # MARKDOWN CLEARANCE LIST
    # --------------------------------------------------------

    st.subheader(
        "💰 Markdown Clearance List"
    )

    clearance_list = inventory[
        inventory["Risk_Status"]
        == "Overstock"
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
```
