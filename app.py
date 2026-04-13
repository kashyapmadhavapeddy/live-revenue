# ==========================================
# ⚡ REVENUE WAR ROOM — FINAL ULTRA VERSION
# ==========================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="⚡ Revenue War Room Ultra",
    initial_sidebar_state="collapsed"
)

# ==========================================
# DATA (REALISTIC)
# ==========================================
PRODUCTS = [
    ("Laptop", 50000, 120000),
    ("Phone", 12000, 80000),
    ("Shoes", 2500, 9000),
    ("Watch", 3000, 25000),
    ("Chair", 7000, 20000),
    ("Desk", 15000, 50000),
]

CITIES = ["Hyderabad","Mumbai","Delhi","Bangalore","Chennai"]

# ==========================================
# SESSION STATE
# ==========================================
ss = st.session_state
ss.setdefault("sales", [])
ss.setdefault("last_add", 0)
ss.setdefault("oid", 1000)

# CLEAN DATA (NO CRASH)
ss.sales = [s for s in ss.sales if isinstance(s, dict)]

# ==========================================
# SALE GENERATOR
# ==========================================
def new_sale(ts=None):
    name, lo, hi = random.choice(PRODUCTS)
    price = random.randint(lo, hi)
    qty = random.choices([1,2,3], [60,30,10])[0]

    return {
        "order": f"ORD-{ss.oid}",
        "product": name,
        "city": random.choice(CITIES),
        "price": price,
        "qty": qty,
        "revenue": price * qty,
        "time": ts or datetime.now()
    }

# ==========================================
# INITIAL DATA
# ==========================================
if not ss.sales:
    now = datetime.now()
    for _ in range(60):
        ss.sales.append(new_sale(now - timedelta(minutes=random.randint(1,120))))

# ==========================================
# LIVE UPDATE (30s)
# ==========================================
if time.time() - ss.last_add > 30:
    ss.sales.append(new_sale())
    ss.last_add = time.time()

# ==========================================
# DATAFRAME SAFE
# ==========================================
df = pd.DataFrame(ss.sales)

required_cols = ["order","product","city","price","qty","revenue","time"]
for col in required_cols:
    if col not in df.columns:
        df[col] = None

df["time"] = pd.to_datetime(df["time"])

# ==========================================
# METRICS
# ==========================================
now = datetime.now()

total_rev = df["revenue"].sum()
orders = len(df)

last_30 = df[df["time"] > now - timedelta(minutes=30)]
prev_30 = df[(df["time"] > now - timedelta(minutes=60)) &
             (df["time"] <= now - timedelta(minutes=30))]

velocity = len(last_30)
trend = velocity - len(prev_30)

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()

demand = min(100, velocity * 3 + max(trend,0)*5)

# ==========================================
# UI STYLE (FULL SYSTEM)
# ==========================================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at 20% 20%, #1e293b, #020617),
        repeating-linear-gradient(
            0deg,
            rgba(255,255,255,0.02),
            rgba(255,255,255,0.02) 1px,
            transparent 1px,
            transparent 40px
        ),
        repeating-linear-gradient(
            90deg,
            rgba(255,255,255,0.02),
            rgba(255,255,255,0.02) 1px,
            transparent 1px,
            transparent 40px
        );
}

/* KPI */
.kpi {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    padding:18px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.08);
    transition:0.3s;
}
.kpi:hover {
    transform: translateY(-5px);
}

/* LIVE DOT */
.live-dot {
    width:8px;height:8px;
    background:#22c55e;
    border-radius:50%;
    display:inline-block;
    animation: blink 1.5s infinite;
}
@keyframes blink {
    0%,100%{opacity:1}
    50%{opacity:0.2}
}

/* PANELS */
.panel {
    background: rgba(255,255,255,0.03);
    padding:15px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.06);
}

/* GLOW */
.glow {
    animation: glow 2s infinite alternate;
}
@keyframes glow {
    from {box-shadow:0 0 5px #22d3ee33;}
    to {box-shadow:0 0 20px #22d3ee88;}
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================
st.markdown("## ⚡ REVENUE WAR ROOM ULTRA")

# ==========================================
# KPI ROW
# ==========================================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi glow">💰 Revenue <span class="live-dot"></span><h2>₹{total_rev:,.0f}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi">📦 Orders<h2>{orders}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi">⚡ Velocity<h2>{velocity}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi">🏆 Top City<h2>{top_city}</h2></div>', unsafe_allow_html=True)

# ==========================================
# MAIN GRID
# ==========================================
left, right = st.columns([2,1])

# -------- CHART
with left:
    st.markdown("### 📊 Revenue Flow")

    df["bucket"] = df["time"].dt.floor("10min")
    rt = df.groupby("bucket")["revenue"].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rt.index,
        y=rt.values,
        fill='tozeroy',
        line=dict(width=3)
    ))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

# -------- COMMAND PANEL
with right:
    st.markdown("### 🧠 Command Radar")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=demand,
        title={'text': "Demand"},
        gauge={'axis': {'range': [0, 100]}}
    ))
    st.plotly_chart(fig, use_container_width=True)

    if demand > 70:
        st.success("🚀 SCALE NOW")
    elif demand > 30:
        st.warning("⚡ MONITOR")
    else:
        st.error("⚠ BOOST SALES")

# ==========================================
# ANOMALY DETECTOR (BEST FEATURE)
# ==========================================
st.markdown("### 🧠 Anomaly Detector")

alerts = []

if trend > 8:
    alerts.append("🚀 Revenue Surge")
elif trend < -5:
    alerts.append("⚠ Revenue Drop")

city_rev = df.groupby("city")["revenue"].sum()
if city_rev.max() > city_rev.mean()*1.8:
    alerts.append(f"🌍 {city_rev.idxmax()} dominating")

prod_rev = df.groupby("product")["revenue"].sum()
if prod_rev.max() > prod_rev.mean()*2:
    alerts.append(f"📈 {prod_rev.idxmax()} breakout")

for a in alerts:
    st.markdown(f'<div class="panel glow">{a}</div>', unsafe_allow_html=True)

# ==========================================
# CITY GRID
# ==========================================
st.markdown("### 🌍 City Command")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    rev = df[df["city"]==city]["revenue"].sum()

    cols[i].markdown(f"""
    <div class="panel">
    <b>{city}</b><br>
    ₹{rev:,.0f}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# AUTO REFRESH
# ==========================================
time.sleep(5)
st.rerun()