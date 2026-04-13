import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ===============================
# CONFIG
# ===============================
st.set_page_config(layout="wide", page_title="⚡ War Room")

PRODUCTS = ["Laptop","Shoes","Watch","Phone","Bag","Tablet","Chair"]
CITIES = ["Hyderabad","Mumbai","Delhi","Bangalore","Chennai"]

# ===============================
# SESSION
# ===============================
if "sales" not in st.session_state:
    st.session_state.sales = []
if "last" not in st.session_state:
    st.session_state.last = time.time()

# ===============================
# GENERATE SALE (30 SEC)
# ===============================
def generate_sale():
    return {
        "time": datetime.now(),
        "product": random.choice(PRODUCTS),
        "city": random.choice(CITIES),
        "price": random.randint(2000,50000),
        "qty": random.randint(1,5)
    }

if time.time() - st.session_state.last > 30:
    st.session_state.sales.append(generate_sale())
    st.session_state.last = time.time()

# ===============================
# DATAFRAME FIX
# ===============================
df = pd.DataFrame(st.session_state.sales)

if df.empty:
    df = pd.DataFrame(columns=["time","product","city","price","qty"])

if not df.empty:
    df["time"] = pd.to_datetime(df["time"])

# ===============================
# METRICS
# ===============================
total_rev = df["price"].sum()
orders = len(df)

last_5m = df[df["time"] > datetime.now() - timedelta(minutes=5)]
velocity = len(last_5m)

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
.title {
    font-size:28px;
    font-weight:bold;
}
.glow {box-shadow:0 0 15px #22d3ee22}
</style>
""", unsafe_allow_html=True)

# ===============================
# HERO
# ===============================
st.markdown('<div class="title">⚡ REVENUE WAR ROOM</div>', unsafe_allow_html=True)

# ===============================
# KPI ROW
# ===============================
c1,c2,c3,c4 = st.columns(4)
c1.metric("💰 Revenue", f"₹{total_rev:,.0f}")
c2.metric("📦 Orders", orders)
c3.metric("⚡ 5m Velocity", velocity)

top_city = df.groupby("city")["price"].sum().idxmax() if not df.empty else "-"
c4.metric("🏆 Top City", top_city)

# ===============================
# MAIN GRID
# ===============================
left, right = st.columns([2,1])

# ---------------- LEFT (CHART)
with left:
    st.markdown("### 📊 Revenue Timeline")

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

# ---------------- RIGHT (PULSE + DECISION)
with right:
    st.markdown("### 🎯 Demand Pulse")

    intensity = min(velocity * 10, 100)
    st.progress(intensity)

    if intensity > 70:
        st.success("🔥 HIGH")
    elif intensity > 30:
        st.warning("⚡ MEDIUM")
    else:
        st.error("❄ LOW")

    st.markdown("### 🤖 Decision")

    if intensity > 70:
        st.success("Scale Ads + Inventory")
    elif intensity < 20:
        st.warning("Run Discounts")

# ===============================
# CITY GRID
# ===============================
st.markdown("### 🌍 City War Grid")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    city_df = df[df["city"] == city]

    rev = city_df["price"].sum()
    count = len(city_df)

    cols[i].markdown(f"""
    <div class="card glow">
    <b>{city}</b><br>
    ₹{rev:,.0f}<br>
    Orders: {count}
    </div>
    """, unsafe_allow_html=True)

# ===============================
# BOTTOM GRID
# ===============================
b1, b2 = st.columns(2)

# -------- HOT PRODUCTS
with b1:
    st.markdown("### 🔥 Hot Products")

    if not df.empty:
        top = df.groupby("product")["price"].sum().sort_values(ascending=False)
        st.bar_chart(top)

# -------- LIVE STREAM
with b2:
    st.markdown("### 📡 Live Feed")

    for _, s in df.tail(6).iloc[::-1].iterrows():
        st.markdown(f"⚡ {s['product']} | ₹{s['price']} | {s['city']}")

# ===============================
# AUTO REFRESH
# ===============================
time.sleep(5)
st.rerun()