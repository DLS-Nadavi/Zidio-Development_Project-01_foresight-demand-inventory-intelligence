import streamlit as st
import pandas as pd
import calendar

st.set_page_config(
    page_title="Demand Forecast Simulator",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Demand Forecast Simulator")

# -----------------------------
# Product
# -----------------------------
product = st.selectbox(
    "Forecast Product",
    ["10 COLOUR SPACEBOY PEN"]
)

st.caption("Available sales history: 2 weeks")


# -----------------------------
# Forecast Year
# -----------------------------
forecast_year = st.number_input(
    "Forecast Year",
    min_value=2020,
    max_value=2100,
    value=2030,
    step=1
)


# -----------------------------
# Forecast Month
# -----------------------------
month_names = list(calendar.month_name)[1:]

forecast_month = st.selectbox(
    "Forecast Month",
    options=range(1, 13),
    format_func=lambda x: f"{x} - {month_names[x - 1]}",
    index=3
)


# -----------------------------
# Week of Month
# -----------------------------
week_of_month = st.selectbox(
    "Week of Month",
    [1, 2, 3, 4, 5],
    index=2
)


# -----------------------------
# Unit Price
# -----------------------------
unit_price = st.number_input(
    "Unit Price",
    min_value=0.0,
    value=1.55,
    step=0.01,
    format="%.2f"
)


# -----------------------------
# Generate Forecast
# -----------------------------
st.markdown("---")

if st.button(
    "🚀 Generate Forecast",
    type="primary",
    use_container_width=True
):

    # Temporary forecast
    # Replace this with your actual model later
    forecast_demand = 439

    # Calculate week of year
    days_before_month = sum(
        calendar.monthrange(forecast_year, m)[1]
        for m in range(1, forecast_month)
    )

    week_of_year = (
        days_before_month // 7
    ) + week_of_month

    # Calculate quarter
    quarter = ((forecast_month - 1) // 3) + 1

    # Display result
    st.success(
        f"Forecast Demand: {forecast_demand} units"
    )

    # -----------------------------
    # Forecast Summary
    # -----------------------------
    summary = pd.DataFrame([{
        "Product Name": product,
        "Forecast Year": forecast_year,
        "Month": f"{forecast_month} - {month_names[forecast_month - 1]}",
        "Week of Month": week_of_month,
        "Week of Year": week_of_year,
        "Quarter": quarter,
        "Unit Price": round(unit_price, 2),
        "Forecast Demand": forecast_demand
    }])

    st.subheader("📊 Forecast Summary")

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )
