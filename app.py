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
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #030b14; }
    ::-webkit-scrollbar-thumb { background: #00dcff; border-radius: 10px; }
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
    # Pre-populate with 50 random orders for immediate visualization
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
        if (time.time() - cache[city]['t']) < 900: # 15 min cache
            return cache[city]['data']
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
    if any(x in d for x in ["cloud", "mist", "haze", "overcast"]): return "cloudy"
    return "clear"

# ─────────────────────────────────────────────
#  SIDEBAR: CONTROLS & FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛠 COMMAND CENTER")
    f_city = st.multiselect("Active Cities", options=CITIES, default=[])
    f_cat = st.multiselect("Categories", options=list(set(CAT_MAP.values())), default=[])
    
    p_range = (int(st.session_state.sales_df.Price.min()), int(st.session_state.sales_df.Price.max()))
    f_price = st.slider("Price Threshold", p_range[0], p_range[1], p_range)
    
    st.markdown("---")
    if st.button("🔴 RESET ALL DATA"):
        st.session_state.sales_df = st.session_state.sales_df.iloc[0:0]
        st.rerun()

# ─────────────────────────────────────────────
#  LIVE DATA GENERATION
# ─────────────────────────────────────────────
if time.time() - st.session_state.get('last_gen', 0) > 30:
    new_batch = []
    for _ in range(random.randint(2, 6)):
        p = random.choice(list(PRODUCTS.keys()))
        new_batch.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "DT": datetime.now(),
            "Product": p, "Category": CAT_MAP[p],
            "Price": random.randint(PRODUCTS[p][0], PRODUCTS[p][1]), "City": random.choice(CITIES)
        })
    st.session_state.sales_df = pd.concat([st.session_state.sales_df, pd.DataFrame(new_batch)]).tail(300)
    st.session_state.last_gen = time.time()

# Apply Filters
df = st.session_state.sales_df.copy()
if f_city: df = df[df.City.isin(f_city)]
if f_cat: df = df[df.Category.isin(f_cat)]
df = df[(df.Price >= f_price[0]) & (df.Price <= f_price[1])]

# ─────────────────────────────────────────────
#  UI: HEADER & KPIs
# ─────────────────────────────────────────────
st.markdown('<div class="war-room-title">⚡ PRO SALES WAR ROOM</div>', unsafe_allow_html=True)
st.markdown(f"<p style='color:#4a9abb;'>SYS_REFRESH: 30S | ACTIVE_ORDERS: {len(df)} | {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
total_rev = df.Price.sum() if not df.empty else 0
with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">GROSS REVENUE</div><div class="kpi-value">₹{total_rev/1e5:.2f}L</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL VOLUME</div><div class="kpi-value">{len(df)}</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">AOV</div><div class="kpi-value">₹{int(df.Price.mean() if not df.empty else 0):,}</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">TOP CATEGORY</div><div class="kpi-value">{df.Category.mode()[0] if not df.empty else "N/A"}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  UI: TOP CHARTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// REVENUE PERFORMANCE & GROWTH</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    if not df.empty:
        df_ts = df.sort_values("DT").assign(CumSum=df.sort_values("DT").Price.cumsum())
        fig_ts = px.line(df_ts, x="DT", y="CumSum", markers=True, title="CUMULATIVE REVENUE TIMELINE",
                         hover_data={"Timestamp": True, "Product": True, "City": True, "DT": False})
        fig_ts.update_traces(line_color='#00dcff', marker=dict(size=6, color="#ff4060", line=dict(width=1, color='white')))
        fig_ts.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350)
        st.plotly_chart(fig_ts, use_container_width=True)

with c2:
    if not df.empty:
        cat_rev = df.groupby("Category")["Price"].sum().reset_index()
        fig_pie = px.pie(cat_rev, values='Price', names='Category', hole=0.5, title="REVENUE BY CATEGORY")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────────────────────────────
#  UI: MIDDLE CHARTS (Advanced)
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// GEOSPATIAL & PRODUCT ANALYSIS</div>', unsafe_allow_html=True)
c3, c4, c5 = st.columns([1.2, 1.2, 1])

with c3:
    if not df.empty:
        # Heatmap: City x Category
        heat = df.pivot_table(index='City', columns='Category', values='Price', aggfunc='count').fillna(0)
        fig_heat = px.imshow(heat, text_auto=True, title="ORDER DENSITY HEATMAP", color_continuous_scale="Blues")
        fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350)
        st.plotly_chart(fig_heat, use_container_width=True)

with c4:
    if not df.empty:
        # Box plot: Price distribution
        fig_box = px.box(df, x="Category", y="Price", color="Category", title="PRICE DISTRIBUTION")
        fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

with c5:
    if not df.empty:
        # Horizontal Bar: Revenue by City
        city_data = df.groupby("City")["Price"].sum().sort_values()
        fig_city = px.bar(city_data, orientation='h', title="CITY REVENUE RANKING")
        fig_city.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#4a9abb", height=350)
        st.plotly_chart(fig_city, use_container_width=True)

# ─────────────────────────────────────────────
#  UI: LIVE FEED & WEATHER
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// LIVE TRANSACTION FEED (LATEST 12)</div>', unsafe_allow_html=True)
col_table, col_leader = st.columns([2, 1])

with col_table:
    if not df.empty:
        active_cities = df.tail(12)["City"].unique()
        weather_map = {c: get_weather(c) for c in active_cities}
        
        feed_df = df.sort_values("DT", ascending=False).head(12).copy()
        feed_df["Weather"] = feed_df["City"].apply(lambda c: {
            "rain": "🌧 Rain", "heat": "🔥 Heat", "clear": "☀ Clear", "cloudy": "☁ Cloudy", "unknown": "❓"
        }.get(weather_condition(weather_map.get(c, {"ok": False})), "❓"))
        
        feed_df["Price"] = feed_df["Price"].apply(lambda x: f"₹{x:,}")
        st.dataframe(feed_df[["Timestamp", "Product", "Category", "Price", "City", "Weather"]], 
                     use_container_width=True, hide_index=True, height=450)

with col_leader:
    st.markdown("<p style='color:#4a9abb; font-size:0.8rem;'>TOP PRODUCTS (VOLUME)</p>", unsafe_allow_html=True)
    if not df.empty:
        top_p = df.groupby("Product").size().sort_values(ascending=False).head(8).reset_index(name='Orders')
        st.table(top_p)
    
    with st.expander("📋 VIEW ALL RAW TRANSACTIONS"):
        st.write(df.sort_values("DT", ascending=False))

# ─────────────────────────────────────────────
#  FOOTER & AUTO-REFRESH
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div style='text-align:center; color:#4a9abb; font-size:0.7rem;'>PRO WAR ROOM ENGINE v2.0 • REAL-TIME BI DATA STREAM</div>", unsafe_allow_html=True)

time.sleep(30)
st.rerun()