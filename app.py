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
    for _ in range(30):
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
velocity = len(df[df["time"] > datetime.now() - timedelta(minutes=10)])

top_city = df.groupby("city")["revenue"].sum().idxmax()

# ================= ULTRA CSS =================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: radial-gradient(circle at 20% 20%, #1e293b, #020617);
}

/* GRID SPACING */
.block-container {
    padding: 2rem 3rem;
}

/* KPI CARDS */
.kpi {
    border-radius: 16px;
    padding: 18px;
    color: white;
    font-weight: 600;
    transition: 0.3s;
}
.kpi:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
}

/* GRADIENTS */
.g1 {background: linear-gradient(135deg,#667eea,#764ba2);}
.g2 {background: linear-gradient(135deg,#f093fb,#f5576c);}
.g3 {background: linear-gradient(135deg,#43e97b,#38f9d7);}
.g4 {background: linear-gradient(135deg,#fa709a,#fee140);}

/* GLASS CARD */
.card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 16px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* TICKER */
.ticker {
    overflow:hidden;
    white-space:nowrap;
    padding:10px;
}
.ticker span {
    display:inline-block;
    padding-right:50px;
    animation: scroll 15s linear infinite;
}
@keyframes scroll {
    0% {transform:translateX(100%)}
    100% {transform:translateX(-100%)}
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("## ⚡ REVENUE WAR ROOM")

# ================= KPI =================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi g1">Revenue<br><h2>₹{total:,.0f}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi g2">Orders<br><h2>{orders}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi g3">Velocity<br><h2>{velocity}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi g4">Top City<br><h2>{top_city}</h2></div>', unsafe_allow_html=True)

# ================= TICKER =================
tick = "".join([
    f"<span>⚡ {s.get('order','--')} {s.get('product','')} ₹{int(s.get('revenue',0)):,} {s.get('city','')}</span>"
    for s in ss.sales[-10:]
])
st.markdown(f'<div class="ticker">{tick}</div>', unsafe_allow_html=True)

# ================= GRID =================
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
    st.markdown("### Insights")

    st.markdown("""
    <div class="card">
    🔥 Demand rising<br>
    ⚡ Stable flow<br>
    ⚠ Monitor low zones
    </div>
    """, unsafe_allow_html=True)

# ================= CITY GRID =================
st.markdown("### 🌍 City Performance")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    rev = df[df["city"]==city]["revenue"].sum()

    cols[i].markdown(f"""
    <div class="card">
    <b>{city}</b><br>
    ₹{rev:,.0f}
    </div>
    """, unsafe_allow_html=True)

# ================= AUTO REFRESH =================
time.sleep(5)
st.rerun()