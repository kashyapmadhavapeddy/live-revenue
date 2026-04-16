import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import requests
from datetime import datetime
import plotly.express as px

# ─────────────────────────────────────────────
#  PAGE CONFIG & CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="SALES WAR ROOM", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Orbitron:wght@700;900&display=swap');
    
    html, body, [data-testid="stApp"] { 
        background: #030b14; 
        color: #c8d8e8; 
        font-family: 'Rajdhani', sans-serif; 
    }
    
    .war-room-title { 
        font-family: 'Orbitron', sans-serif; 
        font-size: 2rem; 
        font-weight: 900; 
        color: #00dcff; 
        text-shadow: 0 0 20px rgba(0,220,255,0.4); 
        margin-bottom: 0px;
    }
    
    .section-hdr { 
        font-family: 'Share Tech Mono', monospace; 
        font-size: .85rem; 
        color: #4a9abb; 
        text-transform: uppercase; 
        border-left: 3px solid #00dcff; 
        padding-left: 10px; 
        margin: 25px 0 15px; 
        letter-spacing: 2px;
    }

    .kpi-card {
        background: rgba(0,20,40,0.7);
        border: 1px solid rgba(0,220,255,0.2);
        border-radius: 4px;
        padding: 20px;
        text-align: center;
        box-shadow: inset 0 0 15px rgba(0,220,255,0.05);
    }
    
    .kpi-label { font-family: 'Share Tech Mono'; color: #4a9abb; font-size: 0.8rem; }
    .kpi-value { font-family: 'Orbitron'; color: #00dcff; font-size: 1.8rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA INITIALIZATION
# ─────────────────────────────────────────────
PRODUCTS = {
    "MacBook Pro 16\"": (189000, 229000), "Dell XPS 15": (129000, 159000),
    "iPhone 15 Pro Max": (134900, 159900), "Samsung Galaxy S24 Ultra": (109900, 129900),
    "Sony WH-1000XM5": (22900, 29900), "iPad Pro 12.9\"": (89900, 119900),
    "LG OLED 55\" TV": (79900, 109900), "OnePlus 12": (54999, 64999),
    "Apple Watch Ultra 2": (79900, 89900), "Bose QC45": (24900, 29900),
    "Canon EOS R6 Mark II": (219000, 259000)
}
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat"]
CAT_MAP = {
    "MacBook Pro 16\"": "Laptops", "Dell XPS 15": "Laptops", "iPhone 15 Pro Max": "Phones",
    "Samsung Galaxy S24 Ultra": "Phones", "OnePlus 12": "Phones", "Sony WH-1000XM5": "Audio",
    "Bose QC45": "Audio", "iPad Pro 12.9\"": "Tablets", "LG OLED 55\" TV": "TVs", 
    "Apple Watch Ultra 2": "Wearables", "Canon EOS R6 Mark II": "Cameras"
}

if "sales_df" not in st.session_state:
    st.session_state.sales_df = pd.DataFrame(columns=["Timestamp", "Product", "Category", "Price", "City"])
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}

# ─────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────
def get_weather(city):
    cache = st.session_state.weather_cache
    if city in cache and isinstance(cache[city], dict) and 't' in cache[city]:
        if (time.time() - cache[city]['t']) < 600: return cache[city]['data']
    try:
        api_key = st.secrets["WEATHER_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
        r = requests.get(url, timeout=3).json()
        res = {"desc": r["weather"][0]["description"].lower(), "temp": r["main"]["temp"], "ok": True}
        cache[city] = {'t': time.time(), 'data': res}
        return res
    except: return {"ok": False}

def weather_condition(w):
    if not w or not w.get("ok"): return "unknown"
    d, t = w.get("desc", ""), w.get("temp", 25)
    if any(x in d for x in ["rain", "drizzle"]): return "rain"
    if t >= 35: return "heat"
    if any(x in d for x in ["cloud", "mist", "haze"]): return "cloudy"
    return "clear"

# ─────────────────────────────────────────────
#  GENERATOR
# ─────────────────────────────────────────────
if time.time() - st.session_state.get('last_gen', 0) > 30:
    new_data = []
    for _ in range(random.randint(2, 5)):
        p = random.choice(list(PRODUCTS.keys()))
        new_data.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Product": p, "Category": CAT_MAP[p],
            "Price": random.randint(PRODUCTS[p][0], PRODUCTS[p][1]),
            "City": random.choice(CITIES)
        })
    st.session_state.sales_df = pd.concat([pd.DataFrame(new_data), st.session_state.sales_df]).head(100)
    st.session_state.last_gen = time.time()

df = st.session_state.sales_df

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
h1, h2 = st.columns([2, 1])
with h1:
    st.markdown('<div class="war-room-title">⚡ SALES WAR ROOM</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#4a9abb;'>AUTO-REFRESH 30s • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TOP ROW: KPIs
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_rev = df["Price"].sum() if not df.empty else 0
with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL REVENUE</div><div class="kpi-value">₹{total_rev/1e5:.2f}L</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL ORDERS</div><div class="kpi-value">{len(df)}</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">AVG ORDER</div><div class="kpi-value">₹{int(df["Price"].mean() if not df.empty else 0):,}</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">HOT CITY</div><div class="kpi-value">{df["City"].mode()[0] if not df.empty else "N/A"}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MIDDLE ROW: CHARTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    if not df.empty:
        # Reverse DF for chronological cumulative chart
        fig_rev = px.area(df.iloc[::-1].assign(CumRev=df.iloc[::-1]['Price'].cumsum()), 
                          x=range(len(df)), y='CumRev', title="REVENUE GROWTH MOMENTUM")
        fig_rev.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=300)
        st.plotly_chart(fig_rev, use_container_width=True)

with c2:
    if not df.empty:
        fig_pie = px.pie(df, values='Price', names='Category', hole=0.4, title="REVENUE SHARE")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=300, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────────────────────────────
#  BOTTOM ROW: TABLES
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// TRANSACTION LOGS & LEADERBOARDS</div>', unsafe_allow_html=True)
col_main, col_side = st.columns([2, 1])

with col_main:
    if not df.empty:
        active_cities = df["City"].unique()
        weather_map = {c: get_weather(c) for c in active_cities}
        
        display_df = df.copy()
        display_df["Weather"] = display_df["City"].apply(lambda c: {
            "rain": "🌧 Rain", "heat": "🔥 Heat", "clear": "☀ Clear", "cloudy": "☁ Cloudy", "unknown": "❓"
        }.get(weather_condition(weather_map.get(c, {"ok": False})), "❓"))
        
        display_df["Price"] = display_df["Price"].apply(lambda x: f"₹{x:,}")
        
        st.dataframe(display_df[["Timestamp", "Product", "Price", "City", "Weather"]], 
                     use_container_width=True, hide_index=True, height=400)

with col_side:
    # Category Leaderboard
    if not df.empty:
        cat_stats = df.groupby("Category").agg(Orders=("Product", "count"), Rev=("Price", "sum")).sort_values("Rev", ascending=False)
        cat_stats["Rev"] = cat_stats["Rev"].apply(lambda x: f"₹{x:,}")
        st.markdown("<p style='font-size:0.8rem; color:#4a9abb; margin-bottom:5px;'>CATEGORY RANKING</p>", unsafe_allow_html=True)
        st.table(cat_stats)

    # City Leaderboard
    if not df.empty:
        city_stats = df.groupby("City").agg(Rev=("Price", "sum")).sort_values("Rev", ascending=False).head(5)
        city_stats["Rev"] = city_stats["Rev"].apply(lambda x: f"₹{x:,}")
        st.markdown("<p style='font-size:0.8rem; color:#4a9abb; margin-bottom:5px;'>TOP CITIES</p>", unsafe_allow_html=True)
        st.table(city_stats)

time.sleep(30)
st.rerun()