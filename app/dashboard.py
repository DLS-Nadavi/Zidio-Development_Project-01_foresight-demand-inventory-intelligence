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

```python
# ============================================================
# 6. DEMAND FORECAST SIMULATOR
# ============================================================

st.header("Demand Forecast Simulator")

st.write(
    "Enter the forecast parameters and generate the expected demand."
)


# ============================================================
# FORECAST PRODUCT DROPDOWN
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

    # --------------------------------------------------------
    # Create product dropdown options
    # --------------------------------------------------------

    product_options = {}

    for product_name in forecast_products:

        # ----------------------------------------------------
        # TEMPORARY AVAILABILITY VALUE
        # ----------------------------------------------------
        # Currently set to 2 weeks for demonstration.
        #
        # Replace this with the actual sales-history
        # calculation when sales-history data is connected.
        # ----------------------------------------------------

        available_weeks = 2


        # ----------------------------------------------------
        # AVAILABLE PRODUCT
        # ----------------------------------------------------

        if available_weeks > 0:

            label = (
                f"✅ {product_name} - "
                f"Available ({available_weeks} weeks)"
            )


        # ----------------------------------------------------
        # NON-AVAILABLE PRODUCT
        # ----------------------------------------------------

        else:

            label = (
                f"❌ {product_name} - "
                f"Not Available (0 weeks)"
            )


        product_options[label] = product_name


    # --------------------------------------------------------
    # PRODUCT DROPDOWN
    # --------------------------------------------------------

    selected_product_label = st.selectbox(
        "Forecast Product",
        options=list(product_options.keys()),
        key="df_simulator_product_select_01"
    )


    # --------------------------------------------------------
    # GET ORIGINAL PRODUCT NAME
    # --------------------------------------------------------

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
# FORECAST BUTTON
# ============================================================

generate_forecast = st.button(
    "Generate Forecast",
    key="df_simulator_generate_01"
)


# ============================================================
# FORECAST RESULT
# ============================================================

if generate_forecast and product is not None:

    # --------------------------------------------------------
    # TEMPORARY FORECAST VALUE
    # --------------------------------------------------------
    # Replace this value with your trained forecasting model.
    # --------------------------------------------------------

    forecast_demand = 439


    # ========================================================
    # CALCULATE WEEK OF YEAR
    # ========================================================

    days_before_month = sum(
        calendar.monthrange(
            forecast_year,
            month
        )[1]
        for month in range(
            1,
            forecast_month
        )
    )


    week_of_year = (
        days_before_month // 7
    ) + week_of_month


    # ========================================================
    # CALCULATE QUARTER
    # ========================================================

    quarter = (
        (forecast_month - 1) // 3
    ) + 1


    # ========================================================
    # FORECAST DEMAND RESULT
    # ========================================================

    st.markdown(
        f"""
        <div class="forecast-result">
            <div class="forecast-value">
                Forecast Demand: {forecast_demand:,} units
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # FORECAST SUMMARY
    # ========================================================

    st.subheader(
        "Forecast Summary"
    )


    summary = pd.DataFrame(
        [
            {
                "Product Name": product,
                "Forecast Year": forecast_year,
                "Month": (
                    f"{forecast_month} - "
                    f"{month_names[forecast_month - 1]}"
                ),
                "Week of Month": week_of_month,
                "Week of Year": week_of_year,
                "Quarter": f"Q{quarter}",
                "Unit Price": round(
                    unit_price,
                    2
                ),
                "Forecast Demand": forecast_demand
            }
        ]
    )


    # ========================================================
    # CENTER ALIGNMENT
    # ========================================================

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
```

