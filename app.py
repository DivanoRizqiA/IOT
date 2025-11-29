import streamlit as st
import pandas as pd
import os
import time
import plotly.express as px

st.set_page_config(page_title="Fitness Dashboard", layout="wide")

# --- Cari file CSV terbaru ---
def get_latest_csv():
    files = [f for f in os.listdir() if f.startswith("fitness_log_") and f.endswith(".csv")]
    if not files:
        return None
    files.sort(reverse=True)
    return files[0]  # file terbaru

latest_csv = get_latest_csv()

st.title("📊 Fitness Tracking Dashboard")

if latest_csv is None:
    st.warning("Tidak ada file CSV ditemukan. Jalankan program MQTT → CSV dulu.")
    st.stop()

df = pd.read_csv(latest_csv)

# Hilangkan baris STOP
df = df[df["steps"] != "STOP"]

# Pastikan tipe data numerik dan waktu benar
for col in ["steps", "hr", "calories"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Konversi timestamp (epoch detik) ke datetime untuk sumbu-X yang terbaca
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["time"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")
else:
    # Fallback jika kolom timestamp tidak ada: gunakan index sebagai waktu
    df["time"] = pd.RangeIndex(start=0, stop=len(df))

if len(df) == 0:
    st.warning("CSV ditemukan, tapi belum ada data sensor.")
    st.stop()

# --- DATA TERBARU ---
last_hr = df["hr"].iloc[-1]
last_steps = df["steps"].iloc[-1]
last_cal = df["calories"].iloc[-1]

st.subheader("Data Terbaru")
col1, col2, col3 = st.columns(3)
col1.metric("Steps", last_steps)
col2.metric("Heart Rate (bpm)", last_hr)
col3.metric("Calories", round(last_cal, 2))

# ====================================
#       Peringatan Heart Rate
# ====================================

if last_hr < 50:
    st.error("⚠️ **Heart Rate sangat rendah! (<50 bpm)**")
elif last_hr > 150:
    st.error("🚨 **Heart Rate sangat tinggi! (>150 bpm)**")
elif last_hr > 120:
    st.warning("⚠️ **Heart Rate tinggi! (>120 bpm)**")

# ====================================
#            Grafik Section
# ====================================
st.subheader("Grafik Sensor")

# Drop baris yang tidak valid untuk plotting
plot_df = df.dropna(subset=["time", "steps", "hr", "calories"]).copy()

# Steps
fig_steps = px.line(
    plot_df,
    x="time",
    y="steps",
    title="Steps",
    labels={"time": "Waktu", "steps": "Steps"},
)
fig_steps.update_layout(showlegend=True, xaxis_title="Waktu", yaxis_title="Steps")
fig_steps.update_traces(name="Steps", hovertemplate="Waktu=%{x}<br>Steps=%{y}")
st.plotly_chart(fig_steps, use_container_width=True)

# Heart Rate
fig_hr = px.line(
    plot_df,
    x="time",
    y="hr",
    title="Heart Rate (bpm)",
    labels={"time": "Waktu", "hr": "BPM"},
)
fig_hr.update_layout(showlegend=True, xaxis_title="Waktu", yaxis_title="BPM")
fig_hr.update_traces(name="Heart Rate", hovertemplate="Waktu=%{x}<br>HR=%{y} bpm")
st.plotly_chart(fig_hr, use_container_width=True)

# Calories
fig_cal = px.line(
    plot_df,
    x="time",
    y="calories",
    title="Calories",
    labels={"time": "Waktu", "calories": "Calories"},
)
fig_cal.update_layout(showlegend=True, xaxis_title="Waktu", yaxis_title="Calories")
fig_cal.update_traces(name="Calories", hovertemplate="Waktu=%{x}<br>Kalori=%{y}")
st.plotly_chart(fig_cal, use_container_width=True)