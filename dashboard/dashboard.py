import os, json
from datetime import date, timedelta

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="AQI Forecast Dashboard", layout="wide", page_icon="🌍")

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CITIES = ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Bangalore"]
AQI_BINS = [0, 50, 100, 200, 300, 400, float("inf")]
AQI_LABELS = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
AQI_COLORS = {"Good": "#00E400", "Satisfactory": "#FFFF00", "Moderate": "#FF7E00",
              "Poor": "#FF0000", "Very Poor": "#8F3F97", "Severe": "#7E0023"}

@st.cache_data
def load_results():
    path = os.path.join(DATA_DIR, "model_results.csv") if os.path.exists(os.path.join(DATA_DIR, "model_results.csv")) else os.path.join(MODEL_DIR, "model_results.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

@st.cache_data
def load_drift():
    path = os.path.join(MODEL_DIR, "drift_report.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_meta():
    path = os.path.join(MODEL_DIR, "model_meta.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_clean_features():
    path = os.path.join(DATA_DIR, "clean_features.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, parse_dates=["Date"])

st.sidebar.title("🌍 AQI Forecast")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🔮 Predict AQI", "📈 Model Performance", "⚠️ Drift Monitor", "⚙️ Settings"])

results_df = load_results()
drift = load_drift()
meta = load_meta()
clean_df = load_clean_features()

if page == "📊 Dashboard":
    st.title("Air Quality Index — Forecast Dashboard")
    st.markdown("Real-time AQI forecasting & monitoring for 5 Indian cities")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Best Model", meta["best_model"].title() if meta else "N/A", help="Model with highest R² score")
    with col2:
        if meta:
            st.metric("R² Score", f"{meta['metrics']['R2']:.4f}", help="Coefficient of determination")
        else:
            st.metric("R² Score", "N/A")
    with col3:
        if meta:
            st.metric("MAE", f"{meta['metrics']['MAE']:.2f}", help="Mean Absolute Error")
        else:
            st.metric("MAE", "N/A")
    with col4:
        if drift:
            alert_count = len(drift.get("alert_features", []))
            st.metric("Drift Alerts", alert_count, delta=f"{alert_count} active" if alert_count else "0")
        else:
            st.metric("Drift Alerts", "N/A")

    st.markdown("---")
    if clean_df is not None:
        st.subheader("Historical AQI Trends")
        city_filter = st.multiselect("Cities", CITIES, default=CITIES[:3])
        df_filtered = clean_df[clean_df["City"].isin(city_filter)]
        fig = px.line(df_filtered, x="Date", y="AQI", color="City",
                      title="Daily AQI by City", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            recent = df_filtered[df_filtered["Date"] >= df_filtered["Date"].max() - pd.Timedelta(days=90)]
            fig2 = px.box(recent, x="City", y="AQI", color="City",
                          title="AQI Distribution (Last 90 Days)", template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            latest = df_filtered.groupby("City").last().reset_index()
            latest["Category"] = pd.cut(latest["AQI"], bins=AQI_BINS, labels=AQI_LABELS)
            fig3 = px.bar(latest, x="City", y="AQI", color="Category",
                          color_discrete_map=AQI_COLORS,
                          title="Latest AQI by City", template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No historical data found. Run `preprocess.py` first.")

elif page == "🔮 Predict AQI":
    st.title("AQI Prediction")
    st.markdown("Get next-day AQI forecast for any city")

    col1, col2 = st.columns(2)
    with col1:
        city = st.selectbox("City", CITIES)
    with col2:
        forecast_date = st.date_input("Forecast Date", value=date.today() + timedelta(days=1))

    st.markdown("#### Lag Features (previous day readings)")
    col1, col2, col3 = st.columns(3)
    with col1:
        aqi_y = st.number_input("AQI Yesterday", min_value=0.0, value=150.0, step=10.0)
        aqi_3 = st.number_input("AQI 3-Day Avg", min_value=0.0, value=145.0, step=10.0)
    with col2:
        pm25_y = st.number_input("PM2.5 Yesterday", min_value=0.0, value=80.0, step=5.0)
        pm25_3 = st.number_input("PM2.5 3-Day Avg", min_value=0.0, value=75.0, step=5.0)
    with col3:
        pm10_y = st.number_input("PM10 Yesterday", min_value=0.0, value=150.0, step=10.0)
        pm10_3 = st.number_input("PM10 3-Day Avg", min_value=0.0, value=140.0, step=10.0)

    if st.button("Predict AQI", type="primary"):
        with st.spinner("Predicting..."):
            try:
                import httpx
                r = httpx.post("http://localhost:8000/predict", json={
                    "city": city,
                    "forecast_date": str(forecast_date),
                    "aqi_yesterday": aqi_y,
                    "aqi_3day_avg": aqi_3,
                    "pm25_yesterday": pm25_y,
                    "pm25_3day_avg": pm25_3,
                    "pm10_yesterday": pm10_y,
                    "pm10_3day_avg": pm10_3,
                }, timeout=10)
                r.raise_for_status()
                data = r.json()
                cat = data["aqi_category"]
                color = AQI_COLORS.get(cat, "#333")
                st.success(f"**Predicted AQI: {data['predicted_aqi']}** — *{cat}*")
                st.markdown(f"<div style='background:{color};padding:20px;border-radius:10px;text-align:center'>"
                            f"<h1 style='color:white;margin:0'>{data['predicted_aqi']}</h1>"
                            f"<p style='color:white;margin:0'>{cat}</p></div>",
                            unsafe_allow_html=True)
                st.caption(f"Model: {data['model_used']} | R²: {data['r2_score']:.4f}")
            except httpx.ConnectError:
                st.error("API not running. Start with: uvicorn src.app:app --reload")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

elif page == "📈 Model Performance":
    st.title("Model Performance Comparison")
    st.markdown("6 regression models trained with MLflow tracking")

    if results_df is not None:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(results_df.sort_values("R2"), x="model", y="R2",
                         color="R2", color_continuous_scale="viridis",
                         title="R² Score by Model", template="plotly_white")
            fig.add_hline(y=0.85, line_dash="dash", line_color="red",
                          annotation_text="Gate: 0.85")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(results_df.sort_values("MAE"), x="model", y="MAE",
                          color="MAE", color_continuous_scale="RdYlGn_r",
                          title="MAE by Model", template="plotly_white")
            fig2.add_hline(y=20, line_dash="dash", line_color="red",
                           annotation_text="Gate: 20")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Model Rankings")
        results_df["Rank"] = range(1, len(results_df) + 1)
        st.dataframe(results_df[["Rank", "model", "R2", "MAE", "RMSE"]].set_index("Rank"),
                     use_container_width=True)

        if meta:
            st.success(f"**Best Model: {meta['best_model']}** — "
                       f"R²={meta['metrics']['R2']:.4f}, MAE={meta['metrics']['MAE']:.2f}")
    else:
        st.info("Run `train.py` to generate model results.")

elif page == "⚠️ Drift Monitor":
    st.title("Data Drift Monitor")
    st.markdown("Population Stability Index (PSI) monitoring for feature drift")

    if drift:
        features = list(drift.get("feature_drift", {}).keys())
        psi_vals = [drift["feature_drift"][f]["PSI"] for f in features]
        statuses = [drift["feature_drift"][f]["status"] for f in features]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records Analyzed", drift.get("n_recent_records", 0))
        with col2:
            st.metric("Window (Days)", drift.get("recent_window_days", 30))
        with col3:
            retrain = drift.get("retraining_needed", False)
            st.metric("Retraining Needed", "⚠️ Yes" if retrain else "✅ No",
                      delta_color="off")

        status_colors = {"OK": "green", "WARNING": "orange", "ALERT": "red"}
        bar_colors = [status_colors[s] for s in statuses]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=features, y=psi_vals, marker_color=bar_colors,
                             text=[f"{v:.4f}" for v in psi_vals], textposition="outside"))
        fig.add_hline(y=0.1, line_dash="dash", line_color="orange",
                      annotation_text="WARN (0.1)")
        fig.add_hline(y=0.2, line_dash="dash", line_color="red",
                      annotation_text="ALERT (0.2)")
        fig.update_layout(title="Feature Drift (PSI)", template="plotly_white",
                          yaxis_title="PSI")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Drift Report Summary")
        for feat, info in drift["feature_drift"].items():
            emoji = {"OK": "✅", "WARNING": "⚠️", "ALERT": "🚨"}
            st.markdown(f"{emoji[info['status']]} **{feat}** — PSI: `{info['PSI']}` ({info['status']})")

        if drift.get("alert_features"):
            st.error(f"🚨 Drift alert on: {', '.join(drift['alert_features'])}. "
                     "Retraining pipeline should be triggered.")
    else:
        st.info("No drift report found. Run `monitor.py` first.")

else:
    st.title("⚙️ Settings & Pipeline Info")
    st.markdown("### Project Structure")
    st.code("""
AQI_Forecast/
├── src/            # Core pipeline (preprocess, train, monitor, app)
├── dashboard/      # Streamlit dashboard
├── config/         # Docker, DVC, CI/CD config
├── models/         # Trained artifacts
├── data/           # Raw & processed data
└── reports/        # Technical documents
    """)

    st.markdown("### Pipeline Commands")
    st.code("""
# Preprocess data
python src/preprocess.py

# Train models
python src/train.py

# Run API
uvicorn src.app:app --reload --port 8000

# Run dashboard
streamlit run dashboard/dashboard.py

# Check drift
python src/monitor.py

# Run tests
pytest src/test_pipeline.py -v

# Docker: all services
docker-compose up --build
    """)

    st.markdown("### API Endpoints")
    st.markdown("| Endpoint | Method | Description |")
    st.markdown("|---|---|---|")
    st.markdown("| `/health` | GET | API health check |")
    st.markdown("| `/model-info` | GET | Model metadata |")
    st.markdown("| `/predict` | POST | Next-day AQI forecast |")
    st.markdown("| `/cities` | GET | Supported cities |")
