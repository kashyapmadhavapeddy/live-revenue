# ==========================================
# ⚡ REVENUE WAR ROOM — ENTERPRISE VERSION
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
    page_title="⚡ War Room Enterprise",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# DATA MODEL
# ==========================================
PRODUCTS = [
    ("Laptop","Electronics",50000,120000),
    ("Phone","Electronics",12000,80000),
    ("Shoes","Apparel",2500,9000),
    ("Watch","Accessories",3000,25000),
    ("Chair","Furniture",7000,20000),
    ("Desk","Furniture",15000,50000),
]

CITIES = [
    ("Hyderabad","South"),
    ("Mumbai","West"),
    ("Delhi","North"),
    ("Bangalore","South"),
    ("Chennai","South"),
]

# ==========================================
# SESSION STATE
# ==========================================
ss = st.session_state
ss.setdefault("sales", [])
ss.setdefault("oid", 1000)
ss.setdefault("last_add", 0)

# ==========================================
# SALE GENERATOR
# ==========================================
def generate_sale(ts=None):
    name, cat, lo, hi = random.choice(PRODUCTS)
    city, region = random.choice(CITIES)

    price = random.randint(lo, hi)
    qty = random.choices([1,2,3],[60,30,10])[0]

    return {
        "time": ts or datetime.now(),
        "order": f"ORD-{ss.oid}",
        "product": name,
        "category": cat,
        "price": price,
        "qty": qty,
        "city": city,
        "region": region,
        "revenue": price * qty
    }

# ==========================================
# INITIAL SEED
# ==========================================
if not ss.sales:
    now = datetime.now()
    for _ in range(60):
        ss.sales.append(generate_sale(now - timedelta(minutes=random.randint(1,180))))

# ==========================================
# LIVE ADD
# ==========================================
if time.time() - ss.last_add > 30:
    ss.sales.append(generate_sale())
    ss.last_add = time.time()

# ==========================================
# DATAFRAME SAFE
# ==========================================
df = pd.DataFrame(ss.sales)

required_cols = ["order","product","city","revenue","time"]
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
prev_30 = df[
    (df["time"] > now - timedelta(minutes=60)) &
    (df["time"] <= now - timedelta(minutes=30))
]

velocity = len(last_30)
trend = velocity - len(prev_30)

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()
top_region = df.groupby("region")["revenue"].sum().idxmax()

demand_index = min(100, velocity * 3 + max(trend,0)*5)

# ==========================================
# UI DESIGN SYSTEM (CLEAN + CONSISTENT)
# ==========================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#020617,#0f172a);
}

/* HERO */
.hero {
    padding:20px;
    border-bottom:1px solid #1e293b;
}

/* KPI */
.kpi {
    background:#0f172a;
    border:1px solid #1e293b;
    padding:15px;
    border-radius:12px;
}

/* SECTION LABEL */
.sec {
    font-size:12px;
    letter-spacing:2px;
    color:#22d3ee;
    margin-top:20px;
}

/* CARD */
.card {
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:10px;
    padding:12px;
}

.ticker {
    overflow:hidden;
    white-space:nowrap;
}
.ticker span {
    display:inline-block;
    padding-right:40px;
    animation: scroll 25s linear infinite;
}
@keyframes scroll {
    0%{transform:translateX(100%)}
    100%{transform:translateX(-100%)}
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# HERO
# ==========================================
st.markdown(f"""
<div class="hero">
<h2>⚡ REVENUE WAR ROOM ENTERPRISE</h2>
LIVE · {orders} ORDERS · DEMAND INDEX: {demand_index}
</div>
""", unsafe_allow_html=True)

# ==========================================
# KPI ROW
# ==========================================
k1,k2,k3,k4,k5 = st.columns(5)

k1.metric("Revenue", f"₹{total_rev:,.0f}")
k2.metric("Orders", orders)
k3.metric("Velocity", velocity)
k4.metric("Top City", top_city)
k5.metric("Top Product", top_product)

# ==========================================
# TICKER
# ==========================================
tick = "".join([
    f"<span>⚡ {s.get('order','--')} {s.get('product','')} ₹{int(s.get('revenue',0)):,} {s.get('city','')}</span>"
    for s in ss.sales[-12:]
])
st.markdown(f'<div class="ticker">{tick}</div>', unsafe_allow_html=True)

# ==========================================
# MAIN GRID
# ==========================================
left, right = st.columns([2,1])

with left:
    st.markdown('<div class="sec">REVENUE FLOW</div>', unsafe_allow_html=True)

    df["bucket"] = df["time"].dt.floor("10min")
    rt = df.groupby("bucket")["revenue"].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rt.index,y=rt.values,fill='tozeroy'))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="sec">COMMAND PANEL</div>', unsafe_allow_html=True)

    st.progress(demand_index)

    st.info(f"Region Leader: {top_region}")

    if trend > 5:
        st.success("🚀 Surge detected")
    elif trend < -5:
        st.error("⚠ Drop detected")

# ==========================================
# CITY GRID
# ==========================================
st.markdown('<div class="sec">CITY PERFORMANCE</div>', unsafe_allow_html=True)

cols = st.columns(len(CITIES))
for i,(city,_) in enumerate(CITIES):
    rev = df[df["city"]==city]["revenue"].sum()
    cols[i].metric(city, f"₹{rev:,.0f}")

# ==========================================
# PRODUCT MOMENTUM
# ==========================================
st.markdown('<div class="sec">PRODUCT MOMENTUM</div>', unsafe_allow_html=True)

pm = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(pm)

# ==========================================
# AUTO REFRESH
# ==========================================
time.sleep(5)
st.rerun()