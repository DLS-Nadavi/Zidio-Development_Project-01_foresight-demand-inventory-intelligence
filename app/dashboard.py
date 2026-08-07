"""
FORESIGHT Streamlit Dashboard
NorthBay Living - Demand & Inventory Intelligence

Runs the full clean -> forecast -> risk-engine pipeline live from an
uploaded transaction CSV, so the app works standalone on Streamlit
Cloud without needing pre-generated model/report files.
"""

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core

st.set_page_config(page_title="FORESIGHT Inventory Intelligence", layout="wide")
st.title("NorthBay Living — Demand & Inventory Intelligence")
st.caption("Upload a transaction export (Invoice, StockCode, Description, Quantity, Price, InvoiceDate, ...) to generate a live demand forecast and inventory risk report.")

with st.sidebar:
    st.header("Data Source")
    uploaded_file = st.file_uploader("Transaction CSV", type=["csv"])
    use_sample_path = st.text_input(
        "...or a server-side file path",
        value="",
        placeholder="/path/to/dataset.csv",
    )
    run_button = st.button("Run Pipeline", type="primary")

if "results" not in st.session_state:
    st.session_state["results"] = None


@st.cache_data(show_spinner=False)
def load_raw(file_bytes_or_path, is_path: bool):
    if is_path:
        return pd.read_csv(file_bytes_or_path, encoding="latin1")
    return pd.read_csv(file_bytes_or_path, encoding="latin1")


@st.cache_resource(show_spinner="Running pipeline (clean -> forecast -> risk engine)...")
def run_pipeline_cached(raw_df):
    return core.run_full_pipeline(raw_df)


if run_button:
    if uploaded_file is not None:
        raw_df = load_raw(uploaded_file, is_path=False)
    elif use_sample_path:
        raw_df = load_raw(use_sample_path, is_path=True)
    else:
        st.warning("Upload a CSV or provide a file path first.")
        raw_df = None

    if raw_df is not None:
        st.session_state["results"] = run_pipeline_cached(raw_df)

results = st.session_state["results"]

if results is None:
    st.info("Upload data and click **Run Pipeline** to generate the dashboard.")
    st.stop()

inventory = results["inventory"]
comparison = results["comparison"]

# KPI section
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total SKUs", inventory["StockCode"].nunique())
col2.metric("Stockout Risk", int((inventory["Risk_Status"] == "Stockout Risk").sum()))
col3.metric("Overstock", int((inventory["Risk_Status"] == "Overstock").sum()))
col4.metric("Sales At Risk", f"{inventory['Sales_At_Risk'].sum():,.2f}")

st.divider()

st.subheader("Forecast Model Performance")
st.dataframe(comparison, use_container_width=True)

st.subheader("Inventory Decision")
sku = st.selectbox("Select Product", inventory["Description"].unique())
selected = inventory[inventory["Description"] == sku]
st.dataframe(selected, use_container_width=True)

risk = inventory["Risk_Status"].value_counts().reset_index()
risk.columns = ["Risk", "Count"]
fig = px.bar(risk, x="Risk", y="Count", title="Inventory Risk Distribution")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.scatter(
    inventory, x="Stockout_Score", y="Overstock_Score",
    hover_data=["StockCode", "Description"],
    title="Inventory Decision Grid",
)
fig2.add_vline(x=1, line_dash="dash")
fig2.add_hline(y=3, line_dash="dash")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Priority Reorder List")
st.dataframe(
    inventory[inventory["Risk_Status"] == "Stockout Risk"][
        ["StockCode", "Description", "Recommended_Order_Qty"]
    ],
    use_container_width=True,
)

st.subheader("Markdown Clearance List")
st.dataframe(
    inventory[inventory["Risk_Status"] == "Overstock"][
        ["StockCode", "Description", "Capital_Locked"]
    ],
    use_container_width=True,
)

st.download_button(
    "Download Inventory Risk Report (CSV)",
    inventory.to_csv(index=False).encode("utf-8"),
    file_name="inventory_risk_report.csv",
    mime="text/csv",
)
