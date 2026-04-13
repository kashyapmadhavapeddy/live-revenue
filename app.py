import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ===============================
# CONFIG
# ===============================
st.set_page_config(layout="wide", page_title="⚡ Revenue War Room")

PRODUCTS = ["Laptop","Shoes","Watch","Phone","Bag","Tablet","Chair"]
CITIES = ["Hyderabad","Mumbai","Delhi","Bangalore","Chennai"]

# ===============================
# SESSION STATE
# ===============================
if "sales" not in st.session_state:
    st.session_state.sales = []
if "last" not in st.session_state:
    st.session_state.last = time.time()

# ===============================
# SALES ENGINE
# ===============================
def generate_sale():
    return {
        "time": datetime.now(),
        "product": random.choice(PRODUCTS),
        "city": random.choice(CITIES),
        "price": random.randint(1000,50000),
        "qty": random.randint(1,5)
    }

if time.time() - st.session_state.last > 2:
    st.session_state.sales.append(generate_sale())
    st.session_state.last = time.time()

df = pd.DataFrame(st.session_state.sales)

# ===============================
# METRICS
# ===============================
total_rev = df["price"].sum() if not df.empty else 0
orders = len(df)

last_30s = df[df["time"] > datetime.now() - timedelta(seconds=30)]
velocity = len(last_30s)

prev_30s = df[(df["time"] > datetime.now()-timedelta(seconds=60)) &
              (df["time"] <= datetime.now()-timedelta(seconds=30))]

trend = velocity - len(prev_30s)

# ===============================
# UI STYLE
# ===============================
st.markdown("""
<style>
body {background:#020617;color:white}
.card {
    background:#0f172a;
    border:1px solid #1e293b;
    padding:15px;
    border-radius:12px;
}
.glow {box-shadow:0 0 12px #22d3ee33}
.alert {padding:10px;border-radius:8px;margin-bottom:6px}
.green {background:#064e3b}
.red {background:#7f1d1d}
.yellow {background:#78350f}
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.title("⚡ REVENUE WAR ROOM v3")

# ===============================
# KPI ROW
# ===============================
c1,c2,c3,c4 = st.columns(4)
c1.metric("💰 Revenue", f"₹{total_rev}")
c2.metric("📦 Orders", orders)
c3.metric("⚡ Velocity (30s)", velocity)
c4.metric("📈 Trend", trend)

# ===============================
# SALES INTENSITY
# ===============================
st.subheader("🎯 Sales Intensity")

intensity = min(velocity * 2, 100)

st.progress(intensity)

if intensity > 70:
    st.success("🔥 HIGH DEMAND")
elif intensity > 30:
    st.warning("⚡ MEDIUM DEMAND")
else:
    st.error("❄ LOW DEMAND")

# ===============================
# CITY COMMAND GRID
# ===============================
st.subheader("🌍 City Command Center")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    city_df = df[df["city"] == city]
    rev = city_df["price"].sum()
    count = len(city_df)

    demand = "LOW"
    if count > 10: demand = "HIGH"
    elif count > 5: demand = "MEDIUM"

    action = "Maintain"
    if demand == "HIGH":
        action = "Scale Ads 🚀"
    elif demand == "LOW":
        action = "Discount ⚠"

    cols[i].markdown(f"""
    <div class="card glow">
    <h4>{city}</h4>
    💰 ₹{rev}<br>
    📦 Orders: {count}<br>
    ⚡ Demand: {demand}<br>
    🎯 Action: {action}
    </div>
    """, unsafe_allow_html=True)

# ===============================
# MOMENTUM CHART
# ===============================
st.subheader("📊 Revenue Momentum")

if not df.empty:
    df["min"] = df["time"].dt.strftime("%H:%M")
    chart = df.groupby("min")["price"].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart.index,
        y=chart.values,
        fill='tozeroy',
        line=dict(width=3)
    ))

    st.plotly_chart(fig, use_container_width=True)

# ===============================
# HOT PRODUCTS
# ===============================
st.subheader("🔥 Hot Products")

if not df.empty:
    top = df.groupby("product")["price"].sum().sort_values(ascending=False)
    st.bar_chart(top)

# ===============================
# ALERT ENGINE
# ===============================
st.subheader("🚨 Alerts")

alerts = []

if trend > 5:
    alerts.append(("green","SURGE detected"))
elif trend < -5:
    alerts.append(("red","DROP detected"))

if velocity < 2:
    alerts.append(("yellow","LOW activity"))

for color,msg in alerts:
    st.markdown(f'<div class="alert {color}">{msg}</div>', unsafe_allow_html=True)

# ===============================
# AI COMMAND CENTER
# ===============================
st.subheader("🤖 Decision Engine")

decision = "Stable operations"

if trend > 5:
    decision = "🚀 Increase inventory & ads"
elif trend < -5:
    decision = "⚠ Launch discounts immediately"

st.success(decision)

# ===============================
# LIVE ACTIVITY STREAM (REPLACES TABLE)
# ===============================
st.subheader("📡 Live Activity Stream")

for sale in df.tail(8).iloc[::-1].iterrows():
    s = sale[1]

    tag = ""
    if s["price"] > 30000:
        tag = "🔥 HIGH VALUE"
    elif s["qty"] > 3:
        tag = "📦 BULK"

    st.markdown(f"""
    ⚡ {s['product']} | ₹{s['price']} | {s['city']}  
    <small>{s['time'].strftime("%H:%M:%S")} {tag}</small>
    """)

# ===============================
# AUTO REFRESH
# ===============================
time.sleep(2)
st.rerun()