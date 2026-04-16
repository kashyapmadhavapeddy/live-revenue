import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SALES WAR ROOM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Orbitron:wght@700;900&display=swap');

html, body, [data-testid="stApp"] {
    background: #030b14;
    color: #c8d8e8;
    font-family: 'Rajdhani', sans-serif;
}
[data-testid="stApp"]::before {
    content: "";
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(0,220,255,.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 30% at 80% 110%, rgba(0,80,200,.06) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1.5rem 2rem; max-width: 100%; }

.kpi-card {
    background: linear-gradient(135deg, rgba(0,20,40,.85) 0%, rgba(0,10,25,.95) 100%);
    border: 1px solid rgba(0,220,255,.18);
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 24px rgba(0,180,255,.06), inset 0 1px 0 rgba(255,255,255,.04);
}
.kpi-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00dcff, transparent);
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: .72rem;
    letter-spacing: .18em;
    color: #4a9abb;
    text-transform: uppercase;
    margin-bottom: .4rem;
}
.kpi-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #00dcff;
    line-height: 1;
    text-shadow: 0 0 20px rgba(0,220,255,.5);
}
.kpi-delta {
    font-family: 'Share Tech Mono', monospace;
    font-size: .78rem;
    margin-top: .5rem;
}
.kpi-delta.up   { color: #00ff9d; }
.kpi-delta.down { color: #ff4060; }
.kpi-delta.neut { color: #4a9abb; }

.section-hdr {
    font-family: 'Share Tech Mono', monospace;
    font-size: .7rem;
    letter-spacing: .25em;
    color: #4a9abb;
    text-transform: uppercase;
    border-left: 2px solid #00dcff;
    padding-left: .6rem;
    margin: 1.4rem 0 .8rem;
}

.weather-pill {
    display: inline-block;
    padding: .25rem .8rem;
    border-radius: 2px;
    font-family: 'Share Tech Mono', monospace;
    font-size: .75rem;
    letter-spacing: .1em;
    font-weight: 600;
    margin: .2rem .2rem;
}
.w-rain  { background: rgba(0,140,255,.15); border: 1px solid rgba(0,140,255,.4); color: #60b8ff; }
.w-heat  { background: rgba(255,120,0,.15);  border: 1px solid rgba(255,120,0,.4);  color: #ffaa44; }
.w-clear { background: rgba(0,255,160,.10);  border: 1px solid rgba(0,255,160,.3);  color: #00ff9d; }
.w-cloud { background: rgba(150,170,200,.10);border: 1px solid rgba(150,170,200,.3);color: #99bbcc; }

.alert-banner { background: rgba(255,64,96,.08); border: 1px solid rgba(255,64,96,.35); border-left: 3px solid #ff4060; padding: .6rem 1rem; color: #ff8099; margin-bottom: .5rem; font-family: 'Share Tech Mono', monospace; }
.good-banner { background: rgba(0,255,157,.06); border: 1px solid rgba(0,255,157,.25); border-left: 3px solid #00ff9d; padding: .6rem 1rem; color: #00ff9d; margin-bottom: .5rem; font-family: 'Share Tech Mono', monospace; }

.ticker-wrap { background: rgba(0,15,30,.9); border-top: 1px solid rgba(0,220,255,.15); border-bottom: 1px solid rgba(0,220,255,.15); padding: .4rem 0; overflow: hidden; white-space: nowrap; margin-bottom: 1rem; }
.ticker-inner { display: inline-block; animation: scroll-left 40s linear infinite; font-family: 'Share Tech Mono', monospace; font-size: .75rem; color: #4a9abb; }
@keyframes scroll-left { 0% { transform: translateX(100vw); } 100% { transform: translateX(-100%); } }

.war-room-title { font-family: 'Orbitron', sans-serif; font-size: 1.5rem; font-weight: 900; color: #00dcff; text-shadow: 0 0 30px rgba(0,220,255,.6); letter-spacing: .15em; }
.blink { animation: blink 1.2s step-start infinite; }
@keyframes blink { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA DEFINITIONS
# ─────────────────────────────────────────────
PRODUCTS = {
    "MacBook Pro 16\"": (189000, 229000), "Dell XPS 15": (129000, 159000),
    "iPhone 15 Pro Max": (134900, 159900), "Samsung Galaxy S24 Ultra": (109900, 129900),
    "Sony WH-1000XM5": (22900, 29900), "iPad Pro 12.9\"": (89900, 119900),
    "LG OLED 55\" TV": (79900, 109900), "OnePlus 12": (54999, 64999),
    "Bose QC45": (24900, 29900), "Dyson V15 Vacuum": (49900, 59900),
    "Nintendo Switch OLED": (29999, 34999), "Canon EOS R6 Mark II": (219000, 259000),
    "Kindle Paperwhite": (13999, 16999), "Apple Watch Ultra 2": (79900, 89900),
    "JBL Flip 6": (8999, 12999),
}

CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat"]

CATEGORY_MAP = {
    "MacBook Pro 16\"": "Laptops", "Dell XPS 15": "Laptops", "iPhone 15 Pro Max": "Phones",
    "Samsung Galaxy S24 Ultra": "Phones", "OnePlus 12": "Phones", "Sony WH-1000XM5": "Audio",
    "Bose QC45": "Audio", "JBL Flip 6": "Audio", "iPad Pro 12.9\"": "Tablets",
    "Kindle Paperwhite": "Tablets", "LG OLED 55\" TV": "TVs", "Nintendo Switch OLED": "Gaming",
    "Canon EOS R6 Mark II": "Cameras", "Dyson V15 Vacuum": "Appliances", "Apple Watch Ultra 2": "Wearables",
}

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "sales_df" not in st.session_state:
    st.session_state.sales_df = pd.DataFrame(columns=["Timestamp", "Product", "Category", "Price", "City"])
if "last_generated" not in st.session_state:
    st.session_state.last_generated = time.time() - 35
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}
if "total_revenue_prev" not in st.session_state:
    st.session_state.total_revenue_prev = 0
if "order_vol_prev" not in st.session_state:
    st.session_state.order_vol_prev = 0

# ─────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    lo, hi = PRODUCTS[product]
    price = int(random.randint(lo, hi) * random.choice([0.9, 1.0, 1.1]))
    city = random.choices(CITIES, weights=[20, 18, 15, 12, 10, 8, 7, 4, 3, 3], k=1)[0]
    return {"Timestamp": datetime.now().strftime("%H:%M:%S"), "Product": product, "Category": CATEGORY_MAP[product], "Price": price, "City": city}

def get_weather(city: str) -> dict:
    cache = st.session_state.weather_cache
    if city in cache and (time.time() - cache[city]["fetched_at"]) < 600:
        return cache[city]
    try:
        api_key = st.secrets["WEATHER_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            result = {"desc": d["weather"][0]["description"].lower(), "temp": d["main"]["temp"], "ok": True, "fetched_at": time.time()}
            cache[city] = result
            return result
    except: pass
    return {"desc": "unknown", "temp": None, "ok": False, "fetched_at": time.time()}

def weather_condition(w: dict) -> str:
    if not w or not w.get("ok"): return "unknown"
    d, t = w.get("desc", ""), w.get("temp", 25)
    if any(x in d for x in ["rain", "drizzle", "thunderstorm"]): return "rain"
    if t is not None and t >= 35: return "heat"
    if any(x in d for x in ["cloud", "overcast", "haze", "mist"]): return "cloudy"
    return "clear"

def kpi(label, value, delta=None, delta_type="neut", is_currency=False):
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        fmt_delta = f"₹{abs(delta):,}" if is_currency else f"{abs(delta):,}"
        delta_html = f'<div class="kpi-delta {delta_type}">{arrow} {fmt_delta}</div>'
    return f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{delta_html}</div>'

# ─────────────────────────────────────────────
#  LOGIC RUN
# ─────────────────────────────────────────────
now = time.time()
if now - st.session_state.last_generated >= 30:
    for _ in range(random.randint(1, 3)):
        st.session_state.sales_df = pd.concat([st.session_state.sales_df, pd.DataFrame([generate_sale()])], ignore_index=True)
    st.session_state.last_generated = now
    st.session_state.sales_df = st.session_state.sales_df.tail(500)

df = st.session_state.sales_df.copy()
total_revenue = df["Price"].sum() if len(df) else 0
order_volume = len(df)

rev_delta = total_revenue - st.session_state.total_revenue_prev
vol_delta = order_volume - st.session_state.order_vol_prev
st.session_state.total_revenue_prev, st.session_state.order_vol_prev = total_revenue, order_volume

active_cities = df["City"].unique().tolist() if len(df) else CITIES
weather_data = {city: get_weather(city) for city in active_cities}

# ─────────────────────────────────────────────
#  UI HEADER & TICKER
# ─────────────────────────────────────────────
c_l, c_t, c_s = st.columns([3, 2, 2])
with c_l: st.markdown('<div class="war-room-title">⚡ SALES WAR ROOM</div>', unsafe_allow_html=True)
with c_t: st.markdown(f"<div style='text-align:center; color:#4a9abb;'>LAST SYNC<br><span style='color:#00dcff; font-size:1.2rem;'>{datetime.now().strftime('%H:%M:%S')}</span></div>", unsafe_allow_html=True)
with c_s: st.markdown(f"<div style='text-align:center; color:#4a9abb;'>STATUS<br><span class='blink' style='color:#00ff9d;'>● LIVE</span></div>", unsafe_allow_html=True)

if len(df) > 0:
    items = "  ◆  ".join(f"[{r.Timestamp}] {r.City.upper()} — {r.Product} @ ₹{r.Price:,}" for _, r in df.tail(8).iterrows())
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-inner">◆ LIVE FEED ◆ {items} ◆</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.markdown(kpi("Total Revenue", f"₹{total_revenue/1e5:.2f}L", rev_delta, "up" if rev_delta>=0 else "down", True), unsafe_allow_html=True)
with k2: st.markdown(kpi("Orders", f"{order_volume:,}", vol_delta, "up" if vol_delta>=0 else "down"), unsafe_allow_html=True)
with k3: st.markdown(kpi("Avg Order", f"₹{int(df['Price'].mean() if len(df) else 0):,}"), unsafe_allow_html=True)
with k4: st.markdown(kpi("Hot City", df["City"].value_counts().idxmax() if len(df) else "—"), unsafe_allow_html=True)
with k5: st.markdown(kpi("Top Category", df["Category"].value_counts().idxmax() if len(df) else "—"), unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// REVENUE INTELLIGENCE</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns([3, 2])

with ch1:
    if len(df) > 2:
        fig = px.area(df.assign(Cum=df['Price'].cumsum()), x=df.index, y='Cum', title="CUMULATIVE REVENUE")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=260, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with ch2:
    if len(df) > 0:
        fig2 = px.pie(df, values='Price', names='Category', hole=0.5, title="BY CATEGORY")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=260, showlegend=False, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

st.markdown('<div class="section-hdr">// DISTRIBUTION & VELOCITY</div>', unsafe_allow_html=True)
ch3, ch4, ch5 = st.columns(3)

with ch3:
    if len(df) > 0:
        prod_rev = df.groupby("Product")["Price"].sum().sort_values().tail(5)
        fig3 = px.bar(prod_rev, orientation='h', title="TOP PRODUCTS")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=260, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig3, use_container_width=True)

with ch4:
    if len(df) > 0:
        city_rev = df.groupby("City")["Price"].sum().sort_values(ascending=False)
        fig4 = px.bar(city_rev, title="CITY REVENUE")
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=260, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig4, use_container_width=True)

with ch5:
    if len(df) > 0:
        vel = df.groupby(df.index // 5).size()
        fig5 = px.line(vel, title="ORDER VELOCITY")
        fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=260, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
#  TABLE & FOOTER
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// LIVE FEED</div>', unsafe_allow_html=True)
if len(df) > 0:
    display_df = df.tail(10).sort_index(ascending=False).copy()
    # Fixed Weather Logic
    display_df["Weather"] = display_df["City"].apply(lambda c: {
        "rain": "🌧 Rain", "heat": "🔥 Heat", "clear": "☀ Clear", "cloudy": "☁ Cloudy", "unknown": "❓"
    }.get(weather_condition(weather_data.get(c, {"ok": False})), "❓"))
    
    st.dataframe(display_df[["Timestamp", "Product", "Price", "City", "Weather"]], use_container_width=True, hide_index=True)

time.sleep(30)
st.rerun()