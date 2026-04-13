# ==========================================
# ⚡ WAR ROOM — EXTREME UI MODE
# ==========================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

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
    for _ in range(80):
        ss.sales.append(new_sale(now - timedelta(minutes=random.randint(1,120))))

# live
if time.time() - ss.last > 30:
    ss.sales.append(new_sale())
    ss.last = time.time()

df = pd.DataFrame(ss.sales)
df["time"] = pd.to_datetime(df["time"])

# ================= METRICS =================
total = df["revenue"].sum()
orders = len(df)

last_30 = df[df["time"] > datetime.now() - timedelta(minutes=30)]
velocity = len(last_30)

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()

# ================= UI =================
st.markdown("""
<style>

/* BACKGROUND ANIMATION */
.stApp {
    background: radial-gradient(circle at center, #0f172a, #020617);
}

/* CORE */
.core {
    text-align:center;
    padding:40px;
    border-radius:20px;
    border:1px solid #22d3ee33;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% {box-shadow:0 0 10px #22d3ee44;}
    50% {box-shadow:0 0 40px #22d3eeaa;}
    100% {box-shadow:0 0 10px #22d3ee44;}
}

/* KPI */
.kpi {
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:12px;
    padding:15px;
    text-align:center;
}

/* PANEL */
.panel {
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;
    padding:15px;
}

</style>
""", unsafe_allow_html=True)

# ================= CORE =================
st.markdown(f"""
<div class="core">
<h1>₹{total:,.0f}</h1>
<p>LIVE REVENUE CORE</p>
</div>
""", unsafe_allow_html=True)

# ================= KPI =================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi">Orders<br><h3>{orders}</h3></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi">Velocity<br><h3>{velocity}</h3></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi">Top City<br><h3>{top_city}</h3></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi">Top Product<br><h3>{top_product}</h3></div>', unsafe_allow_html=True)

# ================= GRID =================
left, right = st.columns([2,1])

# chart
with left:
    df["min"] = df["time"].dt.strftime("%H:%M")
    chart = df.groupby("min")["revenue"].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=chart.index,y=chart.values,fill='tozeroy'))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

# insights
with right:
    st.markdown(f"""
    <div class="panel">
    🔥 {top_product} trending<br>
    🌍 {top_city} leading<br>
    ⚡ {velocity} recent orders
    </div>
    """, unsafe_allow_html=True)

# ================= AUTO =================
time.sleep(5)
st.rerun()