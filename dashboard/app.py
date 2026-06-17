import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="UnJam",
    layout="wide"
)

st.title("🚦 UnJam")

@st.cache_data
def load_data():
    return pd.read_csv(
        "data/raw/jan to may police violation_anonymized791b166.csv"
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
