# Project FORESIGHT
### NorthBay Living — Demand & Inventory Intelligence

## Structure
foresight/
- core.py — shared cleaning/forecasting/risk-engine functions
- app/dashboard.py — Streamlit dashboard (upload a CSV, click Run Pipeline)
- service/api.py — FastAPI scoring endpoint
- scripts/pipeline.py — batch script that trains the model and writes CSV/model artifacts

## Run the dashboard
pip install -r requirements.txt
streamlit run app/dashboard.py

## Run the batch pipeline
python scripts/pipeline.py

## Run the API
uvicorn service.api:app --reload

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub.
2. Go to share.streamlit.io -> New app.
3. Select the repo, branch main, main file path app/dashboard.py.
4. Deploy.
