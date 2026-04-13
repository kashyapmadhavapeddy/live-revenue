import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ===============================
# CONFIG
# ===============================
st.set_page_config(layout="wide", page_title="⚡ War Room Pro")

# REALISTIC PRODUCTS
PRODUCTS = [
    ("Laptop", 40000, 90000),
    ("Phone", 10000, 60000),
    ("Shoes", 2000, 8000),
    ("Watch", 3000, 25000),
    ("Chair", 6000, 20000),
    ("Bag", 1500, 6000),
    ("Tablet", 15000, 50000),
]

CITIES = ["Hyderabad","Mumbai","Delhi","Bangalore","Chennai"]

# ===============================
# SESSION
# ===============================
if "sales" not in st.session_state:
    st.session_state.sales = []
if "last" not in st.session_state:
    st.session_state.last = time.time()

# ===============================
# GENERATE REALISTIC SALE
# ===============================
def generate_sale():
    product, lo, hi = random.choice(PRODUCTS)
    price = random.randint(lo, hi)
    return {
        "time": datetime.now(),
        "product": product,
        "city": random.choice(CITIES),
        "price": price,
        "qty": random.randint(1,3)
    }

# ADD EVERY 30s
if time.time() - st.session_state.last > 30:
    st.session_state.sales.append(generate_sale())
    st.session_state.last = time.time()

# ===============================
# DATAFRAME SAFE
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
# UI STYLE (UPGRADED)
# ===============================
st.markdown("""
<style>
body {background:#020617;color:white}

.kpi {
    background:#0f172a;
    padding:15px;
    border-radius:12px;
    border:1px solid #1e293b;
    box-shadow:0 0 10px #22d3ee22;
    animation: glow 2s infinite alternate;
}
@keyframes glow {
    from {box-shadow:0 0 5px #22d3ee22;}
    to {box-shadow:0 0 15px #22d3ee66;}
}

.card {
    background:#0f172a;
    border-radius:12px;
    padding:15px;
    border:1px solid #1e293b;
}

.tag {
    background:#22d3ee;
    color:black;
    padding:3px 8px;
    border-radius:6px;
    font-size:10px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.title("⚡ REVENUE WAR ROOM PRO")

# ===============================
# KPI ROW
# ===============================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi">💰 Revenue<br><b>₹{total_rev:,.0f}</b></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi">📦 Orders<br><b>{orders}</b></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi">⚡ Velocity<br><b>{velocity}</b></div>', unsafe_allow_html=True)

top_city = df.groupby("city")["price"].sum().idxmax() if not df.empty else "-"
c4.markdown(f'<div class="kpi">🏆 Top City<br><b>{top_city}</b></div>', unsafe_allow_html=True)

# ===============================
# MAIN GRID
# ===============================
left, right = st.columns([2,1])

# -------- CHART
with left:
    st.subheader("📊 Revenue Timeline")

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

# -------- SIDE PANEL
with right:
    st.subheader("🎯 Demand Status")

    intensity = min(velocity * 10, 100)
    st.progress(intensity)

    if intensity > 70:
        st.success("🔥 HIGH DEMAND")
    elif intensity > 30:
        st.warning("⚡ MEDIUM")
    else:
        st.error("❄ LOW")

    st.subheader("🤖 Action")

    if intensity > 70:
        st.success("Scale Ads + Inventory")
    else:
        st.warning("Run Promotions")

# ===============================
# CITY GRID
# ===============================
st.subheader("🌍 City Command")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    city_df = df[df["city"] == city]

    rev = city_df["price"].sum()

    cols[i].markdown(f"""
    <div class="card">
    <b>{city}</b><br>
    ₹{rev:,.0f}
    </div>
    """, unsafe_allow_html=True)

# ===============================
# TRANSACTION CARDS (REPLACED FEED)
# ===============================
st.subheader("💳 Recent Transactions")

for _, s in df.tail(5).iloc[::-1].iterrows():
    tag = ""

    if s["price"] > 40000:
        tag = '<span class="tag">HIGH VALUE</span>'

    st.markdown(f"""
    <div class="card">
    ⚡ {s['product']} — ₹{s['price']:,.0f} ({s['city']}) {tag}
    </div>
    """, unsafe_allow_html=True)

# ===============================
# AUTO REFRESH
# ===============================
time.sleep(5)
st.rerun()