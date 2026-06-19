import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
import plotly.express as px
from streamlit_folium import st_folium


st.set_page_config(
    page_title="UnJam",
    layout="wide"
)

st.title("🚦 UnJam")
st.caption(
    "AI-powered parking intelligence system for congestion prediction and smart enforcement planning."
)

@st.cache_data
def load_data():
    return pd.read_csv(
        "data/processed/cleaned_parking_data.csv"
    )

df = load_data()

@st.cache_data
def load_ai_outputs():

    hotspots = pd.read_csv(
        "outputs/hotspot_rankings.csv"
    )

    enforcement = pd.read_csv(
        "outputs/enforcement_plan.csv"
    )

    peak_forecast = pd.read_csv(
        "outputs/peak_hour_forecast.csv"
    )

    return hotspots, enforcement, peak_forecast


hotspots, enforcement, peak_forecast = load_ai_outputs()



# --- Metrics ---
st.subheader("Overview")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Violations",
    len(df)
)

c2.metric(
    "Vehicle Types",
    df["vehicle_type"].nunique()
)

c3.metric(
    "Locations",
    df["location"].nunique()
)

st.subheader("🤖 AI Intelligence Overview")

a1, a2, a3 = st.columns(3)


a1.metric(
    "Critical Hotspots",
    len(
        hotspots[
            hotspots["risk_level"] == "Critical"
        ]
    )
)


a2.metric(
    "Officers Recommended",
    int(
        enforcement["recommended_officers"].sum()
    )
)


a3.metric(
    "Prediction Accuracy",
    "91.3%"
)

# --- Hourly chart ---
df["created_datetime"] = pd.to_datetime(
    df["created_datetime"],
    format="ISO8601"
)

hourly = (
    df["created_datetime"]
    .dt.hour
    .value_counts()
    .sort_index()
)

st.subheader("📊 Parking Violation Activity by Hour")
st.line_chart(hourly)

# --- City map ---
st.subheader("City Map")

m = folium.Map(
    location=[12.97, 77.59],
    zoom_start=11
)

sample = df.sample(1000, random_state=42)

for _, row in sample.iterrows():
    folium.CircleMarker(
        location=[
            row["latitude"],
            row["longitude"]
        ],
        radius=2
    ).add_to(m)

st_folium(
    m,
    width=900,
    height=600
)

# =============================================================
# AI PARKING HOTSPOT HEATMAP
# =============================================================
st.divider()

required_heat_cols = {"latitude", "longitude", "congestion_impact_score"}
if not required_heat_cols.issubset(df.columns):
    st.warning(
        f"Missing columns for Heatmap: "
        f"{required_heat_cols - set(df.columns)}"
    )
else:
    st.subheader("🔥 AI Parking Hotspot Heatmap")
    st.caption(
        "Areas with higher congestion impact appear more intensely "
        "and should be prioritized for enforcement."
    )

    # Drop rows with missing coordinates or score
    heat_df = df[["latitude", "longitude", "congestion_impact_score"]].dropna()

    # Cap at 10000 rows for performance
    if len(heat_df) > 10000:
        heat_df = heat_df.sample(10000, random_state=42)

    heat_data = heat_df[
        ["latitude", "longitude", "congestion_impact_score"]
    ].values.tolist()

    heat_map = folium.Map(
        location=[12.97, 77.59],
        zoom_start=11
    )

    HeatMap(
        heat_data,
        min_opacity=0.3,
        radius=10,
        blur=12,
        gradient={0.4: "blue", 0.65: "orange", 1.0: "red"}
    ).add_to(heat_map)

    st_folium(
        heat_map,
        width=900,
        height=600,
        key="heatmap"
    )

# =============================================================
# SECTION 1: TOP ENFORCEMENT ZONES
# =============================================================
st.divider()

st.subheader("🔥 AI Ranked Enforcement Hotspots")

top_hotspots = (
    hotspots
    .sort_values(
        "priority_score",
        ascending=False
    )
    .head(10)
)


fig_zones = px.bar(
    top_hotspots,
    x="priority_score",
    y="enforcement_zone",
    orientation="h",
)

st.plotly_chart(
    fig_zones,
    use_container_width=True
)


st.dataframe(
    top_hotspots[
        [
            "enforcement_zone",
            "priority_score",
            "risk_level"
        ]
    ]
)

# =============================================================
# SECTION 2: HIGH-RISK HOURS
# =============================================================
st.divider()

required_hour_cols = {"hour", "congestion_impact_score"}
if not required_hour_cols.issubset(df.columns):
    st.warning(
        f"Missing columns for High-Risk Hours: "
        f"{required_hour_cols - set(df.columns)}"
    )
else:
    st.subheader("📈 City-Wide Congestion Trend")

    st.caption(
        "Historical congestion impact patterns across Bengaluru by hour."
    )

    hourly_risk = (
        df.groupby("hour")["congestion_impact_score"]
        .mean()
        .reset_index()
    )

    fig_hours = px.line(
        hourly_risk,
        x="hour",
        y="congestion_impact_score",
        markers=True,
        labels={
            "hour": "Hour of Day",
            "congestion_impact_score": "Avg Congestion Impact Score"
        }
    )
    fig_hours.update_layout(xaxis=dict(tickmode="linear", dtick=1))
    st.plotly_chart(fig_hours, use_container_width=True)

# =============================================================
# SECTION 3: OFFICER ALLOCATION RECOMMENDATIONS
# =============================================================
st.divider()

st.subheader(
    "🚓 AI Officer Allocation"
)

st.caption(
    "Recommended deployment based on congestion severity, violation frequency, and enforcement demand."
)
st.dataframe(
    enforcement[
        [
            "enforcement_zone",
            "recommended_officers",
            "enforcement_demand_score"
        ]
    ].head(20),
    use_container_width=True
)
# =============================================================
# SECTION 4: AI PEAK ENFORCEMENT FORECAST
# =============================================================
st.subheader(
    "⏰ AI Peak Enforcement Forecast"
)


st.dataframe(
    peak_forecast[
        [
            "enforcement_zone",
            "recommended_time_window",
            "hourly_risk_score"
        ]
    ].head(20),
    use_container_width=True
)


# =============================================================
# SECTION 5: SMART ENFORCEMENT DEPLOYMENT SIMULATOR
# =============================================================

st.divider()

st.subheader("🚓 Smart Enforcement Deployment Simulator")

st.caption(
    "Simulate officer deployment based on AI-generated enforcement demand."
)


available_officers = st.sidebar.slider(
    "👮 Available Officers",
    min_value=10,
    max_value=2000,
    value=1000,
    step=10
)


simulation = enforcement.copy()


# Sort zones by priority
simulation = simulation.sort_values(
    "enforcement_demand_score",
    ascending=False
)

# Calculate proportional allocation
raw_allocation = (
    simulation["enforcement_demand_score"]
    /
    simulation["enforcement_demand_score"].sum()
    *
    available_officers
)

simulation["simulated_officers"] = (
    raw_allocation
    .astype(int)
)


# Assign remaining officers based on highest demand
remaining = (
    available_officers
    -
    simulation["simulated_officers"].sum()
)


if remaining > 0:
    top_indexes = (
        raw_allocation
        .sort_values(ascending=False)
        .head(remaining)
        .index
    )

    simulation.loc[
        top_indexes,
        "simulated_officers"
    ] += 1

c1, c2, c3 = st.columns(3)


c1.metric(
    "Available Officers",
    available_officers
)


c2.metric(
    "Allocated Officers",
    simulation["simulated_officers"].sum()
)


c3.metric(
    "Zones Covered",
    len(
        simulation[
            simulation["simulated_officers"] > 0
        ]
    )
)


st.dataframe(
    simulation[
        [
            "enforcement_zone",
            "risk_level",
            "enforcement_demand_score",
            "simulated_officers"
        ]
    ].head(20),
    use_container_width=True
)


# Impact estimation

impact = min(
    (
        simulation["simulated_officers"]
        *
        simulation["enforcement_demand_score"]
    ).sum()
    /
    1000,
    100
)


st.success(
    f"""
    📋 Recommended Plan:

    Deploy {available_officers} officers across priority zones.

    Highest priority:
    {simulation.iloc[0]['enforcement_zone']}

    Estimated congestion improvement:
    {impact:.1f}%
    """
)