import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import st_folium

st.set_page_config(
    page_title="UnJam",
    layout="wide"
)

st.title("🚦 UnJam")

@st.cache_data
def load_data():
    return pd.read_csv(
        "data/processed/cleaned_parking_data.csv"
    )

df = load_data()

st.write(df.head())

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

st.subheader("Violations by Hour")
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
# SECTION 1: TOP ENFORCEMENT ZONES
# =============================================================
st.divider()

required_zone_cols = {"enforcement_zone", "congestion_impact_score"}
if not required_zone_cols.issubset(df.columns):
    st.warning(
        f"Missing columns for Top Enforcement Zones: "
        f"{required_zone_cols - set(df.columns)}"
    )
else:
    st.subheader("Top Enforcement Zones")
    st.caption(
        "These locations generate the highest estimated traffic disruption "
        "and should be prioritized for enforcement."
    )

    top_zones = (
        df.groupby("enforcement_zone")["congestion_impact_score"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_zones = px.bar(
        top_zones,
        x="congestion_impact_score",
        y="enforcement_zone",
        orientation="h",
        labels={
            "congestion_impact_score": "Avg Congestion Impact Score",
            "enforcement_zone": "Enforcement Zone"
        },
        color="congestion_impact_score",
        color_continuous_scale="Reds"
    )
    fig_zones.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_zones, use_container_width=True)

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
    st.subheader("High-Risk Hours")
    st.caption(
        "These time windows are most vulnerable to parking-induced congestion."
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

required_alloc_cols = {"enforcement_zone", "congestion_impact_score"}
if not required_alloc_cols.issubset(df.columns):
    st.warning(
        f"Missing columns for Officer Allocation: "
        f"{required_alloc_cols - set(df.columns)}"
    )
else:
    st.subheader("Officer Allocation Recommendations")

    top_zones_alloc = (
        df.groupby("enforcement_zone")["congestion_impact_score"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    def officers_needed(score):
        if score > 80:
            return 5
        elif score > 60:
            return 3
        return 1

    top_zones_alloc["Officers Needed"] = top_zones_alloc[
        "congestion_impact_score"
    ].apply(officers_needed)

    top_zones_alloc = top_zones_alloc.rename(columns={
        "enforcement_zone": "Zone",
        "congestion_impact_score": "Risk Score"
    }).sort_values("Risk Score", ascending=False)

    total_officers = top_zones_alloc["Officers Needed"].sum()
    high_risk_zones = (top_zones_alloc["Risk Score"] > 60).sum()

    m1, m2 = st.columns(2)
    m1.metric("Total Recommended Officers", total_officers)
    m2.metric("High Risk Zones", high_risk_zones)

    st.dataframe(
        top_zones_alloc[["Zone", "Risk Score", "Officers Needed"]],
        use_container_width=True,
        hide_index=True
    )
