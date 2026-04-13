import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(layout="wide", page_title="⚡ War Room Ultra")

# ==========================================
# PRODUCTS (REALISTIC)
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
# SESSION
# ==========================================
ss = st.session_state
ss.setdefault("sales", [])
ss.setdefault("last", 0)
ss.setdefault("oid", 1000)

# CLEAN OLD DATA
ss.sales = [s for s in ss.sales if isinstance(s, dict)]

# ==========================================
# SALE GENERATOR
# ==========================================
def new_sale():
    name, lo, hi = random.choice(PRODUCTS)
    price = random.randint(lo, hi)
    qty = random.choice([1,1,1,2])
    return {
        "order": f"ORD-{ss.oid}",
        "product": name,
        "city": random.choice(CITIES),
        "price": price,
        "qty": qty,
        "revenue": price * qty,
        "time": datetime.now()
    }

# SEED
if not ss.sales:
    for _ in range(40):
        ss.sales.append(new_sale())

# ADD EVERY 30 SEC
if time.time() - ss.last > 30:
    ss.sales.append(new_sale())
    ss.last = time.time()

# ==========================================
# DATAFRAME SAFE
# ==========================================
df = pd.DataFrame(ss.sales)

required = ["order","product","city","price","qty","revenue","time"]
for col in required:
    if col not in df.columns:
        df[col] = None

df["time"] = pd.to_datetime(df["time"])

# ==========================================
# METRICS
# ==========================================
total = df["revenue"].sum()
orders = len(df)

recent = df[df["time"] > datetime.now() - timedelta(minutes=30)]
velocity = len(recent)

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()

demand = min(100, velocity * 3)

# ==========================================
# UI CSS (ULTRA)
# ==========================================
st.markdown("""
<style>

body {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color:white;
}

/* KPI CARDS */
.kpi {
    padding:18px;
    border-radius:16px;
    color:white;
    font-weight:600;
    transition:0.3s;
}
.kpi:hover {
    transform: translateY(-5px);
    box-shadow:0 10px 25px rgba(0,0,0,0.5);
}

/* gradients */
.g1 {background:linear-gradient(135deg,#667eea,#764ba2)}
.g2 {background:linear-gradient(135deg,#f093fb,#f5576c)}
.g3 {background:linear-gradient(135deg,#43e97b,#38f9d7)}
.g4 {background:linear-gradient(135deg,#fa709a,#fee140)}
.g5 {background:linear-gradient(135deg,#30cfd0,#330867)}

.card {
    background:rgba(15,23,42,0.7);
    backdrop-filter: blur(10px);
    padding:15px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.05);
}

/* ticker */
.ticker {
    overflow:hidden;
    white-space:nowrap;
}
.ticker span {
    display:inline-block;
    padding-right:50px;
    animation: scroll 20s linear infinite;
}
@keyframes scroll {
    0% {transform:translateX(100%)}
    100% {transform:translateX(-100%)}
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

# ==========================================
# HERO
# ==========================================
st.markdown("## ⚡ REVENUE WAR ROOM ULTRA")

# ==========================================
# KPI ROW
# ==========================================
c1,c2,c3,c4,c5 = st.columns(5)

c1.markdown(f'<div class="kpi g1">Revenue<br><h2>₹{total:,.0f}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi g2">Orders<br><h2>{orders}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi g3">Velocity<br><h2>{velocity}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi g4">Top City<br><h2>{top_city}</h2></div>', unsafe_allow_html=True)
c5.markdown(f'<div class="kpi g5">Top Product<br><h2>{top_product}</h2></div>', unsafe_allow_html=True)

# ==========================================
# TICKER
# ==========================================
tick = "".join([
    f"<span>⚡ {s['order']} {s['product']} ₹{s['revenue']:,} {s['city']}</span>"
    for s in ss.sales[-8:]
])
st.markdown(f'<div class="ticker">{tick}</div>', unsafe_allow_html=True)

# ==========================================
# MAIN GRID
# ==========================================
left, right = st.columns([2,1])

with left:
    st.markdown("### Revenue Flow")

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

with right:
    st.markdown("### Demand")

    st.progress(demand)

    if demand > 70:
        st.success("HIGH DEMAND")
    elif demand > 30:
        st.warning("MODERATE")
    else:
        st.error("LOW")

# ==========================================
# CITY GRID
# ==========================================
st.markdown("### 🌍 City Command")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    rev = df[df["city"]==city]["revenue"].sum()

    cols[i].markdown(f"""
    <div class="card">
    <b>{city}</b><br>
    ₹{rev:,.0f}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# PRODUCT LEADERBOARD
# ==========================================
st.markdown("### 🔥 Product Leaderboard")

top = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(top)

# ==========================================
# AUTO REFRESH
# ==========================================
time.sleep(5)
st.rerun()