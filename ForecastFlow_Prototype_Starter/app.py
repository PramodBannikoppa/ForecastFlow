import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="ForecastFlow | Dharwad", page_icon="💧", layout="wide")

DATA_FILE = Path(__file__).parent / "ForecastFlow_Dharwad_Updated_Monthly_Merged.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["Month_Start", "Target_Month_Start"])
    df = df.sort_values("Month_Start")
    for col in ["GW_Level_Mean", "Rainfall_District_Mean_mm"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

st.title("💧 ForecastFlow")
st.subheader("Dharwad groundwater forecasting and depletion-risk prototype")
st.info(
    "Prototype status: the dashboard and baseline demonstration are operational components, "
    "not a validated groundwater-risk service. The current rainfall record has gaps, and the "
    "available training sample is small. Forecasts below are persistence baselines, not LUBE predictions."
)

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

required = {"Month_Start", "GW_Level_Mean"}
if not required.issubset(df.columns):
    st.error(f"Dataset is missing required columns: {sorted(required - set(df.columns))}")
    st.stop()

gw = df.dropna(subset=["Month_Start", "GW_Level_Mean"]).copy()
rain = df.dropna(subset=["Month_Start", "Rainfall_District_Mean_mm"]).copy() if "Rainfall_District_Mean_mm" in df else pd.DataFrame()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Groundwater months", f"{len(gw)}")
c2.metric("First month", gw["Month_Start"].min().strftime("%b %Y") if len(gw) else "—")
c3.metric("Last month", gw["Month_Start"].max().strftime("%b %Y") if len(gw) else "—")
c4.metric("Months with usable rainfall", f"{len(rain)}")

st.markdown("### 1. Historical groundwater levels")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=gw["Month_Start"], y=gw["GW_Level_Mean"], mode="lines+markers",
    name="Monthly mean groundwater level"
))
fig.update_layout(
    xaxis_title="Month", yaxis_title="Groundwater level (source units; verify units)",
    hovermode="x unified", margin=dict(l=20, r=20, t=25, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 2. Monthly rainfall coverage")
if not rain.empty:
    rfig = go.Figure()
    rfig.add_trace(go.Bar(
        x=rain["Month_Start"], y=rain["Rainfall_District_Mean_mm"],
        name="Rainfall monthly mean across qualifying stations (mm)"
    ))
    rfig.update_layout(
        xaxis_title="Month", yaxis_title="Rainfall (mm)",
        hovermode="x unified", margin=dict(l=20, r=20, t=25, b=20)
    )
    st.plotly_chart(rfig, use_container_width=True)
else:
    st.warning("No usable rainfall values were found in the merged dataset.")

if "Rainfall_Month_Complete" in df.columns:
    complete_count = int(df["Rainfall_Month_Complete"].fillna(False).astype(bool).sum())
    st.caption(f"Months passing the current rainfall completeness rule: {complete_count}. Missing rainfall is not treated as zero.")

st.markdown("### 3. Baseline forecast demonstration")
horizon = st.selectbox("Forecast horizon", [1, 2, 3], index=0, format_func=lambda n: f"{n} month(s) ahead")
if gw.empty:
    st.warning("No groundwater history is available for forecasting.")
else:
    last_date = gw["Month_Start"].max()
    last_level = float(gw.iloc[-1]["GW_Level_Mean"])
    future_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    forecast = pd.DataFrame({"Month_Start": future_dates, "Baseline_GW_Level": [last_level] * horizon})
    ffig = go.Figure()
    ffig.add_trace(go.Scatter(x=gw["Month_Start"], y=gw["GW_Level_Mean"], mode="lines+markers", name="Observed monthly mean"))
    ffig.add_trace(go.Scatter(x=forecast["Month_Start"], y=forecast["Baseline_GW_Level"], mode="lines+markers", line=dict(dash="dash"), name="Persistence baseline (demo)"))
    ffig.update_layout(
        xaxis_title="Month", yaxis_title="Groundwater level (source units; verify units)",
        hovermode="x unified", margin=dict(l=20, r=20, t=25, b=20)
    )
    st.plotly_chart(ffig, use_container_width=True)
    st.dataframe(forecast, use_container_width=True, hide_index=True)
    st.warning(
        "This flat line is a persistence benchmark only. It does not model rainfall effects, "
        "uncertainty, or depletion probability. Do not present it as a validated future prediction."
    )

with st.expander("Data quality and next research steps"):
    st.write("- Verify groundwater-level units and the measurement sign convention from the source.")
    st.write("- Rainfall is only usable where the source records meet the completeness rule; other months remain missing.")
    st.write("- Expand historical rainfall coverage and check station representativeness.")
    st.write("- Evaluate models with chronological/rolling-origin validation, never random month shuffling.")
    st.write("- Add LUBE or quantile regression only after there are enough valid observations to assess interval coverage.")
    st.write("- Define a groundwater risk threshold from an authoritative source before displaying risk alerts.")

st.markdown("---")
st.caption("ForecastFlow research prototype • Dharwad district • Results require validation before operational use.")
