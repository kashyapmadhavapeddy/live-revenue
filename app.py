import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="⚡ Analytics War Room")

# =========================
# REAL DATA
# =========================
PRODUCTS = [
    ("Laptop", 40000, 90000),
    ("Phone", 10000, 60000),
    ("Shoes", 2000, 8000),
    ("Watch", 3000, 25000),
    ("Chair", 6000, 20000),
]

CITIES = ["Hyderabad","Mumbai","Delhi","Bangalore","Chennai"]

# =========================
# SESSION
# =========================
if "sales" not in st.session_state:
    st.session_state.sales = []
if "last" not in st.session_state:
    st.session_state.last = time.time()

def generate_sale():
    p, lo, hi = random.choice(PRODUCTS)
    return {
        "time": datetime.now(),
        "product": p,
        "city": random.choice(CITIES),
        "price": random.randint(lo, hi)
    }

# 30 sec logic
if time.time() - st.session_state.last > 30:
    st.session_state.sales.append(generate_sale())
    st.session_state.last = time.time()

df = pd.DataFrame(st.session_state.sales)

if df.empty:
    df = pd.DataFrame(columns=["time","product","city","price"])

if not df.empty:
    df["time"] = pd.to_datetime(df["time"])

# =========================
# METRICS
# =========================
total = df["price"].sum()
orders = len(df)

velocity = len(df[df["time"] > datetime.now() - timedelta(minutes=5)])

top_city = df.groupby("city")["price"].sum().idxmax() if not df.empty else "-"

# =========================
# UI STYLE (MAIN MAGIC)
# =========================
st.markdown("""
<style>
body {background:#0b1020;color:white}

/* KPI CARDS */
.kpi {
    padding:18px;
    border-radius:14px;
    color:white;
    font-weight:600;
}
.kpi h3 {margin:0;font-size:14px;opacity:0.8}
.kpi h1 {margin:5px 0;font-size:26px}

/* gradients */
.g1 {background:linear-gradient(135deg,#667eea,#764ba2)}
.g2 {background:linear-gradient(135deg,#f093fb,#f5576c)}
.g3 {background:linear-gradient(135deg,#43e97b,#38f9d7)}
.g4 {background:linear-gradient(135deg,#fa709a,#fee140)}

.card {
    background:#121a33;
    padding:15px;
    border-radius:12px;
    border:1px solid #1e293b;
}

/* transaction card */
.tx {
    background:#121a33;
    padding:10px;
    border-radius:10px;
    margin-bottom:8px;
    border-left:4px solid #22d3ee;
}
</style>
""", unsafe_allow_html=True)

# =========================
# KPI ROW (GRADIENT)
# =========================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi g1"><h3>Revenue</h3><h1>₹{total:,.0f}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi g2"><h3>Orders</h3><h1>{orders}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi g3"><h3>Velocity</h3><h1>{velocity}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi g4"><h3>Top City</h3><h1>{top_city}</h1></div>', unsafe_allow_html=True)

# =========================
# MAIN GRID
# =========================
left, right = st.columns([2,1])

# -------- CHART
with left:
    st.markdown("### Revenue")

    if not df.empty:
        df["min"] = df["time"].dt.strftime("%H:%M")
        chart = df.groupby("min")["price"].sum()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=chart.index,
            y=chart.values
        ))

        fig.update_layout(
            plot_bgcolor="#121a33",
            paper_bgcolor="#121a33",
            font=dict(color="white")
        )

        st.plotly_chart(fig, use_container_width=True)

# -------- INSIGHTS PANEL
with right:
    st.markdown("### Insights")

    st.markdown("""
    <div class="card">
    🔥 Demand rising in Bangalore<br>
    ⚡ Mumbai stable<br>
    ⚠ Delhi needs promotion
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOWER GRID
# =========================
b1, b2 = st.columns([1,1])

# ---- CITY CARDS
with b1:
    st.markdown("### Cities")

    for city in CITIES:
        rev = df[df["city"] == city]["price"].sum()
        st.markdown(f"""
        <div class="card">
        {city} — ₹{rev:,.0f}
        </div>
        """, unsafe_allow_html=True)

# ---- TRANSACTIONS
with b2:
    st.markdown("### Transactions")

    for _, s in df.tail(5).iloc[::-1].iterrows():
        st.markdown(f"""
        <div class="tx">
        {s['product']} — ₹{s['price']:,.0f} ({s['city']})
        </div>
        """, unsafe_allow_html=True)

# =========================
# AUTO REFRESH
# =========================
time.sleep(5)
st.rerun()