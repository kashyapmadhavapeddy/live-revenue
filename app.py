import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, time
from datetime import datetime, timedelta

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(layout="wide", page_title="⚡ Revenue War Room X")

# ==========================================
# REALISTIC PRODUCTS
# ==========================================
PRODUCTS = [
    ("Laptop", "Electronics", 45000, 90000),
    ("Phone", "Electronics", 12000, 70000),
    ("Headphones", "Electronics", 2000, 12000),
    ("Shoes", "Apparel", 2500, 9000),
    ("Jacket", "Apparel", 3000, 12000),
    ("Chair", "Furniture", 7000, 22000),
    ("Desk", "Furniture", 12000, 45000),
    ("Watch", "Accessories", 3000, 25000),
]

CITIES = [
    ("Hyderabad","South"),
    ("Mumbai","West"),
    ("Delhi","North"),
    ("Bangalore","South"),
    ("Chennai","South"),
]

# ==========================================
# SESSION
# ==========================================
ss = st.session_state
ss.setdefault("sales", [])
ss.setdefault("last_add", 0)
ss.setdefault("oid", 1000)

# ==========================================
# SALE GENERATOR (REALISTIC)
# ==========================================
def new_sale(ts=None):
    name, cat, lo, hi = random.choice(PRODUCTS)
    city, region = random.choice(CITIES)

    qty = random.choices([1,2,3], weights=[60,30,10])[0]
    price = random.randint(lo, hi)

    revenue = price * qty

    sale = {
        "time": ts or datetime.now(),
        "order": f"ORD-{ss.oid}",
        "product": name,
        "category": cat,
        "price": price,
        "qty": qty,
        "city": city,
        "region": region,
        "revenue": revenue
    }

    ss.oid += 1
    return sale

# ==========================================
# SEED HISTORY
# ==========================================
if not ss.sales:
    now = datetime.now()
    for _ in range(50):
        ts = now - timedelta(minutes=random.randint(1,120))
        ss.sales.append(new_sale(ts))

# ==========================================
# ADD EVERY 30 SEC
# ==========================================
if time.time() - ss.last_add > 30:
    ss.sales.append(new_sale())
    ss.last_add = time.time()

# ==========================================
# DATAFRAME
# ==========================================
df = pd.DataFrame(ss.sales)

if not df.empty:
    df["time"] = pd.to_datetime(df["time"])

# ==========================================
# METRICS
# ==========================================
total_rev = df["revenue"].sum()
orders = len(df)

now = datetime.now()

last_30m = df[df["time"] > now - timedelta(minutes=30)]
velocity = len(last_30m)

prev_30m = df[
    (df["time"] > now - timedelta(minutes=60)) &
    (df["time"] <= now - timedelta(minutes=30))
]

trend = (len(last_30m) - len(prev_30m))

top_city = df.groupby("city")["revenue"].sum().idxmax()
top_product = df.groupby("product")["revenue"].sum().idxmax()
top_region = df.groupby("region")["revenue"].sum().idxmax()

# ==========================================
# DEMAND INDEX (NEW)
# ==========================================
demand_index = min(100, int((velocity * 3) + max(trend,0)*5))

# ==========================================
# CSS (PREMIUM)
# ==========================================
st.markdown("""
<style>
body {background:#020817;color:#e2e8f0}

.hero {
    padding:20px;
    border:1px solid #1e293b;
    border-radius:12px;
    margin-bottom:10px;
    background:linear-gradient(120deg,#020817,#0f172a);
}

.kpi {
    background:#0f172a;
    padding:15px;
    border-radius:10px;
    border:1px solid #1e293b;
}

.sec {
    font-size:12px;
    color:#22d3ee;
    letter-spacing:2px;
    margin-top:20px;
}

.ticker {
    white-space:nowrap;
    overflow:hidden;
}
.ticker span {
    display:inline-block;
    padding-right:40px;
    animation: scroll 20s linear infinite;
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
<h2>⚡ REVENUE WAR ROOM X</h2>
LIVE · {orders} ORDERS · NEXT SALE ~30s
</div>
""", unsafe_allow_html=True)

# ==========================================
# KPI ROW
# ==========================================
c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("Revenue", f"₹{total_rev:,.0f}")
c2.metric("Orders", orders)
c3.metric("Velocity", velocity)
c4.metric("Top City", top_city)
c5.metric("Top Product", top_product)

# ==========================================
# TICKER (ACTIVITY TAPE)
# ==========================================
tick = "".join([
    f"<span>⚡ {s['order']} {s['product']} ₹{s['revenue']:,} {s['city']}</span>"
    for s in ss.sales[-10:]
])

st.markdown(f'<div class="ticker">{tick}</div>', unsafe_allow_html=True)

# ==========================================
# MAIN GRID
# ==========================================
left, right = st.columns([2,1])

# -------- REVENUE FLOW
with left:
    df["bucket"] = df["time"].dt.floor("10min")
    rt = df.groupby("bucket")["revenue"].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rt.index,
        y=rt.values,
        fill='tozeroy'
    ))
    st.plotly_chart(fig, use_container_width=True)

# -------- DEMAND PANEL
with right:
    st.markdown("### Demand Pressure")

    st.progress(demand_index)

    if demand_index > 70:
        st.success("HIGH DEMAND")
    elif demand_index > 30:
        st.warning("MODERATE")
    else:
        st.error("LOW")

    st.markdown("### Region Leader")
    st.info(top_region)

# ==========================================
# CITY GRID
# ==========================================
st.markdown('<div class="sec">CITY PERFORMANCE</div>', unsafe_allow_html=True)

cols = st.columns(len(CITIES))

for i,(city,region) in enumerate(CITIES):
    rev = df[df["city"]==city]["revenue"].sum()
    cols[i].metric(city, f"₹{rev:,.0f}")

# ==========================================
# PRODUCT MOMENTUM
# ==========================================
st.markdown('<div class="sec">PRODUCT MOMENTUM</div>', unsafe_allow_html=True)

pm = df.groupby("product")["revenue"].sum().sort_values(ascending=False)

st.bar_chart(pm)

# ==========================================
# ALERTS
# ==========================================
st.markdown('<div class="sec">SMART ALERTS</div>', unsafe_allow_html=True)

if trend > 5:
    st.success("🚀 Sales accelerating rapidly")
elif trend < -5:
    st.error("⚠ Sales dropping significantly")
else:
    st.info("Stable performance")

# ==========================================
# AUTO REFRESH
# ==========================================
time.sleep(5)
st.rerun()