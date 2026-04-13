# ==========================================
# ⚡ REVENUE WAR ROOM — CLEAN PREMIUM UI
# ==========================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ================= CONFIG =================
st.set_page_config(layout="wide", page_title="⚡ War Room")

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
def new_sale(ts=None):
    name, lo, hi = random.choice(PRODUCTS)
    price = random.randint(lo, hi)
    qty = random.choice([1,1,2])

    return {
        "order": f"ORD-{ss.oid}",
        "product": name,
        "city": random.choice(CITIES),
        "price": price,
        "qty": qty,
        "revenue": price * qty,
        "time": ts or datetime.now()
    }

# ================= SEED =================
if not ss.sales:
    now = datetime.now()
    for _ in range(50):
        ss.sales.append(new_sale(now - timedelta(minutes=random.randint(1,120))))

# ================= LIVE UPDATE =================
if time.time() - ss.last > 30:
    ss.sales.append(new_sale())
    ss.last = time.time()

# ================= DATAFRAME =================
df = pd.DataFrame(ss.sales)

if df.empty:
    df = pd.DataFrame(columns=["order","product","city","revenue","time"])

df["time"] = pd.to_datetime(df["time"])

# ================= METRICS =================
total = df["revenue"].sum()
orders = len(df)

last_30 = df[df["time"] > datetime.now() - timedelta(minutes=30)]
velocity = len(last_30)

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()

# ================= UI CSS =================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at top left, #0f172a, #020617),
        repeating-linear-gradient(
            0deg,
            rgba(255,255,255,0.02),
            rgba(255,255,255,0.02) 1px,
            transparent 1px,
            transparent 40px
        );
}

/* KPI */
.kpi {
    padding:18px;
    border-radius:14px;
    color:white;
    font-weight:600;
}
.g1 {background:linear-gradient(135deg,#667eea,#764ba2)}
.g2 {background:linear-gradient(135deg,#f093fb,#f5576c)}
.g3 {background:linear-gradient(135deg,#43e97b,#38f9d7)}
.g4 {background:linear-gradient(135deg,#fa709a,#fee140)}

/* CARD */
.card {
    background:rgba(255,255,255,0.04);
    border-radius:14px;
    padding:15px;
    border:1px solid rgba(255,255,255,0.08);
}

/* SECTION */
.section {
    margin-top:20px;
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

# ================= MAIN GRID =================
left, right = st.columns([2,1])

# -------- CHART
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

# -------- INSIGHT PANEL
with right:
    st.markdown("### Insights")

    st.markdown(f"""
    <div class="card">
    🔥 Top City: {top_city}<br>
    🏆 Best Product: {top_product}<br>
    ⚡ Orders (30m): {velocity}
    </div>
    """, unsafe_allow_html=True)

# ================= CITY GRID =================
st.markdown("### 🌍 Cities")

cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    rev = df[df["city"]==city]["revenue"].sum()

    cols[i].markdown(f"""
    <div class="card">
    <b>{city}</b><br>
    ₹{rev:,.0f}
    </div>
    """, unsafe_allow_html=True)

# ================= PRODUCT =================
st.markdown("### 🔥 Products")

top = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(top)

# ================= AUTO REFRESH =================
time.sleep(5)
st.rerun()