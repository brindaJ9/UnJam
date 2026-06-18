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

# =============================================================
# SHARED: Build peak_hours dataframe (used by Sections 4 & 5)
# =============================================================

required_pred_cols = {"enforcement_zone", "hour", "congestion_impact_score"}
_pred_cols_present = required_pred_cols.issubset(df.columns)

if _pred_cols_present:
    # Aggregate by zone + hour
    _zone_hour = (
        df.groupby(["enforcement_zone", "hour"])
        .agg(
            avg_score=("congestion_impact_score", "mean"),
            violation_count=("congestion_impact_score", "count")
        )
        .reset_index()
    )

    # Peak hour per zone = hour with highest avg score
    peak_hours = (
        _zone_hour.loc[
            _zone_hour.groupby("enforcement_zone")["avg_score"].idxmax()
        ][["enforcement_zone", "hour", "avg_score", "violation_count"]]
        .rename(columns={"hour": "peak_hour"})
        .copy()
    )

    # Normalize violation count 0–100
    v_min = peak_hours["violation_count"].min()
    v_max = peak_hours["violation_count"].max()
    peak_hours["norm_violation"] = (
        ((peak_hours["violation_count"] - v_min) / (v_max - v_min) * 100)
        if v_max > v_min else 50.0
    )

    # Predicted risk 0–100
    raw_score = 0.7 * peak_hours["avg_score"] + 0.3 * peak_hours["norm_violation"]
    r_min, r_max = raw_score.min(), raw_score.max()
    peak_hours["predicted_risk"] = (
        ((raw_score - r_min) / (r_max - r_min) * 100).round(1)
        if r_max > r_min else 50.0
    )

    def risk_category(score):
        if score >= 85:   return "🔴 Critical"
        elif score >= 70: return "🟠 High"
        elif score >= 40: return "🟡 Medium"
        return "🟢 Low"

    def pred_officers(score):
        if score >= 85:   return 5
        elif score >= 70: return 4
        elif score >= 40: return 2
        return 1

    peak_hours["risk_category"]        = peak_hours["predicted_risk"].apply(risk_category)
    peak_hours["recommended_officers"] = peak_hours["predicted_risk"].apply(pred_officers)


# =============================================================
# SECTION 4: PREDICTIVE ENFORCEMENT RECOMMENDATIONS
# =============================================================
st.divider()

if not _pred_cols_present:
    st.warning(
        f"Missing columns for Predictive Enforcement: "
        f"{required_pred_cols - set(df.columns)}"
    )
else:
    st.subheader("🔮 Predictive Enforcement Recommendations")
    st.caption(
        "Forecasted congestion risk by zone and peak hour — "
        "identify future enforcement priorities before violations occur."
    )

    display_df = (
        peak_hours[[
            "enforcement_zone", "peak_hour",
            "predicted_risk", "risk_category",
            "recommended_officers"
        ]]
        .sort_values("predicted_risk", ascending=False)
        .head(15)
        .rename(columns={
            "enforcement_zone":     "Zone",
            "peak_hour":            "Peak Hour",
            "predicted_risk":       "Predicted Risk",
            "risk_category":        "Risk Category",
            "recommended_officers": "Recommended Officers"
        })
        .reset_index(drop=True)
    )

    critical_count   = (peak_hours["predicted_risk"] >= 85).sum()
    high_count       = ((peak_hours["predicted_risk"] >= 70) & (peak_hours["predicted_risk"] < 85)).sum()
    total_pred_off   = peak_hours["recommended_officers"].sum()

    k1, k2, k3 = st.columns(3)
    k1.metric("🔴 Critical Zones",          int(critical_count))
    k2.metric("🟠 High Risk Zones",         int(high_count))
    k3.metric("👮 Total Officers Required", int(total_pred_off))

    def color_risk(val):
        return {
            "🔴 Critical": "background-color: #ff4b4b; color: white;",
            "🟠 High":     "background-color: #ffa500; color: white;",
            "🟡 Medium":   "background-color: #ffd700; color: black;",
            "🟢 Low":      "background-color: #21c354; color: white;",
        }.get(val, "")

    styled = display_df.style.applymap(
        color_risk, subset=["Risk Category"]
    ).format({"Predicted Risk": "{:.1f}", "Peak Hour": "{:02d}:00"})

    st.dataframe(styled, use_container_width=True, hide_index=True)


# =============================================================
# SECTION 5: SMART ENFORCEMENT DEPLOYMENT SIMULATOR
# =============================================================
st.divider()

if not _pred_cols_present:
    st.warning(
        "Smart Enforcement Simulator requires: "
        f"{required_pred_cols - set(df.columns)}"
    )
else:
    st.subheader("🚓 Smart Enforcement Deployment Simulator")
    st.caption(
        "Allocate a fixed number of officers to the highest-risk zones "
        "and preview the deployment on the map."
    )

    # Sidebar slider
    available_officers = st.sidebar.slider(
        "👮 Available Officers",
        min_value=5,
        max_value=100,
        value=25,
        step=1
    )

    # ── Greedy allocation ────────────────────────────────────
    sorted_zones = (
        peak_hours
        .sort_values("predicted_risk", ascending=False)
        .copy()
        .reset_index(drop=True)
    )

    remaining     = available_officers
    assigned_list = []
    priority_rank = 0

    for _, row in sorted_zones.iterrows():
        if remaining <= 0:
            break
        alloc = min(int(row["recommended_officers"]), remaining)
        priority_rank += 1
        assigned_list.append({
            "Zone":             row["enforcement_zone"],
            "Predicted Risk":   round(row["predicted_risk"], 1),
            "Risk Category":    row["risk_category"],
            "Assigned Officers": alloc,
            "Priority Rank":    priority_rank
        })
        remaining -= alloc

    deployment_df = pd.DataFrame(assigned_list)

    allocated_officers   = available_officers - remaining
    unallocated_officers = remaining
    zones_covered        = len(deployment_df)

    # ── KPI cards ────────────────────────────────────────────
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("👮 Available Officers",   available_officers)
    d2.metric("✅ Allocated Officers",   allocated_officers)
    d3.metric("❌ Unallocated Officers", unallocated_officers)
    d4.metric("📍 Zones Covered",        zones_covered)

    # ── Deployment table ─────────────────────────────────────
    styled_dep = deployment_df.style.applymap(
        color_risk, subset=["Risk Category"]
    ).format({"Predicted Risk": "{:.1f}"})

    st.dataframe(styled_dep, use_container_width=True, hide_index=True)

    # ── Congestion reduction estimate ────────────────────────
    reduction = min(allocated_officers * 1.5, 100)
    st.info(f"📉 Estimated Congestion Reduction: **{reduction:.1f}%**")

    # ── Deployment map ────────────────────────────────────────
    has_coords = {"latitude", "longitude", "enforcement_zone"}.issubset(df.columns)

    if has_coords:
        # Average lat/lon per zone
        zone_coords = (
            df.groupby("enforcement_zone")[["latitude", "longitude"]]
            .mean()
            .reset_index()
        )
        dep_map_df = deployment_df.merge(
            zone_coords, left_on="Zone", right_on="enforcement_zone", how="left"
        ).dropna(subset=["latitude", "longitude"])

        dep_map = folium.Map(location=[12.97, 77.59], zoom_start=11)

        color_map = {
            "🔴 Critical": "red",
            "🟠 High":     "orange",
            "🟡 Medium":   "beige",
            "🟢 Low":      "green",
        }

        for _, row in dep_map_df.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=8,
                color=color_map.get(row["Risk Category"], "blue"),
                fill=True,
                fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b>{row['Zone']}</b><br>"
                    f"Risk: {row['Predicted Risk']}<br>"
                    f"Officers: {row['Assigned Officers']}",
                    max_width=200
                )
            ).add_to(dep_map)

        st.subheader("📍 Deployment Map")
        st_folium(dep_map, width=900, height=500, key="deployment_map")
    else:
        st.info("Deployment map unavailable — latitude/longitude columns not found.")

    # ── Summary action plan ───────────────────────────────────
    top_zone_name  = deployment_df.iloc[0]["Zone"] if not deployment_df.empty else "N/A"
    peak_hr        = int(sorted_zones.iloc[0]["peak_hour"]) if not sorted_zones.empty else 0

    st.subheader("📋 Recommended Action Plan")
    st.success(
        f"Deploy **{allocated_officers} officers** across **{zones_covered} priority zones**.\n\n"
        f"Focus on **{top_zone_name}** and surrounding hotspots during peak hour "
        f"(**{peak_hr:02d}:00**).\n\n"
        f"Expected congestion reduction: **{reduction:.1f}%**."
    )
