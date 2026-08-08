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
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR.parent / "data" / "inventory_risk_report.csv"


# ============================================================
# LOAD INVENTORY DATA
# ============================================================

inventory = None

if DATA_FILE.exists():

    try:

        inventory = pd.read_csv(DATA_FILE)

    except Exception as e:

        st.warning(
            f"Inventory file could not be loaded: {e}"
        )

else:

    st.warning(
        "Inventory data file was not found."
    )

    st.info(
        f"Expected file location: {DATA_FILE}"
    )


# ============================================================
# TABS
# ============================================================

forecast_tab, inventory_tab = st.tabs(
    [
        "📈 Demand Forecast Simulator",
        "📦 Inventory Intelligence"
    ]
)


# ============================================================
# DEMAND FORECAST TAB
# ============================================================

with forecast_tab:

    st.header("📈 Demand Forecast Simulator")

    st.write(
        "Enter the forecasting parameters below."
    )

    st.divider()

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    product = st.selectbox(
        "Forecast Product",
        [
            "10 COLOUR SPACEBOY PEN"
        ]
    )

    st.caption(
        "Available sales history: 2 weeks"
    )

    # --------------------------------------------------------
    # FORECAST YEAR
    # --------------------------------------------------------

    forecast_year = st.number_input(
        "Forecast Year",
        min_value=2020,
        max_value=2100,
        value=2030,
        step=1
    )

    # --------------------------------------------------------
    # FORECAST MONTH
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
    # WEEK OF MONTH
    # --------------------------------------------------------

    week_of_month = st.selectbox(
        "Week of Month",
        [1, 2, 3, 4, 5],
        index=2
    )

    # --------------------------------------------------------
    # UNIT PRICE
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
    # FORECAST BUTTON
    # --------------------------------------------------------

    generate_forecast = st.button(
        "🚀 Generate Forecast",
        type="primary",
        use_container_width=True
    )

    if generate_forecast:

        # ----------------------------------------------------
        # TEMPORARY FORECAST
        # ----------------------------------------------------
        # Replace this with your trained ML model.
        # ----------------------------------------------------

        forecast_demand = 439

        # ----------------------------------------------------
        # WEEK OF YEAR
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # QUARTER
        # ----------------------------------------------------

        quarter = (
            (forecast_month - 1) // 3
        ) + 1

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        st.success(
            f"Forecast Demand: {forecast_demand:,} units"
        )

        st.subheader(
            "📊 Forecast KPIs"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Forecast Demand",
                f"{forecast_demand:,} units"
            )

        with col2:

            st.metric(
                "Unit Price",
                f"{unit_price:.2f}"
            )

        with col3:

            st.metric(
                "Week of Year",
                week_of_year
            )

        with col4:

            st.metric(
                "Quarter",
                f"Q{quarter}"
            )

        # ----------------------------------------------------
        # FORECAST SUMMARY
        # ----------------------------------------------------

        st.subheader(
            "📋 Forecast Summary"
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
        "📦 Inventory Intelligence"
    )

    # --------------------------------------------------------
    # CHECK DATA
    # --------------------------------------------------------

    if inventory is None:

        st.error(
            "Inventory data is unavailable."
        )

        st.info(
            "Please place inventory_risk_report.csv inside "
            "the project's data folder."
        )

    else:

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
                "The inventory CSV is missing these columns:"
            )

            st.write(
                missing_columns
            )

        else:

            # ------------------------------------------------
            # CLEAN DATA
            # ------------------------------------------------

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

            # ------------------------------------------------
            # KPI SECTION
            # ------------------------------------------------

            col1, col2, col3, col4 = st.columns(4)

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

            with col1:

                st.metric(
                    "Total SKUs",
                    f"{total_skus:,}"
                )

            with col2:

                st.metric(
                    "Stockout Risk",
                    f"{stockout_risk:,}"
                )

            with col3:

                st.metric(
                    "Overstock",
                    f"{overstock:,}"
                )

            with col4:

                st.metric(
                    "Sales At Risk",
                    f"{sales_at_risk:,.2f}"
                )

            st.divider()

            # ------------------------------------------------
            # PRODUCT SELECTOR
            # ------------------------------------------------

            st.subheader(
                "🔎 Product Analysis"
            )

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

                st.subheader(
                    "📦 Inventory Decision"
                )

                st.dataframe(
                    selected,
                    use_container_width=True,
                    hide_index=True
                )

            # ------------------------------------------------
            # RISK GRAPH
            # ------------------------------------------------

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

            # ------------------------------------------------
            # PRIORITY REORDER LIST
            # ------------------------------------------------

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

            if not reorder_list.empty:

                st.dataframe(
                    reorder_list,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No products currently require "
                    "urgent reordering."
                )

            # ------------------------------------------------
            # MARKDOWN CLEARANCE LIST
            # ------------------------------------------------

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

            if not clearance_list.empty:

                st.dataframe(
                    clearance_list,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No products are currently classified "
                    "as overstock."
                )
