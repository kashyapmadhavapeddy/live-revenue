import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import requests
from datetime import datetime, timedelta
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
#  CUSTOM CSS  –  dark command-center aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Orbitron:wght@700;900&display=swap');

/* ── base ── */
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
/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1.5rem 2rem; max-width: 100%; }

/* ── scanline overlay ── */
body::after {
    content: "";
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,.03) 2px, rgba(0,0,0,.03) 4px);
    pointer-events: none; z-index: 9999;
}

/* ── KPI cards ── */
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

/* ── section headers ── */
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

/* ── weather pill ── */
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

/* ── alert banner ── */
.alert-banner {
    background: rgba(255,64,96,.08);
    border: 1px solid rgba(255,64,96,.35);
    border-left: 3px solid #ff4060;
    border-radius: 3px;
    padding: .6rem 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: .8rem;
    color: #ff8099;
    margin-bottom: .5rem;
}
.good-banner {
    background: rgba(0,255,157,.06);
    border: 1px solid rgba(0,255,157,.25);
    border-left: 3px solid #00ff9d;
    border-radius: 3px;
    padding: .6rem 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: .8rem;
    color: #00ff9d;
    margin-bottom: .5rem;
}

/* ── live feed table ── */
[data-testid="stDataFrame"] {
    background: rgba(0,10,25,.7) !important;
    border: 1px solid rgba(0,220,255,.12) !important;
    border-radius: 3px;
}
[data-testid="stDataFrame"] th {
    background: rgba(0,220,255,.06) !important;
    color: #4a9abb !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: .7rem !important;
    letter-spacing: .12em !important;
}

/* ── ticker ── */
.ticker-wrap {
    background: rgba(0,15,30,.9);
    border-top: 1px solid rgba(0,220,255,.15);
    border-bottom: 1px solid rgba(0,220,255,.15);
    padding: .4rem 0;
    overflow: hidden;
    white-space: nowrap;
    margin-bottom: 1rem;
}
.ticker-inner {
    display: inline-block;
    animation: scroll-left 40s linear infinite;
    font-family: 'Share Tech Mono', monospace;
    font-size: .75rem;
    color: #4a9abb;
    letter-spacing: .08em;
}
@keyframes scroll-left {
    0%   { transform: translateX(100vw); }
    100% { transform: translateX(-100%); }
}

/* ── plotly chart backgrounds ── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* ── title ── */
.war-room-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.5rem;
    font-weight: 900;
    color: #00dcff;
    text-shadow: 0 0 30px rgba(0,220,255,.6);
    letter-spacing: .15em;
    margin: 0;
}
.war-room-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: .7rem;
    color: #4a9abb;
    letter-spacing: .2em;
    margin-top: .15rem;
}
.blink { animation: blink 1.2s step-start infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ── metric delta override ── */
[data-testid="stMetricDelta"] { display: none; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #030b14; }
::-webkit-scrollbar-thumb { background: rgba(0,220,255,.2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA DEFINITIONS
# ─────────────────────────────────────────────
PRODUCTS = {
    "MacBook Pro 16\"":     (189000, 229000),
    "Dell XPS 15":          (129000, 159000),
    "iPhone 15 Pro Max":    (134900, 159900),
    "Samsung Galaxy S24 Ultra": (109900, 129900),
    "Sony WH-1000XM5":      (22900,  29900),
    "iPad Pro 12.9\"":      (89900,  119900),
    "LG OLED 55\" TV":      (79900,  109900),
    "OnePlus 12":           (54999,  64999),
    "Bose QC45":            (24900,  29900),
    "Dyson V15 Vacuum":     (49900,  59900),
    "Nintendo Switch OLED": (29999,  34999),
    "Canon EOS R6 Mark II": (219000, 259000),
    "Kindle Paperwhite":    (13999,  16999),
    "Apple Watch Ultra 2":  (79900,  89900),
    "JBL Flip 6":           (8999,   12999),
}

CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat",
]

CATEGORY_MAP = {
    "MacBook Pro 16\"": "Laptops",
    "Dell XPS 15": "Laptops",
    "iPhone 15 Pro Max": "Phones",
    "Samsung Galaxy S24 Ultra": "Phones",
    "OnePlus 12": "Phones",
    "Sony WH-1000XM5": "Audio",
    "Bose QC45": "Audio",
    "JBL Flip 6": "Audio",
    "iPad Pro 12.9\"": "Tablets",
    "Kindle Paperwhite": "Tablets",
    "LG OLED 55\" TV": "TVs",
    "Nintendo Switch OLED": "Gaming",
    "Canon EOS R6 Mark II": "Cameras",
    "Dyson V15 Vacuum": "Appliances",
    "Apple Watch Ultra 2": "Wearables",
}

WEATHER_API_KEY_NAME = "WEATHER_API_KEY"   # key name inside st.secrets

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "sales_df" not in st.session_state:
    st.session_state.sales_df = pd.DataFrame(
        columns=["Timestamp", "Product", "Category", "Price", "City"]
    )
if "last_generated" not in st.session_state:
    st.session_state.last_generated = time.time() - 35   # trigger immediately
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}
if "weather_last_fetched" not in st.session_state:
    st.session_state.weather_last_fetched = 0
if "total_revenue_prev" not in st.session_state:
    st.session_state.total_revenue_prev = 0
if "order_vol_prev" not in st.session_state:
    st.session_state.order_vol_prev = 0

# ─────────────────────────────────────────────
#  SALE GENERATOR
# ─────────────────────────────────────────────
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    lo, hi = PRODUCTS[product]
    # add small random variance and occasional discount/surge
    base = random.randint(lo, hi)
    multiplier = random.choice([0.88, 0.92, 0.95, 1.0, 1.0, 1.0, 1.05])
    price = int(base * multiplier)
    city = random.choices(
        CITIES,
        weights=[20, 18, 15, 12, 10, 8, 7, 4, 3, 3],  # Mumbai/Delhi/Bengaluru busier
        k=1
    )[0]
    return {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Product": product,
        "Category": CATEGORY_MAP[product],
        "Price": price,
        "City": city,
    }

# ─────────────────────────────────────────────
#  WEATHER FETCHER
# ─────────────────────────────────────────────
def get_weather(city: str) -> dict:
    """Return weather info dict for a city. Caches for 10 min."""
    cache = st.session_state.weather_cache
    if city in cache and (time.time() - cache[city]["fetched_at"]) < 600:
        return cache[city]

    try:
        api_key = st.secrets[WEATHER_API_KEY_NAME]
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},IN&appid={api_key}&units=metric"
        )
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            desc = d["weather"][0]["description"].lower()
            temp = d["main"]["temp"]
            feels = d["main"]["feels_like"]
            icon  = d["weather"][0]["icon"]
            result = {
                "desc": desc, "temp": temp, "feels": feels,
                "icon": icon, "fetched_at": time.time(), "ok": True,
            }
            cache[city] = result
            return result
    except Exception:
        pass

    # fallback
    fallback = {
        "desc": "data unavailable", "temp": None, "feels": None,
        "icon": "01d", "fetched_at": time.time(), "ok": False,
    }
    cache[city] = fallback
    return fallback


def weather_condition(w: dict) -> str:
    # ADD THIS LINE: check if dictionary is empty or missing the 'ok' key
    if not w or "ok" not in w or not w["ok"]:
        return "unknown"
        
    d = w.get("desc", "")
    t = w.get("temp", 25)
    
    if any(x in d for x in ["rain", "drizzle", "shower", "thunderstorm"]):
        return "rain"
    if t >= 35:
        return "heat"
    if any(x in d for x in ["cloud", "overcast", "mist", "fog", "haze", "smoke"]):
        return "cloudy"
    return "clear"

def weather_pill_html(city: str, w: dict) -> str:
    cond = weather_condition(w)
    if cond == "rain":
        cls, icon_txt = "w-rain",  f"🌧 {city}"
    elif cond == "heat":
        cls, icon_txt = "w-heat",  f"🔥 {city}"
    elif cond == "cloudy":
        cls, icon_txt = "w-cloud", f"☁ {city}"
    elif cond == "clear":
        cls, icon_txt = "w-clear", f"☀ {city}"
    else:
        cls, icon_txt = "w-cloud", f"❓ {city}"

    temp_str = f" {w['temp']:.0f}°C" if w["temp"] is not None else ""
    return f'<span class="weather-pill {cls}">{icon_txt}{temp_str}</span>'

# ─────────────────────────────────────────────
#  TRIGGER SALE IF 30 s ELAPSED
# ─────────────────────────────────────────────
now = time.time()
if now - st.session_state.last_generated >= 30:
    n_sales = random.randint(1, 3)   # sometimes 2-3 orders arrive at once
    for _ in range(n_sales):
        new_row = generate_sale()
        st.session_state.sales_df = pd.concat(
            [st.session_state.sales_df, pd.DataFrame([new_row])],
            ignore_index=True,
        )
    st.session_state.last_generated = now
    # keep last 500 rows
    if len(st.session_state.sales_df) > 500:
        st.session_state.sales_df = st.session_state.sales_df.tail(500).reset_index(drop=True)

df = st.session_state.sales_df.copy()

# ─────────────────────────────────────────────
#  COMPUTED METRICS
# ─────────────────────────────────────────────
total_revenue   = df["Price"].sum() if len(df) else 0
order_volume    = len(df)
avg_order_value = int(df["Price"].mean()) if len(df) else 0
top_city        = df["City"].value_counts().idxmax() if len(df) else "—"
top_product     = df["Product"].value_counts().idxmax() if len(df) else "—"
top_category    = df["Category"].value_counts().idxmax() if len(df) else "—"

rev_delta  = total_revenue - st.session_state.total_revenue_prev
vol_delta  = order_volume  - st.session_state.order_vol_prev
st.session_state.total_revenue_prev = total_revenue
st.session_state.order_vol_prev     = order_volume

# ─────────────────────────────────────────────
#  WEATHER FOR ACTIVE CITIES
# ─────────────────────────────────────────────
active_cities = df["City"].unique().tolist() if len(df) else CITIES[:5]
weather_data  = {city: get_weather(city) for city in active_cities[:8]}

# ─────────────────────────────────────────────
#  WEATHER IMPACT ANALYSIS
# ─────────────────────────────────────────────
rain_cities  = [c for c, w in weather_data.items() if weather_condition(w) == "rain"]
heat_cities  = [c for c, w in weather_data.items() if weather_condition(w) == "heat"]
clear_cities = [c for c, w in weather_data.items() if weather_condition(w) == "clear"]

def weather_impact_alert():
    alerts = []
    if len(df) == 0:
        return alerts
    for city in rain_cities:
        city_rev = df[df["City"] == city]["Price"].sum()
        avg_city_rev = df.groupby("City")["Price"].sum().mean()
        if city_rev < avg_city_rev * 0.85:
            alerts.append(("warn", f"🌧 RAIN IMPACT — {city}: Revenue ₹{city_rev:,.0f} is {((avg_city_rev-city_rev)/avg_city_rev*100):.0f}% below average. Consider logistics delay buffer."))
        else:
            alerts.append(("good", f"🌧 Rain in {city} not impacting sales — ₹{city_rev:,.0f} (steady)."))
    for city in heat_cities:
        city_orders = len(df[df["City"] == city])
        avg_orders  = len(df) / max(df["City"].nunique(), 1)
        if city_orders > avg_orders * 1.1:
            alerts.append(("good", f"🔥 HEAT SURGE — {city}: {city_orders} orders (+{((city_orders/avg_orders-1)*100):.0f}% vs avg). AC/Cooling products likely driving demand."))
    return alerts

alerts = weather_impact_alert()

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
col_logo, col_time, col_status = st.columns([3, 2, 2])
with col_logo:
    st.markdown("""
    <div class="war-room-title">⚡ SALES WAR ROOM</div>
    <div class="war-room-sub">COMMAND CENTER · REAL-TIME INTELLIGENCE FEED</div>
    """, unsafe_allow_html=True)
with col_time:
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:.7rem;
         color:#4a9abb; letter-spacing:.15em; text-align:center; margin-top:.6rem;">
    LAST SYNC<br>
    <span style="font-size:1.3rem; color:#00dcff;">{datetime.now().strftime('%H:%M:%S')}</span><br>
    {datetime.now().strftime('%d %b %Y')}
    </div>
    """, unsafe_allow_html=True)
with col_status:
    next_refresh = max(0, 30 - int(time.time() - st.session_state.last_generated))
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:.7rem;
         color:#4a9abb; letter-spacing:.15em; text-align:center; margin-top:.6rem;">
    NEXT ORDER IN<br>
    <span class="blink" style="font-size:1.3rem; color:#00ff9d;">{next_refresh}s</span><br>
    <span style="color:#00ff9d;">● LIVE</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TICKER (last 5 sales)
# ─────────────────────────────────────────────
if len(df) > 0:
    recent = df.tail(8)
    items  = "  ◆  ".join(
        f"[{r.Timestamp}]  {r.City.upper()} — {r.Product} @ ₹{r.Price:,.0f}"
        for _, r in recent.iterrows()
    )
    st.markdown(f"""
    <div class="ticker-wrap">
      <div class="ticker-inner">
        ◆ LIVE SALES FEED ◆&nbsp;&nbsp;&nbsp;{items}&nbsp;&nbsp;&nbsp;◆ LIVE SALES FEED ◆&nbsp;&nbsp;&nbsp;{items}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(label, value, delta=None, delta_type="neut", is_currency=False):
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        # Format the delta display here
        fmt_delta = f"₹{abs(delta):,}" if is_currency else f"{abs(delta):,}"
        delta_html = f'<div class="kpi-delta {delta_type}">{arrow} {fmt_delta}</div>'
    
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>
    """

with k1:
    rev_d_type = "up" if rev_delta >= 0 else "down"
    st.markdown(kpi(
        "Total Revenue", 
        f"₹{total_revenue/1e5:.2f}L", 
        rev_delta,      # Pass number, not f-string
        rev_d_type,
        is_currency=True
    ), unsafe_allow_html=True)

with k2:
    vol_d_type = "up" if vol_delta >= 0 else "down"
    st.markdown(kpi(
        "Order Volume", 
        f"{order_volume:,}", 
        vol_delta,      # Pass number, not f-string
        vol_d_type
    ), unsafe_allow_html=True)
with k3:
    st.markdown(kpi("Avg Order Value", f"₹{avg_order_value:,}"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi("Hot City", top_city), unsafe_allow_html=True)
with k5:
    st.markdown(kpi("Top Category", top_category), unsafe_allow_html=True)

st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  WEATHER STATUS BAR
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// CITY WEATHER STATUS</div>', unsafe_allow_html=True)
pills_html = "".join(weather_pill_html(c, w) for c, w in weather_data.items())
st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  WEATHER IMPACT ALERTS
# ─────────────────────────────────────────────
if alerts:
    st.markdown('<div class="section-hdr">// WEATHER IMPACT ANALYSIS</div>', unsafe_allow_html=True)
    for typ, msg in alerts:
        css = "alert-banner" if typ == "warn" else "good-banner"
        st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
elif len(df) > 0:
    st.markdown('<div class="section-hdr">// WEATHER IMPACT ANALYSIS</div>', unsafe_allow_html=True)
    # Show basic summary even without alerts
    weather_summary_parts = []
    for city, w in weather_data.items():
        cond = weather_condition(w)
        city_rev = df[df["City"] == city]["Price"].sum() if city in df["City"].values else 0
        city_orders = len(df[df["City"] == city])
        temp_str = f"{w['temp']:.0f}°C" if w.get("temp") is not None else "N/A"
        weather_summary_parts.append(
            f"{city}: {cond.upper()} {temp_str} | {city_orders} orders | ₹{city_rev:,.0f}"
        )
    for part in weather_summary_parts[:4]:
        st.markdown(f'<div class="good-banner">📊 {part}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CHARTS  ROW 1
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// REVENUE INTELLIGENCE</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns([3, 2])

CHART_BG  = "rgba(0,0,0,0)"
GRID_COL  = "rgba(0,220,255,0.07)"
FONT_MONO = "Share Tech Mono"
ACCENT    = "#00dcff"
GREEN     = "#00ff9d"
ORANGE    = "#ff9940"
RED       = "#ff4060"

with chart_col1:
    # Revenue over time (rolling 20 orders)
    if len(df) >= 3:
        df_time = df.copy()
        df_time["OrderNum"] = range(1, len(df_time)+1)
        df_time["CumRevenue"] = df_time["Price"].cumsum()
        df_time["RollingAvg"] = df_time["Price"].rolling(5, min_periods=1).mean()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=df_time["OrderNum"], y=df_time["CumRevenue"],
            fill="tozeroy", fillcolor="rgba(0,220,255,0.05)",
            line=dict(color=ACCENT, width=2),
            name="Cumulative Revenue",
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=df_time["OrderNum"], y=df_time["RollingAvg"],
            line=dict(color=GREEN, width=1.5, dash="dot"),
            name="Rolling Avg Order",
        ), secondary_y=True)

        fig.update_layout(
            title=dict(text="CUMULATIVE REVENUE vs ROLLING AVG ORDER VALUE",
                       font=dict(family=FONT_MONO, size=11, color="#4a9abb")),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            legend=dict(font=dict(family=FONT_MONO, size=9, color="#4a9abb"),
                        bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=35, b=0),
            height=260,
            xaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#4a9abb"),
                       title="", zeroline=False),
            yaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#4a9abb"),
                       tickprefix="₹", zeroline=False),
            yaxis2=dict(gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(family=FONT_MONO, size=8, color=GREEN),
                        tickprefix="₹", zeroline=False),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div style="height:260px; display:flex; align-items:center; justify-content:center; color:#4a9abb; font-family:\'Share Tech Mono\',monospace; font-size:.8rem;">AWAITING DATA...</div>', unsafe_allow_html=True)

with chart_col2:
    # Revenue by category donut
    if len(df) > 0:
        cat_rev = df.groupby("Category")["Price"].sum().reset_index()
        DONUT_COLORS = [ACCENT, GREEN, ORANGE, RED, "#aa44ff", "#ffdd00", "#ff66cc"]
        fig2 = go.Figure(go.Pie(
            labels=cat_rev["Category"], values=cat_rev["Price"],
            hole=.55,
            marker=dict(colors=DONUT_COLORS[:len(cat_rev)],
                        line=dict(color="#030b14", width=2)),
            textfont=dict(family=FONT_MONO, size=9, color="#c8d8e8"),
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig2.update_layout(
            title=dict(text="REVENUE BY CATEGORY",
                       font=dict(family=FONT_MONO, size=11, color="#4a9abb")),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            legend=dict(font=dict(family=FONT_MONO, size=9, color="#4a9abb"),
                        bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=35, b=0),
            height=260,
            annotations=[dict(text=f"₹{total_revenue/1e5:.1f}L",
                              x=.5, y=.5, showarrow=False,
                              font=dict(family="Orbitron", size=14, color=ACCENT))]
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
#  CHARTS  ROW 2
# ─────────────────────────────────────────────
chart_col3, chart_col4, chart_col5 = st.columns([2, 2, 2])

with chart_col3:
    # Top products bar
    if len(df) > 0:
        prod_rev = df.groupby("Product")["Price"].sum().sort_values(ascending=True).tail(8)
        short_labels = [p.replace('"', '').replace("'", '')[:18] for p in prod_rev.index]
        fig3 = go.Figure(go.Bar(
            x=prod_rev.values, y=short_labels,
            orientation="h",
            marker=dict(
                color=prod_rev.values,
                colorscale=[[0, "rgba(0,140,200,0.6)"], [1, "rgba(0,220,255,0.9)"]],
                line=dict(color="rgba(0,220,255,0.3)", width=1),
            ),
            text=[f"₹{v:,.0f}" for v in prod_rev.values],
            textposition="outside",
            textfont=dict(family=FONT_MONO, size=8, color="#4a9abb"),
            hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
        ))
        fig3.update_layout(
            title=dict(text="TOP PRODUCTS BY REVENUE",
                       font=dict(family=FONT_MONO, size=11, color="#4a9abb")),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            margin=dict(l=0, r=80, t=35, b=0), height=280,
            xaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#4a9abb"),
                       tickprefix="₹", zeroline=False),
            yaxis=dict(tickfont=dict(family=FONT_MONO, size=8, color="#c8d8e8"),
                       gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with chart_col4:
    # City heatmap (orders)
    if len(df) > 0:
        city_orders = df.groupby("City").size().reset_index(name="Orders")
        city_rev    = df.groupby("City")["Price"].sum().reset_index(name="Revenue")
        city_merged = city_orders.merge(city_rev, on="City").sort_values("Revenue", ascending=False)

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=city_merged["City"], y=city_merged["Revenue"],
            name="Revenue",
            marker=dict(color=city_merged["Revenue"],
                        colorscale=[[0,"rgba(0,80,120,0.6)"],[1,"rgba(0,255,160,0.85)"]],
                        line=dict(color="rgba(0,255,160,0.3)", width=1)),
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        ))
        # overlay weather icons
        for _, row in city_merged.iterrows():
            w = weather_data.get(row["City"], {})
            cond = weather_condition(w) if w else "unknown"
            icon_map = {"rain": "🌧", "heat": "🔥", "clear": "☀", "cloudy": "☁", "unknown": "❓"}
            fig4.add_annotation(
                x=row["City"], y=row["Revenue"],
                text=icon_map[cond], showarrow=False,
                yshift=14, font=dict(size=13),
            )

        fig4.update_layout(
            title=dict(text="CITY REVENUE + WEATHER",
                       font=dict(family=FONT_MONO, size=11, color="#4a9abb")),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            margin=dict(l=0, r=0, t=35, b=0), height=280,
            xaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#c8d8e8")),
            yaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#4a9abb"),
                       tickprefix="₹", zeroline=False),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

with chart_col5:
    # Orders per 30-sec bucket (velocity)
    if len(df) >= 5:
        # bucket by index chunks of 5
        df_vel = df.copy()
        df_vel["Bucket"] = df_vel.index // 5
        vel = df_vel.groupby("Bucket").agg(
            Orders=("Product", "count"),
            Revenue=("Price", "sum"),
        ).reset_index()
        vel["Label"] = vel["Bucket"].apply(lambda x: f"B{x+1}")

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=vel["Label"], y=vel["Orders"],
            fill="tozeroy", fillcolor="rgba(255,153,64,0.08)",
            line=dict(color=ORANGE, width=2),
            marker=dict(size=5, color=ORANGE),
            name="Order Velocity",
        ))
        fig5.update_layout(
            title=dict(text="ORDER VELOCITY (PER BATCH)",
                       font=dict(family=FONT_MONO, size=11, color="#4a9abb")),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            margin=dict(l=0, r=0, t=35, b=0), height=280,
            xaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#4a9abb")),
            yaxis=dict(gridcolor=GRID_COL, tickfont=dict(family=FONT_MONO, size=8, color="#4a9abb"),
                       zeroline=False),
            showlegend=False,
        )
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div style="height:280px; display:flex; align-items:center; justify-content:center; color:#4a9abb; font-family:\'Share Tech Mono\',monospace; font-size:.8rem;">BUILDING VELOCITY DATA...</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LIVE FEED TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-hdr">// LIVE TRANSACTION FEED</div>', unsafe_allow_html=True)
feed_col, detail_col = st.columns([3, 2])

with feed_col:
    if len(df) > 0:
        display_df = df.tail(15).sort_index(ascending=False).copy()
        display_df["Price"] = display_df["Price"].apply(lambda x: f"₹{x:,.0f}")
        # add weather column
        display_df["Weather"] = display_df["City"].apply(
            lambda c: {"rain": "🌧 Rain", "heat": "🔥 Heat",
                       "clear": "☀ Clear", "cloudy": "☁ Cloudy",
                       "unknown": "❓"}.get(weather_condition(weather_data.get(c, {})), "❓")
        )
        st.dataframe(
            display_df[["Timestamp", "Product", "Category", "Price", "City", "Weather"]],
            use_container_width=True,
            hide_index=True,
            height=340,
        )
    else:
        st.markdown('<div style="color:#4a9abb; font-family:\'Share Tech Mono\',monospace; font-size:.8rem; padding:1rem;">NO TRANSACTIONS YET — AWAITING FIRST CYCLE...</div>', unsafe_allow_html=True)

with detail_col:
    # Category breakdown table
    if len(df) > 0:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace; font-size:.7rem; color:#4a9abb; letter-spacing:.15em; margin-bottom:.5rem;">CATEGORY BREAKDOWN</div>', unsafe_allow_html=True)
        cat_summary = df.groupby("Category").agg(
            Orders=("Product","count"),
            Revenue=("Price","sum"),
            AvgOrder=("Price","mean"),
        ).sort_values("Revenue", ascending=False).reset_index()
        cat_summary["Revenue"]  = cat_summary["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        cat_summary["AvgOrder"] = cat_summary["AvgOrder"].apply(lambda x: f"₹{int(x):,}")
        st.dataframe(cat_summary, use_container_width=True, hide_index=True, height=150)

        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace; font-size:.7rem; color:#4a9abb; letter-spacing:.15em; margin:1rem 0 .5rem;">CITY LEADERBOARD</div>', unsafe_allow_html=True)
        city_summary = df.groupby("City").agg(
            Orders=("Product","count"),
            Revenue=("Price","sum"),
        ).sort_values("Revenue", ascending=False).reset_index()
        city_summary["Revenue"] = city_summary["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        city_summary.insert(0, "Rank", [f"#{i+1}" for i in range(len(city_summary))])
        st.dataframe(city_summary, use_container_width=True, hide_index=True, height=160)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:1.5rem; border-top:1px solid rgba(0,220,255,.1);
     padding-top:.6rem; text-align:center;
     font-family:'Share Tech Mono',monospace; font-size:.65rem;
     color:rgba(74,154,187,.5); letter-spacing:.15em;">
SALES WAR ROOM  ·  AUTO-REFRESH 30s  ·  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
·  POWERED BY OPENWEATHERMAP  ·  STREAMLIT CLOUD
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  AUTO REFRESH  (30 s)
# ─────────────────────────────────────────────
time.sleep(30)
st.rerun()