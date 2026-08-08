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
# FILE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INVENTORY_FILE = (
    BASE_DIR.parent
    / "data"
    / "inventory_risk_report.csv"
)

# Change this filename if your sales-history file
# has a different name.
SALES_FILE = (
    BASE_DIR.parent
    / "data"
    / "sales_history.csv"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       MAIN PAGE
       -------------------------------------------------------- */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* --------------------------------------------------------
       KPI CARDS
       -------------------------------------------------------- */

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


    /* --------------------------------------------------------
       FORECAST RESULT
       -------------------------------------------------------- */

    .forecast-result {
        background-color: #d9f5df;
        border: 1px solid #a7dfb2;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: left;
    }

    .forecast-value {
        font-size: 25px;
        font-weight: 700;
        color: #245c32;
    }


    /* --------------------------------------------------------
       FORECAST BUTTON
       -------------------------------------------------------- */

    div.stButton > button {
        background-color: white;
        color: #1f2937;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 20px;
        width: auto;
    }

    div.stButton > button:hover {
        background-color: #f8fafc;
        color: #1f2937;
        border: 1px solid #9ca3af;
    }


    /* --------------------------------------------------------
       AVAILABILITY INDICATORS
       -------------------------------------------------------- */

    .availability-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .availability-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        font-weight: 700;
        line-height: 20px;
    }

    .available-box {
        background-color: #22c55e;
    }

    .unavailable-box {
        background-color: #ef4444;
    }

    .availability-text {
        font-size: 14px;
        color: #475569;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD INVENTORY DATA
# ============================================================

inventory = None

if INVENTORY_FILE.exists():

    try:

        inventory = pd.read_csv(
            INVENTORY_FILE
        )

    except Exception as e:

        st.error(
            f"Unable to load inventory data: {e}"
        )

else:

    st.warning(
        "Inventory data file was not found."
    )

    st.info(
        f"Expected file location: {INVENTORY_FILE}"
    )


# ============================================================
# LOAD SALES HISTORY
# ============================================================

sales = None

if SALES_FILE.exists():

    try:

        sales = pd.read_csv(
            SALES_FILE
        )

    except Exception as e:

        st.warning(
            f"Unable to load sales history: {e}"
        )

else:

    st.warning(
        "Sales history file was not found."
    )

    st.info(
        f"Expected file location: {SALES_FILE}"
    )


# ============================================================
# INVENTORY DATA VALIDATION
# ============================================================

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

        # Clean inventory columns

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


# ============================================================
# SALES HISTORY FUNCTIONS
# ============================================================

def find_column(dataframe, possible_names):

    """
    Find a column using several possible column names.
    """

    for name in possible_names:

        if name in dataframe.columns:
            return name

    # Try case-insensitive matching

    lower_columns = {
        str(column).lower(): column
        for column in dataframe.columns
    }

    for name in possible_names:

        if name.lower() in lower_columns:

            return lower_columns[name.lower()]

    return None


def calculate_product_weeks(
    sales_data,
    product_name
):

    """
    Calculate the number of unique weeks with sales
    for a product.
    """

    if sales_data is None:
        return 0

    if sales_data.empty:
        return 0

    # --------------------------------------------------------
    # Find product column
    # --------------------------------------------------------

    product_column = find_column(
        sales_data,
        [
            "Description",
            "Product",
            "Product_Name",
            "Product Name",
            "StockCode",
            "Stock Code"
        ]
    )

    # --------------------------------------------------------
    # Find date column
    # --------------------------------------------------------

    date_column = find_column(
        sales_data,
        [
            "InvoiceDate",
            "Invoice Date",
            "Date",
            "OrderDate",
            "Order Date",
            "TransactionDate",
            "Transaction Date"
        ]
    )

    if product_column is None:
        return 0

    if date_column is None:
        return 0

    # --------------------------------------------------------
    # Filter product
    # --------------------------------------------------------

    product_sales = sales_data[
        sales_data[product_column]
        .astype(str)
        .str.strip()
        .str.upper()
        ==
        str(product_name)
        .strip()
        .upper()
    ].copy()

    if product_sales.empty:
        return 0

    # --------------------------------------------------------
    # Convert date
    # --------------------------------------------------------

    product_sales[date_column] = pd.to_datetime(
        product_sales[date_column],
        errors="coerce"
    )

    product_sales = product_sales.dropna(
        subset=[date_column]
    )

    if product_sales.empty:
        return 0

    # --------------------------------------------------------
    # Count unique weeks
    # --------------------------------------------------------

    weeks_available = (
        product_sales[date_column]
        .dt.to_period("W")
        .nunique()
    )

    return int(weeks_available)


# ============================================================
# GET FORECAST PRODUCTS
# ============================================================

forecast_products = []

if inventory_valid:

    forecast_products = (
        inventory["Description"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

elif sales is not None:

    product_column = find_column(
        sales,
        [
            "Description",
            "Product",
            "Product_Name",
            "Product Name",
            "StockCode",
            "Stock Code"
        ]
    )

    if product_column is not None:

        forecast_products = (
            sales[product_column]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )


# ============================================================
# 1. KPI VALUES
# ============================================================

st.header("KPI Values")

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
                <div class="kpi-title">
                    Total SKUs
                </div>

                <div class="kpi-value">
                    {total_skus:,}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    Stockout Risk
                </div>

                <div class="kpi-value">
                    {stockout_risk:,}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    Overstock
                </div>

                <div class="kpi-value">
                    {overstock:,}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    Sales At Risk
                </div>

                <div class="kpi-value">
                    {sales_at_risk:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:

    st.info(
        "Inventory KPIs will appear when inventory data is available."
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
# 6. DEMAND FORECAST SIMULATOR
# ============================================================

st.header("Demand Forecast Simulator")

st.write(
    "Enter the forecast parameters and generate the expected demand."
)


# ============================================================
# FORECAST PRODUCT
# ============================================================

if forecast_products:

    # --------------------------------------------------------
    # Create labels with availability
    # --------------------------------------------------------

    product_labels = {}

    for product_name in forecast_products:

        weeks = calculate_product_weeks(
            sales,
            product_name
        )

        if weeks > 0:

            label = (
                f"{product_name} - "
                f"✓ Available ({weeks} weeks)"
            )

        else:

            label = (
                f"{product_name} - "
                f"✕ Not Available (0 weeks)"
            )

        product_labels[label] = product_name


    # --------------------------------------------------------
    # Product dropdown
    # --------------------------------------------------------

    selected_product_label = st.selectbox(
        "Forecast Product",
        list(product_labels.keys()),
        key="forecast_product"
    )

    product = product_labels[
        selected_product_label
    ]


    # --------------------------------------------------------
    # Availability indicator
    # --------------------------------------------------------

    selected_weeks = calculate_product_weeks(
        sales,
        product
    )

    if selected_weeks > 0:

        st.markdown(
            f"""
            <div class="availability-row">

                <span class="availability-box available-box">
                    ✓
                </span>

                <span class="availability-text">
                    Available ({selected_weeks} weeks)
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="availability-row">

                <span class="availability-box unavailable-box">
                    ✕
                </span>

                <span class="availability-text">
                    Not Available (0 weeks)
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

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
    step=1
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
    index=3
)


# ============================================================
# WEEK OF MONTH
# ============================================================

week_of_month = st.selectbox(
    "Week of Month",
    [1, 2, 3, 4, 5],
    index=2
)


# ============================================================
# UNIT PRICE
# ============================================================

unit_price = st.number_input(
    "Unit Price",
    min_value=0.0,
    value=1.55,
    step=0.01,
    format="%.2f"
)


st.write("")


# ============================================================
# FORECAST BUTTON
# ============================================================

generate_forecast = st.button(
    "Generate Forecast"
)


# ============================================================
# FORECAST RESULT
# ============================================================

if generate_forecast and product is not None:

    # --------------------------------------------------------
    # TEMPORARY FORECAST VALUE
    # --------------------------------------------------------
    # Replace this with your actual forecasting model.
    # --------------------------------------------------------

    forecast_demand = 439


    # --------------------------------------------------------
    # CALCULATE WEEK OF YEAR
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # CALCULATE QUARTER
    # --------------------------------------------------------

    quarter = (
        (forecast_month - 1) // 3
    ) + 1


    # --------------------------------------------------------
    # FORECAST DEMAND
    # --------------------------------------------------------

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
                "Month": month_names[
                    forecast_month - 1
                ],
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

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )
