# ==========================================
# ⚡ REVENUE WAR ROOM — PRO UI (FINAL)
# ==========================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# =========================
# DATA ENGINE
# =========================
PRODUCTS = [
    ("Laptop", 50000, 120000),
    ("Phone", 12000, 80000),
    ("Shoes", 2500, 9000),
    ("Watch", 3000, 25000),
    ("Chair", 7000, 20000),
]

CITIES = ["Hyderabad","Mumbai","Delhi","Bangalore","Chennai"]

ss = st.session_state
ss.setdefault("sales", [])
ss.setdefault("last", 0)

def new_sale(ts=None):
    name, lo, hi = random.choice(PRODUCTS)
    price = random.randint(lo, hi)
    qty = random.choice([1,1,2])
    return {
        "time": ts or datetime.now(),
        "product": name,
        "city": random.choice(CITIES),
        "revenue": price * qty
    }

# seed
if not ss.sales:
    now = datetime.now()
    for _ in range(70):
        ss.sales.append(new_sale(now - timedelta(minutes=random.randint(1,120))))

# live
if time.time() - ss.last > 30:
    ss.sales.append(new_sale())
    ss.last = time.time()

df = pd.DataFrame(ss.sales)
df["time"] = pd.to_datetime(df["time"])

# =========================
# METRICS
# =========================
total = df["revenue"].sum()
orders = len(df)

last_30 = df[df["time"] > datetime.now() - timedelta(minutes=30)]
velocity = len(last_30)

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()

# =========================
# UI SYSTEM
# =========================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at top left, #0f172a, #020617),
        linear-gradient(to bottom, #020617, #020617);
}

/* GLOBAL SPACING */
.block-container {
    padding: 2rem 3rem;
}

/* HERO */
.hero {
    padding:20px;
    border-radius:16px;
    background: linear-gradient(135deg,#020617,#0f172a);
    border:1px solid #1e293b;
}

/* KPI */
.kpi {
    padding:18px;
    border-radius:14px;
    color:white;
    font-weight:600;
    transition:0.3s;
}
.kpi:hover {
    transform: translateY(-5px);
}

.g1 {background:linear-gradient(135deg,#667eea,#764ba2)}
.g2 {background:linear-gradient(135deg,#f093fb,#f5576c)}
.g3 {background:linear-gradient(135deg,#43e97b,#38f9d7)}
.g4 {background:linear-gradient(135deg,#fa709a,#fee140)}

/* PANEL */
.panel {
    background: rgba(255,255,255,0.03);
    border-radius:14px;
    padding:16px;
    border:1px solid rgba(255,255,255,0.06);
}

/* SECTION TITLE */
.sec {
    font-size:12px;
    color:#22d3ee;
    letter-spacing:2px;
    margin-bottom:8px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown(f"""
<div class="hero">
<h2>⚡ REVENUE WAR ROOM</h2>
LIVE ANALYTICS · {orders} ORDERS
</div>
""", unsafe_allow_html=True)

# =========================
# KPI STRIP
# =========================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi g1">Revenue<br><h2>₹{total:,.0f}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi g2">Orders<br><h2>{orders}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi g3">Velocity<br><h2>{velocity}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi g4">Top City<br><h2>{top_city}</h2></div>', unsafe_allow_html=True)

# =========================
# MAIN GRID
# =========================
left, right = st.columns([2,1])

# -------- CHART
with left:
    st.markdown('<div class="sec">REVENUE FLOW</div>', unsafe_allow_html=True)

    df["min"] = df["time"].dt.strftime("%H:%M")
    chart = df.groupby("min")["revenue"].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart.index,
        y=chart.values,
        fill='tozeroy',
        line=dict(width=3)
    ))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

# -------- SIDE PANEL
with right:
    st.markdown('<div class="sec">INSIGHTS</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="panel">
    🔥 Top Product: {top_product}<br>
    🌍 Top City: {top_city}<br>
    ⚡ Orders (30m): {velocity}
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOWER GRID
# =========================
b1,b2 = st.columns([1,1])

# -------- CITY
with b1:
    st.markdown('<div class="sec">CITY PERFORMANCE</div>', unsafe_allow_html=True)

    for city in CITIES:
        rev = df[df["city"]==city]["revenue"].sum()
        st.markdown(f'<div class="panel">{city} — ₹{rev:,.0f}</div>', unsafe_allow_html=True)

# -------- PRODUCTS
with b2:
    st.markdown('<div class="sec">PRODUCT LEADERBOARD</div>', unsafe_allow_html=True)

    top = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    st.bar_chart(top)

# =========================
# AUTO REFRESH
# =========================
time.sleep(5)
st.rerun()