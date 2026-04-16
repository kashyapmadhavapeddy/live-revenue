import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
#  PAGE CONFIG & THEME
# ─────────────────────────────────────────────
st.set_page_config(page_title="ULTIMATE SALES WAR ROOM", page_icon="🔥", layout="wide")

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
        font-size: 2.2rem; 
        font-weight: 900; 
        color: #00dcff; 
        text-shadow: 0 0 20px rgba(0,220,255,0.4); 
        letter-spacing: 2px;
    }
    
    .section-hdr { 
        font-family: 'Share Tech Mono', monospace; 
        font-size: .85rem; 
        color: #4a9abb; 
        text-transform: uppercase; 
        border-left: 3px solid #ff4060; 
        padding-left: 12px; 
        margin: 30px 0 15px; 
        letter-spacing: 2px;
    }

    .kpi-card {
        background: linear-gradient(135deg, rgba(0,25,50,0.7) 0%, rgba(0,10,20,0.8) 100%);
        border: 1px solid rgba(0,220,255,0.2);
        border-radius: 4px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .kpi-label { font-family: 'Share Tech Mono'; color: #4a9abb; font-size: 0.75rem; letter-spacing: 1px; }
    .kpi-value { font-family: 'Orbitron'; color: #00dcff; font-size: 2rem; font-weight: 700; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA CONSTANTS
# ─────────────────────────────────────────────
PRODUCTS = {
    "MacBook Pro 16\"": (189000, 229000), "Dell XPS 15": (129000, 159000),
    "iPhone 15 Pro Max": (134900, 159900), "Samsung Galaxy S24 Ultra": (109900, 129900),
    "Sony WH-1000XM5": (22900, 29900), "iPad Pro 12.9\"": (89900, 119900),
    "LG OLED 55\" TV": (79900, 109900), "OnePlus 12": (54999, 64999),
    "Apple Watch Ultra 2": (79900, 89900), "Bose QC45": (24900, 29900),
    "Canon EOS R6 Mark II": (219000, 259000), "Nintendo Switch": (28000, 32000)
}
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat"]
CAT_MAP = {k: "Laptops" if any(x in k for x in ["MacBook", "Dell"]) else 
                "Phones" if any(x in k for x in ["iPhone", "Samsung", "OnePlus"]) else 
                "Audio" if any(x in k for x in ["Sony", "Bose"]) else 
                "Tablets" if "iPad" in k else "TVs" if "TV" in k else 
                "Wearables" if "Watch" in k else "Cameras" if "Canon" in k else "Gaming" 
                for k in PRODUCTS.keys()}

# ─────────────────────────────────────────────
#  STATE MANAGEMENT
# ─────────────────────────────────────────────
if "sales_df" not in st.session_state:
    start_time = datetime.now() - timedelta(hours=2)
    init_data = []
    for i in range(50):
        p = random.choice(list(PRODUCTS.keys()))
        init_data.append({
            "Timestamp": (start_time + timedelta(minutes=i*2)).strftime("%H:%M:%S"),
            "DT": start_time + timedelta(minutes=i*2),
            "Product": p, "Category": CAT_MAP[p],
            "Price": random.randint(PRODUCTS[p][0], PRODUCTS[p][1]), "City": random.choice(CITIES)
        })
    st.session_state.sales_df = pd.DataFrame(init_data)

if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}

# ─────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────
def get_weather(city):
    cache = st.session_state.weather_cache
    if city in cache and isinstance(cache[city], dict) and 't' in cache[city]:
        if (time.time() - cache[city]['t']) < 900: return cache[city]['data']
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
    if any(x in d for x in ["rain", "drizzle", "thunder"]): return "rain"
    if t >= 35: return "heat"
    if any(x in d for x in ["cloud", "mist", "haze"]): return "cloudy"
    return "clear"

# ─────────────────────────────────────────────
#  SIDEBAR COMMANDS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛠 FILTERS")
    f_city = st.multiselect("Cities", options=CITIES, default=[])
    f_cat = st.multiselect("Categories", options=list(set(CAT_MAP.values())), default=[])
    
    current_min = int(st.session_state.sales_df.Price.min()) if not st.session_state.sales_df.empty else 0
    current_max = int(st.session_state.sales_df.Price.max()) if not st.session_state.sales_df.empty else 300000
    f_price = st.slider("Price Range", current_min, current_max, (current_min, current_max))
    
    st.markdown("---")
    if st.button("🔴 CLEAR SESSION"):
        st.session_state.sales_df = pd.DataFrame(columns=["Timestamp", "DT", "Product", "Category", "Price", "City"])
        st.rerun()

# ─────────────────────────────────────────────
#  LIVE DATA FLOW
# ─────────────────────────────────────────────
if time.time() - st.session_state.get('last_gen', 0) > 30:
    new_orders = []
    for _ in range(random.randint(2, 5)):
        p = random.choice(list(PRODUCTS.keys()))
        new_orders.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "DT": datetime.now(),
            "Product": p, "Category": CAT_MAP[p],
            "Price": random.randint(PRODUCTS[p][0], PRODUCTS[p][1]), "City": random.choice(CITIES)
        })
    st.session_state.sales_df = pd.concat([st.session_state.sales_df, pd.DataFrame(new_orders)]).tail(200)
    st.session_state.last_gen = time.time()

# Apply Filters
df = st.session_state.sales_df.copy()
if f_city: df = df[df.City.isin(f_city)]
if f_cat: df = df[df.Category.isin(f_cat)]
df = df[(df.Price >= f_price[0]) & (df.Price <= f_price[1])]

# ─────────────────────────────────────────────
#  MAIN DASHBOARD
# ─────────────────────────────────────────────
st.markdown('<div class="war-room-title">⚡ PRO SALES WAR ROOM</div>', unsafe_allow_html=True)

if df.empty:
    st.warning("📡 No transactions found for selected filters. Waiting for data...")
else:
    # 1. KPI SECTION
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">GROSS REV</div><div class="kpi-value">₹{df.Price.sum()/1e5:.2f}L</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">VOL</div><div class="kpi-value">{len(df)}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">AOV</div><div class="kpi-value">₹{int(df.Price.mean()):,}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">HOT CITY</div><div class="kpi-value">{df.City.mode()[0]}</div></div>', unsafe_allow_html=True)

    # 2. ANALYTICS ROW
    st.markdown('<div class="section-hdr">// PERFORMANCE ANALYTICS</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Sort and cumulative logic protected by the 'if not df.empty' check
        df_plot = df.sort_values("DT")
        df_plot["CumSum"] = df_plot["Price"].cumsum()
        fig_ts = px.line(df_plot, x="DT", y="CumSum", markers=True, title="CUMULATIVE REVENUE TIMELINE")
        fig_ts.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350)
        st.plotly_chart(fig_ts, use_container_width=True)
        
    with c2:
        fig_pie = px.pie(df, values='Price', names='Category', hole=0.5, title="REVENUE BY CATEGORY")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 3. ADVANCED ROW
    st.markdown('<div class="section-hdr">// DISTRIBUTION & DENSITY</div>', unsafe_allow_html=True)
    c3, c4, c5 = st.columns([1, 1, 1])
    
    with c3:
        heat = df.pivot_table(index='City', columns='Category', values='Price', aggfunc='count').fillna(0)
        fig_h = px.imshow(heat, text_auto=True, title="ORDER HEATMAP", color_continuous_scale="Blues")
        fig_h.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig_h, use_container_width=True)
        
    with c4:
        fig_b = px.box(df, x="Category", y="Price", color="Category", title="PRICE BOXPLOT")
        fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350, showlegend=False)
        st.plotly_chart(fig_b, use_container_width=True)
        
    with c5:
        city_rev = df.groupby("City")["Price"].sum().sort_values()
        fig_bar = px.bar(city_rev, orientation='h', title="CITY REVENUE")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig_bar, use_container_width=True)

    # 4. LIVE FEED
    st.markdown('<div class="section-hdr">// LIVE FEED & LEADERBOARD</div>', unsafe_allow_html=True)
    col_f, col_l = st.columns([2, 1])
    
    with col_f:
        # Weather logic only for the latest cities
        active_c = df.tail(12)["City"].unique()
        weather_map = {c: get_weather(c) for c in active_c}
        
        feed_df = df.sort_values("DT", ascending=False).head(12).copy()
        feed_df["Weather"] = feed_df["City"].apply(lambda c: {
            "rain": "🌧", "heat": "🔥", "clear": "☀", "cloudy": "☁"
        }.get(weather_condition(weather_map.get(c, {})), "❓"))
        
        feed_df["Price"] = feed_df["Price"].apply(lambda x: f"₹{x:,}")
        st.dataframe(feed_df[["Timestamp", "Product", "Price", "City", "Weather"]], use_container_width=True, hide_index=True)

    with col_l:
        st.markdown("<p style='font-size:0.8rem; color:#4a9abb;'>TOP PRODUCTS (VOL)</p>", unsafe_allow_html=True)
        st.table(df.groupby("Product").size().sort_values(ascending=False).head(8).reset_index(name='Orders'))

    with st.expander("📋 RAW DATA EXPLORER"):
        st.dataframe(df.sort_values("DT", ascending=False))

time.sleep(30)
st.rerun()