# 🚦 UnJam

AI-powered parking intelligence platform that detects illegal parking hotspots, predicts congestion risk, and recommends optimal officer deployment using historical parking violation data.

---

## Problem Statement

Illegal parking and spillover parking reduce road capacity, increase congestion, and make traffic enforcement largely reactive.

UnJam helps authorities:

- Detect parking hotspots
- Quantify congestion impact
- Predict high-risk congestion zones
- Optimize officer deployment

---

## Features

### 📍 Hotspot Detection
- Interactive parking hotspot heatmap
- High-risk enforcement zone identification

### 📊 Congestion Intelligence
- Congestion impact scoring
- Risk-based zone prioritization

### 🤖 AI Risk Prediction
- Random Forest Classifier
- Predicts high-congestion-risk locations
- Accuracy: **91.3%**

### 👮 Smart Deployment Planner
- Officer allocation recommendations
- Risk threshold simulation
- Resource optimization

---

## Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### Data Processing
- Pandas
- NumPy

### Machine Learning
- Scikit-Learn
- Random Forest Classifier

### Visualization
- Plotly
- Folium

---

## Architecture

Parking Violation Data

↓  

Data Cleaning & Preprocessing

↓

Feature Engineering

↓

Congestion Impact Scoring

↓

Random Forest Prediction Engine

↓

Deployment Optimization

↓

UnJam Dashboard

---

## Setup

### Clone Repository

```bash
git clone https://github.com/<your-username>/UnJam.git
cd UnJam
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Dataset Setup

Create:

```text
data/raw/
```

Place the dataset inside:

```text
data/raw/jan to may police violation_anonymized791b166.csv
```

---

## Run Data Processing

Open and run:

```text
notebooks/01_data_exploration.ipynb
```

Output:

```text
data/processed/cleaned_parking_data.csv
```

---

## Train ML Model

Open and run:

```text
notebooks/03_congestion_prediction_model.ipynb
```

Output:

```text
data/processed/prediction_results.csv
```

---

## Launch Dashboard

```bash
streamlit run app.py
```

Dashboard:

```text
http://localhost:8501
```

---

## Team

### Brinda Jallapuram
- Machine Learning
- Data Engineering
- Predictive Analytics

### Harsha Sri Kaveti
- Dashboard Development
- UI/UX Design
- Visualization & Deployment Planning

---

## Impact

✅ Detects parking-induced congestion hotspots

✅ Predicts future congestion risk

✅ Enables proactive enforcement

✅ Optimizes officer allocation

🚦 Built for smarter cities.