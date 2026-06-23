import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
import plotly.express as px
from streamlit_folium import st_folium

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UnJam · Command Center",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# LIQUID-GLASS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: #e2e8f0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
            
/* ── Hide Streamlit top toolbar ── */
header[data-testid="stHeader"] {
    display: none;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* ── Reduce default top padding ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}

[data-testid="stSidebar"] { display: none; }

/* ── Glass card utility ── */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

/* ── KPI card ── */
.kpi-card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 44px rgba(0,0,0,0.45);
}
.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(148, 163, 184, 0.9);
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: rgba(148, 163, 184, 0.7);
    margin-top: 0.35rem;
}
.kpi-accent-blue  { border-top: 3px solid #3b82f6; }
.kpi-accent-red   { border-top: 3px solid #ef4444; }
.kpi-accent-amber { border-top: 3px solid #f59e0b; }
.kpi-accent-green { border-top: 3px solid #10b981; }

/* ── Recommendation card ── */
.rec-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 6px 24px rgba(0,0,0,0.3);
    transition: transform 0.2s ease;
}
.rec-card:hover { transform: translateY(-2px); }
.rec-zone {
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.6rem;
}
.rec-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    margin-right: 0.4rem;
    margin-bottom: 0.5rem;
}
.badge-critical { background: rgba(239,68,68,0.25); color: #fca5a5; border: 1px solid rgba(239,68,68,0.4); }
.badge-high     { background: rgba(245,158,11,0.25); color: #fcd34d; border: 1px solid rgba(245,158,11,0.4); }
.badge-medium   { background: rgba(59,130,246,0.25); color: #93c5fd; border: 1px solid rgba(59,130,246,0.4); }
.badge-low      { background: rgba(16,185,129,0.25); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.4); }
.rec-meta {
    font-size: 0.78rem;
    color: rgba(148,163,184,0.85);
    line-height: 1.8;
}
.rec-action {
    font-size: 0.82rem;
    color: #a5b4fc;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* ── Section heading ── */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: rgba(148,163,184,0.8);
    margin-bottom: 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* ── Dashboard header ── */
.dash-header {
    padding: 0.6rem 0 0.75rem 0;
    margin-bottom: 0.25rem;
}
.dash-title {
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.dash-subtitle {
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: rgba(148,163,184,0.65);
    margin-top: 0.3rem;
    text-transform: uppercase;
}
.dash-caption {
    font-size: 0.75rem;
    color: rgba(148,163,184,0.45);
    margin-top: 0.2rem;
    font-style: italic;
}

/* ── Streamlit tab styling ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.08);
    gap: 2px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(148,163,184,0.8) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(96,165,250,0.2) !important;
    color: #93c5fd !important;
    box-shadow: 0 2px 12px rgba(96,165,250,0.2) !important;
}

/* ── Metric overrides ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 0.8rem 1rem;
    border: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stMetricLabel"] { color: rgba(148,163,184,0.85) !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ── Input widgets ── */
[data-testid="stNumberInput"], [data-testid="stSlider"] {
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 0.2rem 0;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly, .js-plotly-plot .plotly .svg-container {
    background: transparent !important;
}

/* ── Success/info boxes ── */
[data-testid="stSuccess"], [data-testid="stInfo"] {
    background: rgba(16,185,129,0.1) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important;
    color: #6ee7b7 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING  (unchanged logic)
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_parking_data.csv")


@st.cache_data
def load_ai_outputs():
    hotspots   = pd.read_csv("outputs/hotspot_rankings.csv")
    enforcement = pd.read_csv("outputs/enforcement_plan.csv")
    peak_forecast = pd.read_csv("outputs/peak_hour_forecast.csv")
    return hotspots, enforcement, peak_forecast


df = load_data()
hotspots, enforcement, peak_forecast = load_ai_outputs()

# Pre-compute derived values (unchanged logic)
df["created_datetime"] = pd.to_datetime(df["created_datetime"], format="ISO8601")
hourly = df["created_datetime"].dt.hour.value_counts().sort_index()

total_violations     = len(df)
n_hotspots           = len(hotspots[hotspots["risk_level"] == "Critical"])
recommended_officers = int(enforcement["recommended_officers"].sum())

if "hour" in df.columns and "congestion_impact_score" in df.columns:
    hourly_risk = (
        df.groupby("hour")["congestion_impact_score"]
        .mean()
        .reset_index()
    )
    high_risk_hours = int(
        (hourly_risk["congestion_impact_score"] > hourly_risk["congestion_impact_score"].mean()).sum()
    )
else:
    high_risk_hours = "N/A"
    hourly_risk = None


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div class="dash-title">UNJAM</div>
  <div class="dash-subtitle">AI Traffic Intelligence Platform</div>
  <div class="dash-caption">Predictive Parking Enforcement &amp; Congestion Prevention</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_overview, tab_risk, tab_deploy, tab_ai, tab_impact = st.tabs([
    "🏙️  Overview",
    "⚠️  Risk Intelligence",
    "🚓  Deployment Planner",
    "🤖  AI Recommendations",
    "📈  Impact & Performance",
])


# ══════════════════════════════════════════════
# TAB 1 · OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:

    # ── KPI row ──────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-blue">
            <div class="kpi-label">Total Violations</div>
            <div class="kpi-value">{total_violations:,}</div>
            <div class="kpi-sub">All recorded incidents</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-red">
            <div class="kpi-label">Critical Hotspots</div>
            <div class="kpi-value">{n_hotspots}</div>
            <div class="kpi-sub">Zones needing urgent action</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-amber">
            <div class="kpi-label">High Risk Hours</div>
            <div class="kpi-value">{high_risk_hours}</div>
            <div class="kpi-sub">Above-average congestion windows</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-green">
            <div class="kpi-label">Recommended Officers</div>
            <div class="kpi-value">{recommended_officers:,}</div>
            <div class="kpi-sub">AI-calculated deployment need</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ───────────────────────────
    col_chart, col_map = st.columns([1, 1], gap="large")

    with col_chart:
        st.markdown('<div class="section-title">📊 Violations by Hour</div>', unsafe_allow_html=True)
        hourly_df = hourly.reset_index()
        hourly_df.columns = ["Hour", "Violations"]
        fig_hourly = px.area(
            hourly_df, x="Hour", y="Violations",
            color_discrete_sequence=["#60a5fa"],
            template="plotly_dark",
        )
        fig_hourly.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            font_color="#cbd5e1",
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        fig_hourly.update_traces(fillcolor="rgba(96,165,250,0.15)", line_color="#60a5fa")
        st.plotly_chart(fig_hourly, use_container_width=True)

    with col_map:
        st.markdown('<div class="section-title">🗺️ Bengaluru Illegal Parking Hotspots</div>', unsafe_allow_html=True)

        required_heat_cols = {"latitude", "longitude", "congestion_impact_score"}
        if required_heat_cols.issubset(df.columns):
            heat_df = df[["latitude", "longitude", "congestion_impact_score"]].dropna()
            if len(heat_df) > 10000:
                heat_df = heat_df.sample(10000, random_state=42)
            heat_data = heat_df[["latitude", "longitude", "congestion_impact_score"]].values.tolist()

            heat_map = folium.Map(location=[12.97, 77.59], zoom_start=11, tiles="CartoDB dark_matter")
            HeatMap(
                heat_data,
                min_opacity=0.3,
                radius=10,
                blur=12,
                gradient={0.4: "blue", 0.65: "orange", 1.0: "red"},
            ).add_to(heat_map)
            st_folium(heat_map, width=None, height=420, key="overview_heatmap")
        else:
            st.warning(f"Missing columns for Heatmap: {required_heat_cols - set(df.columns)}")


# ══════════════════════════════════════════════
# TAB 2 · RISK INTELLIGENCE
# ══════════════════════════════════════════════
with tab_risk:

    # ── Row 1: Top Zones + High-Risk Hours ───
    r1c1, r1c2 = st.columns(2, gap="large")

    with r1c1:
        st.markdown('<div class="section-title">🔥 Top Enforcement Zones</div>', unsafe_allow_html=True)
        top_hotspots = hotspots.sort_values("priority_score", ascending=False).head(10)

        fig_zones = px.bar(
            top_hotspots,
            x="priority_score",
            y="enforcement_zone",
            orientation="h",
            color="priority_score",
            color_continuous_scale=["#1e40af", "#3b82f6", "#f59e0b", "#ef4444"],
            template="plotly_dark",
            labels={"priority_score": "Priority Score", "enforcement_zone": "Zone"},
        )
        fig_zones.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            font_color="#cbd5e1",
            coloraxis_showscale=False,
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        )
        st.plotly_chart(fig_zones, use_container_width=True)

    with r1c2:
        st.markdown('<div class="section-title">📈 City-Wide Congestion Trend</div>', unsafe_allow_html=True)
        if hourly_risk is not None:
            fig_hours = px.line(
                hourly_risk,
                x="hour",
                y="congestion_impact_score",
                markers=True,
                template="plotly_dark",
                color_discrete_sequence=["#a78bfa"],
                labels={"hour": "Hour of Day", "congestion_impact_score": "Avg Congestion Impact"},
            )
            fig_hours.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                font_color="#cbd5e1",
                xaxis=dict(tickmode="linear", dtick=1, gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            )
            fig_hours.update_traces(line=dict(color="#a78bfa", width=2.5))
            st.plotly_chart(fig_hours, use_container_width=True)
        else:
            st.warning("Missing columns for Congestion Trend chart.")

    # ── Row 2: Zone table + Peak forecast ────
    r2c1, r2c2 = st.columns(2, gap="large")

    with r2c1:
        st.markdown('<div class="section-title">📋 Hotspot Rankings</div>', unsafe_allow_html=True)
        st.dataframe(
            top_hotspots[["enforcement_zone", "priority_score", "risk_level"]],
            use_container_width=True,
            hide_index=True,
        )

    with r2c2:
        st.markdown('<div class="section-title">⏰ Peak Enforcement Forecast</div>', unsafe_allow_html=True)
        st.dataframe(
            peak_forecast[["enforcement_zone", "recommended_time_window", "hourly_risk_score"]].head(10),
            use_container_width=True,
            hide_index=True,
        )


# ══════════════════════════════════════════════
# TAB 3 · DEPLOYMENT PLANNER
# ══════════════════════════════════════════════
with tab_deploy:

    # ── Simulation controls ───────────────────
    st.markdown('<div class="section-title">⚙️ Simulation Controls</div>', unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns([1, 2, 1], gap="large")

    with ctrl1:
        available_officers = st.number_input(
            "👮 Available Officers",
            min_value=10,
            max_value=2000,
            value=1000,
            step=10,
            help="Total officers available for deployment",
        )

    with ctrl2:
        risk_threshold = st.slider(
            "⚠️ Enforcement Priority Threshold (%)",
            min_value=0,
            max_value=100,
            value=70,
            step=5,
            help="Only deploy to zones whose Risk Score is at or above this value",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Simulation logic (unchanged allocation math) ─────────
    simulation = enforcement.copy()
    simulation = simulation.sort_values("priority_score", ascending=False)

    # Filter: only zones whose risk score meets the threshold
    simulation = simulation[simulation["priority_score"] >= risk_threshold]

    if len(simulation) == 0:
        st.warning(f"No zones have a Risk Score ≥ {risk_threshold}. Lower the threshold to see results.")
    else:
        raw_allocation = (
            simulation["enforcement_demand_score"]
            / simulation["enforcement_demand_score"].sum()
            * available_officers
        )
        simulation["simulated_officers"] = raw_allocation.astype(int)

        remaining = available_officers - simulation["simulated_officers"].sum()
        if remaining > 0:
            top_indexes = (
                raw_allocation.sort_values(ascending=False).head(remaining).index
            )
            simulation.loc[top_indexes, "simulated_officers"] += 1

        # ── Deployment recommendation (shown first) ───
        impact = min(
            (simulation["simulated_officers"] * simulation["enforcement_demand_score"]).sum() / 1000,
            100,
        )
        st.success(
            f"📋 **Deployment Recommendation** — Deploy {available_officers} officers across "
            f"{len(simulation[simulation['simulated_officers'] > 0])} priority zones. "
            f"Highest priority: **{simulation.iloc[0]['enforcement_zone']}**. "
            f"Estimated congestion improvement: **{impact:.1f}%**"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Resource metrics ──────────────────
        st.markdown('<div class="section-title">📊 Resource Allocation Metrics</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Available Officers", available_officers)
        m2.metric("Allocated Officers", simulation["simulated_officers"].sum())
        m3.metric("Zones Covered", len(simulation[simulation["simulated_officers"] > 0]))
        m4.metric("Risk Threshold", f"{risk_threshold}%")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Officer allocation table + bar chart ──
        tbl_col, chart_col = st.columns([1.2, 1], gap="large")

        with tbl_col:
            st.markdown('<div class="section-title">🗂️ Officer Allocation Table</div>', unsafe_allow_html=True)

            # Build display table — expose risk score and priority classification
            alloc_display = simulation[
                ["enforcement_zone", "priority_score", "risk_level", "simulated_officers"]
            ].copy()

            alloc_display["priority_score"] = alloc_display["priority_score"].round(1)

            def classify_priority(score):
                if score >= 80:
                    return "🔴 High"
                elif score >= 60:
                    return "🟡 Medium"
                else:
                    return "🟢 Low"

            alloc_display["Priority"] = alloc_display["priority_score"].apply(classify_priority)

            alloc_display = alloc_display.rename(columns={
                "enforcement_zone": "Zone",
                "priority_score":   "Risk Score",
                "simulated_officers": "Officers Needed",
            }).drop(columns=["risk_level"])

            alloc_display = alloc_display[["Zone", "Risk Score", "Priority", "Officers Needed"]]

            st.dataframe(
                alloc_display,
                use_container_width=True,
                hide_index=True,
            )

        with chart_col:
            st.markdown('<div class="section-title">📊 Allocation Distribution</div>', unsafe_allow_html=True)
            fig_alloc = px.bar(
                simulation.head(15),
                x="simulated_officers",
                y="enforcement_zone",
                orientation="h",
                color="simulated_officers",
                color_continuous_scale=["#1e3a5f", "#3b82f6", "#34d399"],
                template="plotly_dark",
                labels={"simulated_officers": "Officers", "enforcement_zone": "Zone"},
            )
            fig_alloc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                font_color="#cbd5e1",
                coloraxis_showscale=False,
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            )
            st.plotly_chart(fig_alloc, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 · AI RECOMMENDATIONS  (with Explainable AI)
# ══════════════════════════════════════════════
with tab_ai:

    st.markdown('<div class="section-title">🤖 Zone Intelligence Cards</div>', unsafe_allow_html=True)

    # ── City-wide baselines for explainability ──
    city_avg_congestion  = df["congestion_impact_score"].mean()
    city_avg_violations  = df.groupby("enforcement_zone")["violation_count"].sum().mean()
    city_avg_veh_impact  = df["vehicle_impact"].mean()

    # Peak-hour (17–20) violation rate vs city average
    peak_mask            = df["hour"].between(17, 20)
    zone_peak_viol       = (
        df[peak_mask]
        .groupby("enforcement_zone")["violation_count"]
        .sum()
        .rename("peak_violations")
    )
    zone_total_viol      = (
        df.groupby("enforcement_zone")["violation_count"]
        .sum()
        .rename("total_violations")
    )
    city_peak_avg        = zone_peak_viol.mean()

    # Heavy vehicles (vehicle_impact >= 3 means heavy/multi-axle)
    heavy_mask           = df["vehicle_impact"] >= 3
    zone_heavy_pct       = (
        df[heavy_mask]
        .groupby("enforcement_zone")["vehicle_impact"]
        .count()
        .div(df.groupby("enforcement_zone")["vehicle_impact"].count())
        .fillna(0)
        .rename("heavy_pct")
    )
    city_heavy_pct_avg   = zone_heavy_pct.mean()

    # Repeat-violation proxy: rows per zone / unique days
    df["date"] = df["created_datetime"].dt.date
    zone_days            = df.groupby("enforcement_zone")["date"].nunique().rename("active_days")
    zone_daily_rate      = (zone_total_viol / zone_days).rename("daily_rate")
    city_daily_rate_avg  = zone_daily_rate.mean()

    # Peak forecast — best window per zone
    pf_best = (
        peak_forecast
        .sort_values("hourly_risk_score", ascending=False)
        .drop_duplicates("enforcement_zone")[["enforcement_zone", "recommended_time_window", "hourly_risk_score"]]
        .set_index("enforcement_zone")
    )

    # Build recommendation data
    rec_df = (
        hotspots
        .merge(
            enforcement[["enforcement_zone", "recommended_officers", "enforcement_demand_score"]],
            on="enforcement_zone",
            how="left",
        )
        .sort_values("priority_score", ascending=False)
        .head(12)
    )

    def get_action(risk_level):
        actions = {
            "Critical": "Immediate heavy deployment + traffic barriers",
            "High":     "Surge enforcement during peak hours",
            "Medium":   "Standard patrol with periodic check-ins",
            "Low":      "Routine monitoring — low intervention needed",
        }
        return actions.get(str(risk_level).capitalize(), "Monitor and assess")

    def get_badge_class(risk_level):
        mapping = {
            "Critical": "badge-critical",
            "High":     "badge-high",
            "Medium":   "badge-medium",
            "Low":      "badge-low",
        }
        return mapping.get(str(risk_level).capitalize(), "badge-medium")

    def predicted_congestion(score):
        if pd.isna(score):
            return "N/A"
        pct = min(score / rec_df["enforcement_demand_score"].max() * 100, 100)
        return f"{pct:.0f}%"

    def build_reasons(zone, rec):
        """Return a list of (icon, reason) tuples — only truths, derived from data."""
        reasons = []

        # 1. Congestion impact above city average
        zone_cong = rec.get("avg_congestion_score", None)
        if pd.notna(zone_cong) and zone_cong > city_avg_congestion:
            reasons.append(("✓", f"Congestion impact ({zone_cong:.1f}) exceeds city average ({city_avg_congestion:.1f})"))

        # 2. Peak-hour violations above city average
        ph = zone_peak_viol.get(zone, 0)
        if ph > city_peak_avg:
            reasons.append(("✓", "Peak-hour violations exceed city average (5 PM – 8 PM window)"))

        # 3. High daily repeat violations
        dr = zone_daily_rate.get(zone, 0)
        if pd.notna(dr) and dr > city_daily_rate_avg:
            reasons.append(("✓", "Repeated daily violations observed at this location"))

        # 4. Heavy vehicle activity
        hv = zone_heavy_pct.get(zone, 0)
        if pd.notna(hv) and hv > city_heavy_pct_avg:
            reasons.append(("✓", f"Heavy vehicle activity above average ({hv*100:.0f}% of violations)"))

        # 5. High violation frequency score (from enforcement data)
        freq = rec.get("frequency_score", None)
        if pd.notna(freq) and freq > 50:
            reasons.append(("✓", f"High violation frequency score ({freq:.0f}/100)"))

        return reasons if reasons else [("✓", "Elevated combined risk score from enforcement model")]

    # ── Render cards in a 3-column grid ──────
    cols_per_row = 3
    rows = [rec_df.iloc[i:i+cols_per_row] for i in range(0, len(rec_df), cols_per_row)]

    # Merge frequency_score into rec_df for reason generation
    rec_df = rec_df.merge(
        enforcement[["enforcement_zone", "frequency_score", "avg_congestion_score"]],
        on="enforcement_zone",
        how="left",
        suffixes=("", "_enf"),
    )

    for row_slice in rows:
        cols = st.columns(cols_per_row, gap="medium")
        for col, (_, rec) in zip(cols, row_slice.iterrows()):
            zone       = rec["enforcement_zone"]
            badge_cls  = get_badge_class(rec.get("risk_level", ""))
            risk_label = str(rec.get("risk_level", "N/A")).capitalize()
            action     = get_action(rec.get("risk_level", ""))
            officers   = int(rec["recommended_officers"]) if pd.notna(rec.get("recommended_officers")) else "N/A"
            congestion = predicted_congestion(rec.get("enforcement_demand_score"))
            priority   = f"{rec.get('priority_score', 0):.1f}"
            reasons    = build_reasons(zone, rec)
            time_window = pf_best.loc[zone, "recommended_time_window"] if zone in pf_best.index else "—"

            reasons_html = "".join(
                f'<div style="color:#86efac;font-size:0.74rem;margin:0.18rem 0;">'
                f'<span style="color:#4ade80;margin-right:0.4rem;">{icon}</span>{text}</div>'
                for icon, text in reasons
            )

            with col:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-zone">📍 {zone}</div>
                    <span class="rec-badge {badge_cls}">{risk_label}</span>
                    <div class="rec-meta" style="margin-top:0.5rem;">
                        🎯 Risk Score: <b>{priority}</b> &nbsp;|&nbsp;
                        📈 Est. Congestion: <b>{congestion}</b>
                    </div>
                    <div style="margin-top:0.75rem;margin-bottom:0.4rem;font-size:0.72rem;
                                font-weight:700;letter-spacing:0.05em;color:rgba(148,163,184,0.6);
                                text-transform:uppercase;">
                        Why was this location flagged?
                    </div>
                    {reasons_html}
                    <div style="margin-top:0.8rem;padding-top:0.6rem;
                                border-top:1px solid rgba(255,255,255,0.07);">
                        <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.05em;
                                    color:rgba(148,163,184,0.6);text-transform:uppercase;
                                    margin-bottom:0.35rem;">Recommended Action</div>
                        <div class="rec-action">→ {action}</div>
                        <div style="font-size:0.76rem;color:rgba(148,163,184,0.75);margin-top:0.3rem;">
                            👮 Deploy <b style="color:#f1f5f9;">{officers}</b> officers
                            &nbsp;·&nbsp;
                            🕐 <b style="color:#f1f5f9;">{time_window}</b>
                            &nbsp;·&nbsp;
                            Priority: <b style="color:#f1f5f9;">{risk_label}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 5 · IMPACT & PERFORMANCE
# ══════════════════════════════════════════════
with tab_impact:

    st.markdown("""
    <div style="font-size:0.78rem;color:rgba(148,163,184,0.55);margin-bottom:1rem;font-style:italic;">
        Historical trend analysis based on recorded violation data.
        This is not a live dashboard — it reflects patterns across the observation period.
    </div>
    """, unsafe_allow_html=True)

    # ── Pre-compute monthly aggregates ───────
    MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    monthly_congestion = (
        df.groupby("month")["congestion_impact_score"]
        .mean()
        .reset_index()
        .rename(columns={"month": "Month", "congestion_impact_score": "Avg Congestion Score"})
    )
    monthly_congestion["Month Label"] = monthly_congestion["Month"].map(MONTH_NAMES)

    # High-risk zone count per month using the deployment planner threshold
    monthly_highrisk = (
        df[df["congestion_impact_score"] >= risk_threshold]
        .groupby("month")["location"]
        .nunique()
        .reset_index()
        .rename(columns={"month": "Month", "location": "High-Risk Locations"})
    )
    monthly_highrisk["Month Label"] = monthly_highrisk["Month"].map(MONTH_NAMES)

    # ── Row 1: Monthly congestion + high-risk count ──
    ic1, ic2 = st.columns(2, gap="large")

    with ic1:
        st.markdown('<div class="section-title">📉 Monthly Congestion Risk Trend</div>', unsafe_allow_html=True)
        st.caption("Tracks historical changes in average congestion impact across the city.")

        fig_mc = px.line(
            monthly_congestion,
            x="Month Label",
            y="Avg Congestion Score",
            markers=True,
            template="plotly_dark",
            color_discrete_sequence=["#f59e0b"],
        )
        fig_mc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            font_color="#cbd5e1",
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", categoryorder="array",
                       categoryarray=list(MONTH_NAMES.values())),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        fig_mc.update_traces(line=dict(color="#f59e0b", width=2.5),
                             marker=dict(size=7, color="#fcd34d"))
        st.plotly_chart(fig_mc, use_container_width=True)

    with ic2:
        st.markdown('<div class="section-title">🔴 High-Risk Zones Over Time</div>', unsafe_allow_html=True)
        st.caption(f"Locations exceeding congestion score ≥ {risk_threshold} — using active deployment threshold.")

        if monthly_highrisk.empty:
            st.info(f"No locations exceeded a congestion score of {risk_threshold} in any month. Try lowering the Deployment Planner threshold.")
        else:
            fig_hr = px.line(
                monthly_highrisk,
                x="Month Label",
                y="High-Risk Locations",
                markers=True,
                template="plotly_dark",
                color_discrete_sequence=["#ef4444"],
            )
            fig_hr.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                font_color="#cbd5e1",
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", categoryorder="array",
                           categoryarray=list(MONTH_NAMES.values())),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            )
            fig_hr.update_traces(line=dict(color="#ef4444", width=2.5),
                                 marker=dict(size=7, color="#fca5a5"))
            st.plotly_chart(fig_hr, use_container_width=True)

    # ── Section 3: Most Improved Zones ───────
    st.markdown('<div class="section-title">🏆 Most Improved Zones</div>', unsafe_allow_html=True)
    st.caption("Locations showing the largest reduction in average congestion risk from earliest to latest recorded month.")

    zone_monthly = (
        df.groupby(["enforcement_zone", "month"])["congestion_impact_score"]
        .mean()
        .reset_index()
    )

    # Need at least 2 months of data per zone
    zone_month_counts = zone_monthly.groupby("enforcement_zone")["month"].nunique()
    multi_month_zones = zone_month_counts[zone_month_counts >= 2].index
    zone_monthly_filtered = zone_monthly[zone_monthly["enforcement_zone"].isin(multi_month_zones)]

    if zone_monthly_filtered.empty:
        st.info("Insufficient monthly data to calculate zone improvement trends.")
    else:
        earliest = (
            zone_monthly_filtered.sort_values("month")
            .groupby("enforcement_zone")
            .first()
            .rename(columns={"congestion_impact_score": "Initial Risk", "month": "First Month"})
        )
        latest = (
            zone_monthly_filtered.sort_values("month")
            .groupby("enforcement_zone")
            .last()
            .rename(columns={"congestion_impact_score": "Current Risk", "month": "Last Month"})
        )
        improvement_df = earliest[["Initial Risk"]].join(latest[["Current Risk"]])
        improvement_df["Improvement"] = (
            improvement_df["Initial Risk"] - improvement_df["Current Risk"]
        ).round(2)

        top_improved = (
            improvement_df[improvement_df["Improvement"] > 0]
            .sort_values("Improvement", ascending=False)
            .head(10)
            .reset_index()
            .rename(columns={"enforcement_zone": "Zone"})
        )
        top_improved["Initial Risk"] = top_improved["Initial Risk"].round(2)
        top_improved["Current Risk"]  = top_improved["Current Risk"].round(2)

        if top_improved.empty:
            st.info("No zones show improvement over the recorded period.")
        else:
            st.dataframe(
                top_improved[["Zone", "Initial Risk", "Current Risk", "Improvement"]],
                use_container_width=True,
                hide_index=True,
            )


