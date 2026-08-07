
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="FORESIGHT Inventory Intelligence",
    layout="wide"
)

st.title(
    "NorthBay Living - Demand & Inventory Intelligence"
)

inventory = pd.read_csv(
    "foresight/data/inventory_risk_report.csv"
)

# KPI SECTION

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total SKUs",
    inventory["StockCode"].nunique()
)

col2.metric(
    "Stockout Risk",
    (inventory["Risk_Status"] == "Stockout Risk").sum()
)

col3.metric(
    "Overstock",
    (inventory["Risk_Status"] == "Overstock").sum()
)

col4.metric(
    "Sales At Risk",
    round(
        inventory["Sales_At_Risk"].sum(),
        2
    )
)

st.divider()

# SKU FILTER

sku = st.selectbox(
    "Select Product",
    inventory["Description"].unique()
)

selected = inventory[
    inventory["Description"] == sku
]

st.subheader(
    "Inventory Decision"
)

st.dataframe(selected)

# RISK GRAPH

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
    title="Inventory Risk Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ACTION TABLES

st.subheader(
    "Priority Reorder List"
)

st.dataframe(
    inventory[
        inventory["Risk_Status"] == "Stockout Risk"
    ][
        [
            "StockCode",
            "Description",
            "Recommended_Order_Qty"
        ]
    ]
)

st.subheader(
    "Markdown Clearance List"
)

st.dataframe(
    inventory[
        inventory["Risk_Status"] == "Overstock"
    ][
        [
            "StockCode",
            "Description",
            "Capital_Locked"
        ]
    ]
)
