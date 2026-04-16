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
    html, body, [data-testid="stApp"] { background: #030b14; color: #c8d8e8; font-family: 'Rajdhani', sans-serif; }
    .stDataFrame { border: 1px solid rgba(0,220,255,0.1) !important; }
    .war-room-title { font-family: 'Orbitron', sans-serif; font-size: 1.8rem; font-weight: 900; color: #00dcff; text-shadow: 0 0 20px rgba(0,220,255,0.4); }
    .section-hdr { font-family: 'Share Tech Mono', monospace; font-size: .8rem; color: #4a9abb; text-transform: uppercase; border-left: 3px solid #00dcff; padding-left: 10px; margin: 20px 0 10px; }
    .kpi-card { background: rgba(0,20,40,0.6); border: 1px solid rgba(0,220,255,0.2); border-radius: 4px; padding: 15px; text-align: center; }
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
    "Apple Watch Ultra 2": (79900, 89900), "Bose QC45": (24900, 29900)
}
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat"]
CAT_MAP = {
    "MacBook Pro 16\"": "Laptops", "Dell XPS 15": "Laptops", "iPhone 15 Pro Max": "Phones",
    "Samsung Galaxy S24 Ultra": "Phones", "OnePlus 12": "Phones", "Sony WH-1000XM5": "Audio",
    "Bose QC45": "Audio", "iPad Pro 12.9\"": "Tablets", "LG OLED 55\" TV": "TVs", "Apple Watch Ultra 2": "Wearables"
}

if "sales_df" not in st.session_state:
    st.session_state.sales_df = pd.DataFrame(columns=["Timestamp", "Product", "Category", "Price", "City"])
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}

# ─────────────────────────────────────────────
#  CORE FUNCTIONS
# ─────────────────────────────────────────────
def get_weather(city):
    cache = st.session_state.weather_cache
    
    # Check if city is in cache AND has the 't' (timestamp) and 'data' keys
    if city in cache and isinstance(cache[city], dict):
        if 't' in cache[city] and 'data' in cache[city]:
            if (time.time() - cache[city]['t']) < 600:
                return cache[city]['data']
    
    try:
        api_key = st.secrets["WEATHER_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
        r = requests.get(url, timeout=3).json()
        
        # Ensure we got a successful response from the API
        if "weather" in r and "main" in r:
            res = {
                "desc": r["weather"][0]["description"].lower(),
                "temp": r["main"]["temp"],
                "ok": True
            }
            # Save with the correct structure
            cache[city] = {'t': time.time(), 'data': res}
            return res
        else:
            return {"ok": False}
    except Exception as e:
        return {"ok": False}

def weather_condition(w):
    if not w.get("ok"): return "unknown"
    d, t = w.get("desc", ""), w.get("temp", 25)
    if any(x in d for x in ["rain", "drizzle"]): return "rain"
    if t >= 35: return "heat"
    if any(x in d for x in ["cloud", "mist", "haze"]): return "cloudy"
    return "clear"

# ─────────────────────────────────────────────
#  SIMULATION ENGINE
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
    st.session_state.sales_df = pd.concat([pd.DataFrame(new_data), st.session_state.sales_df]).head(50)
    st.session_state.last_gen = time.time()

df = st.session_state.sales_df

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="war-room-title">⚡ SALES WAR ROOM</div>', unsafe_allow_html=True)
st.markdown(f"<p style='color:#4a9abb;'>AUTO-REFRESH 30s • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────────
col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown('<div class="section-hdr">// LIVE TRANSACTION FEED</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Fetch weather for visible cities only to save API calls
        active_cities = df["City"].unique()
        weather_map = {c: get_weather(c) for c in active_cities}
        
        display_df = df.copy()
        display_df["Weather"] = display_df["City"].apply(lambda c: {
            "rain": "🌧 Rain", "heat": "🔥 Heat", "clear": "☀ Clear", "cloudy": "☁ Cloudy", "unknown": "❓"
        }.get(weather_condition(weather_map.get(c, {"ok": False})), "❓"))
        
        # Formatting for the table
        display_df["Price"] = display_df["Price"].apply(lambda x: f"₹{x:,}")
        
        st.dataframe(
            display_df[["Timestamp", "Product", "Category", "Price", "City", "Weather"]],
            use_container_width=True,
            hide_index=True,
            height=450
        )
    else:
        st.info("Waiting for incoming transactions...")

with col_side:
    # 1. Category Breakdown
    st.markdown('<div class="section-hdr">CATEGORY BREAKDOWN</div>', unsafe_allow_html=True)
    if not df.empty:
        cat_stats = df.groupby("Category").agg(
            Orders=("Product", "count"),
            Revenue=("Price", "sum")
        ).sort_values("Revenue", ascending=False)
        cat_stats["AvgOrder"] = (cat_stats["Revenue"] / cat_stats["Orders"]).astype(int)
        
        # Formatting for display
        cat_disp = cat_stats.copy()
        cat_disp["Revenue"] = cat_disp["Revenue"].apply(lambda x: f"₹{x:,}")
        cat_disp["AvgOrder"] = cat_disp["AvgOrder"].apply(lambda x: f"₹{x:,}")
        st.table(cat_disp)

    # 2. City Leaderboard
    st.markdown('<div class="section-hdr">CITY LEADERBOARD</div>', unsafe_allow_html=True)
    if not df.empty:
        city_stats = df.groupby("City").agg(
            Orders=("Product", "count"),
            Revenue=("Price", "sum")
        ).sort_values("Revenue", ascending=False).head(6)
        
        city_disp = city_stats.copy()
        city_disp["Revenue"] = city_disp["Revenue"].apply(lambda x: f"₹{x:,}")
        st.table(city_disp)

# ─────────────────────────────────────────────
#  FOOTER & RERUN
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div style='text-align:center; color:#4a9abb; font-size:0.7rem;'>POWERED BY OPENWEATHERMAP • STREAMLIT CLOUD</div>", unsafe_allow_html=True)

time.sleep(30)
st.rerun()