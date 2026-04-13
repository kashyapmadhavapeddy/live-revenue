import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ================= CONFIG =================
st.set_page_config(layout="wide", page_title="⚡ War Room X")

# ================= DATA =================
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
ss.setdefault("oid", 1000)

# ================= GENERATOR =================
def new_sale():
    name, lo, hi = random.choice(PRODUCTS)
    price = random.randint(lo, hi)
    return {
        "order": f"ORD-{ss.oid}",
        "product": name,
        "city": random.choice(CITIES),
        "revenue": price,
        "time": datetime.now()
    }

if not ss.sales:
    for _ in range(50):
        ss.sales.append(new_sale())

if time.time() - ss.last > 30:
    ss.sales.append(new_sale())
    ss.last = time.time()

# ================= DF =================
df = pd.DataFrame(ss.sales)

if df.empty:
    df = pd.DataFrame(columns=["order","product","city","revenue","time"])

df["time"] = pd.to_datetime(df["time"])

# ================= METRICS =================
total = df["revenue"].sum()
orders = len(df)

recent = df[df["time"] > datetime.now() - timedelta(minutes=30)]
velocity = len(recent)

trend = velocity - len(df[(df["time"] > datetime.now()-timedelta(minutes=60)) &
                          (df["time"] <= datetime.now()-timedelta(minutes=30))])

top_city = df.groupby("city")["revenue"].sum().idxmax()

demand = min(100, velocity * 3 + max(trend,0)*5)

# ================= UI CSS (EXTREME) =================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at 30% 20%, #1e293b, #020617);
}

/* KPI */
.kpi {
    padding:20px;
    border-radius:16px;
    background:rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border:1px solid rgba(255,255,255,0.1);
    transition:0.3s;
}
.kpi:hover {
    transform: translateY(-6px);
    box-shadow:0 20px 40px rgba(0,0,0,0.6);
}

/* PANEL */
.panel {
    background:rgba(255,255,255,0.04);
    border-radius:16px;
    padding:15px;
    border:1px solid rgba(255,255,255,0.08);
}

/* GLOW ANIMATION */
.glow {
    animation: glow 2s infinite alternate;
}
@keyframes glow {
    from {box-shadow:0 0 5px #22d3ee33;}
    to {box-shadow:0 0 20px #22d3ee88;}
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("## ⚡ REVENUE WAR ROOM X")

# ================= KPI =================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi glow">💰 Revenue<br><h2>₹{total:,.0f}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi">📦 Orders<br><h2>{orders}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi">⚡ Velocity<br><h2>{velocity}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi">🏆 Top City<br><h2>{top_city}</h2></div>', unsafe_allow_html=True)

# ================= GRID =================
left, right = st.columns([2,1])

# -------- CHART
with left:
    st.markdown("### 📊 Revenue Flow")

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

# -------- COMMAND RADAR (NEW FEATURE)
with right:
    st.markdown("### 🧠 Command Radar")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=demand,
        title={'text': "Demand Index"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "cyan"}
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    if demand > 70:
        st.success("🚀 SCALE NOW")
    elif demand > 30:
        st.warning("⚡ MONITOR")
    else:
        st.error("⚠ BOOST SALES")

# ================= CITY GRID =================
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

# ================= AUTO REFRESH =================
time.sleep(5)
st.rerun()