import streamlit as st
import pandas as pd
import random
import time
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SalesPulse Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --accent: #00ff88;
    --accent2: #ff6b35;
    --accent3: #7c3aed;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --rain: #38bdf8;
    --heat: #fb923c;
    --border: rgba(255,255,255,0.08);
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Metric cards */
.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent3));
}
.metric-label {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
    font-family: 'Space Mono', monospace;
}
.metric-value {
    font-size: 36px;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 4px;
}
.metric-sub {
    font-size: 12px;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
}
.metric-delta-pos { color: var(--accent); }
.metric-delta-neg { color: var(--accent2); }

/* Weather badge */
.weather-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-rain {
    background: rgba(56,189,248,0.15);
    border: 1px solid rgba(56,189,248,0.4);
    color: var(--rain);
}
.badge-heat {
    background: rgba(251,146,60,0.15);
    border: 1px solid rgba(251,146,60,0.4);
    color: var(--heat);
}
.badge-normal {
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    color: var(--accent);
}

/* Section header */
.section-title {
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

/* Sale feed item */
.sale-item {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    transition: border-color 0.2s;
}
.sale-item:first-child {
    border-color: rgba(0,255,136,0.4);
    background: rgba(0,255,136,0.04);
}
.sale-product { color: var(--text); font-weight: 700; }
.sale-city { color: var(--muted); }
.sale-price { color: var(--accent); font-weight: 700; }
.sale-time { color: var(--muted); font-size: 10px; }

/* Alert banner */
.alert-rain {
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--rain);
    font-family: 'Space Mono', monospace;
}
.alert-heat {
    background: rgba(251,146,60,0.08);
    border: 1px solid rgba(251,146,60,0.3);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--heat);
    font-family: 'Space Mono', monospace;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Pulse animation for live indicator */
@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.3); }
    100% { opacity: 1; transform: scale(1); }
}
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 1.5s infinite;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ──────────────────────────────────────────────────────────────
PRODUCTS = [
    ("Laptop Pro X1", 1299), ("Wireless Earbuds", 149), ("Smart Watch Series 5", 399),
    ("Gaming Chair", 449), ("4K Monitor", 599), ("Mechanical Keyboard", 179),
    ("Webcam HD", 89), ("USB-C Hub", 59), ("Portable SSD 1TB", 129),
    ("Standing Desk", 799), ("Noise Cancelling Headphones", 349), ("iPad Pro", 1099),
    ("RTX Graphics Card", 849), ("NAS Storage", 499), ("Smart Speaker", 129),
]

CITIES = [
    "Mumbai", "Delhi", "Hyderabad", "Bangalore", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
]

CITY_COORDS = {
    "Mumbai":    (19.0760, 72.8777),
    "Delhi":     (28.6139, 77.2090),
    "Hyderabad": (17.3850, 78.4867),
    "Bangalore": (12.9716, 77.5946),
    "Chennai":   (13.0827, 80.2707),
    "Kolkata":   (22.5726, 88.3639),
    "Pune":      (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur":    (26.9124, 75.7873),
    "Surat":     (21.1702, 72.8311),
}

WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "")

# ─── SESSION STATE INIT ──────────────────────────────────────────────────────
if "sales" not in st.session_state:
    st.session_state.sales = []
if "last_generated" not in st.session_state:
    st.session_state.last_generated = time.time() - 31
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}
if "weather_last_fetch" not in st.session_state:
    st.session_state.weather_last_fetch = 0
if "total_revenue_start" not in st.session_state:
    st.session_state.total_revenue_start = 0.0

# ─── SALE GENERATOR ─────────────────────────────────────────────────────────
def generate_sale():
    product, base_price = random.choice(PRODUCTS)
    price = round(base_price * random.uniform(0.85, 1.15), 2)
    city = random.choice(CITIES)
    return {
        "product": product,
        "price": price,
        "city": city,
        "timestamp": datetime.now(),
    }

def maybe_generate_sale():
    now = time.time()
    if now - st.session_state.last_generated >= 30:
        sale = generate_sale()
        st.session_state.sales.insert(0, sale)
        if len(st.session_state.sales) > 200:
            st.session_state.sales = st.session_state.sales[:200]
        st.session_state.last_generated = now
        return True
    return False

# ─── WEATHER FETCHER ────────────────────────────────────────────────────────
def fetch_weather(city):
    if not WEATHER_API_KEY:
        return None
    now = time.time()
    cache = st.session_state.weather_cache
    # Cache for 10 minutes
    if city in cache and now - cache[city].get("fetched_at", 0) < 600:
        return cache[city]
    try:
        lat, lon = CITY_COORDS[city]
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        )
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            result = {
                "temp": round(d["main"]["temp"], 1),
                "description": d["weather"][0]["description"].lower(),
                "main": d["weather"][0]["main"].lower(),
                "humidity": d["main"]["humidity"],
                "fetched_at": now,
            }
            st.session_state.weather_cache[city] = result
            return result
    except Exception:
        pass
    return None

def get_weather_condition(weather):
    """Return 'rain', 'heat', or 'normal'"""
    if not weather:
        return "normal"
    if any(w in weather["main"] for w in ["rain", "drizzle", "thunderstorm"]):
        return "rain"
    if weather["temp"] >= 38:
        return "heat"
    return "normal"

def weather_sales_impact(condition):
    if condition == "rain":
        return "📉 Rain may boost indoor electronics & delivery orders"
    if condition == "heat":
        return "📈 Heat wave likely driving cooling products & beverages"
    return "✅ Normal conditions — steady demand expected"

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='padding: 16px 0 8px;'>
            <div style='font-family:Syne,sans-serif; font-size:22px; font-weight:800; color:#e8e8f0;'>
                ⚡ SalesPulse
            </div>
            <div style='font-family:Space Mono,monospace; font-size:11px; color:#6b6b80; letter-spacing:2px; margin-top:4px;'>
                LIVE DASHBOARD v1.0
            </div>
        </div>
        <hr style='border-color:rgba(255,255,255,0.08); margin: 8px 0 20px;'/>
    """, unsafe_allow_html=True)

    refresh_rate = st.slider("⏱ Auto-refresh (seconds)", 5, 60, 10)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)

    all_cities = ["All"] + CITIES
    selected_city = st.selectbox("🌆 City", all_cities)

    all_products = ["All"] + sorted(set(p for p, _ in PRODUCTS))
    selected_product = st.selectbox("📦 Product", all_products)

    min_price, max_price = st.slider("💰 Price Range (₹)", 0, 2000, (0, 2000), step=50)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Time Window</div>", unsafe_allow_html=True)
    time_window = st.selectbox("Show sales from last", ["5 minutes", "15 minutes", "30 minutes", "1 hour", "All"])

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🗑 Clear Sales Data", use_container_width=True):
        st.session_state.sales = []
        st.session_state.total_revenue_start = 0

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin-top:20px;'/>", unsafe_allow_html=True)
    api_status = "🟢 Connected" if WEATHER_API_KEY else "🔴 No API Key"
    st.markdown(f"<div style='font-size:11px; color:#6b6b80; font-family:Space Mono,monospace;'>Weather API: {api_status}</div>", unsafe_allow_html=True)

# ─── GENERATE SALE ───────────────────────────────────────────────────────────
maybe_generate_sale()

# Pre-populate with some initial data if empty
if not st.session_state.sales:
    for i in range(15):
        sale = generate_sale()
        sale["timestamp"] = datetime.now() - timedelta(minutes=random.randint(1, 59))
        st.session_state.sales.append(sale)
    st.session_state.sales.sort(key=lambda x: x["timestamp"], reverse=True)

# ─── FILTER DATA ────────────────────────────────────────────────────────────
df_all = pd.DataFrame(st.session_state.sales)

# Time window filter
def apply_time_filter(df, window):
    if window == "All" or df.empty:
        return df
    minutes = {"5 minutes": 5, "15 minutes": 15, "30 minutes": 30, "1 hour": 60}[window]
    cutoff = datetime.now() - timedelta(minutes=minutes)
    return df[df["timestamp"] >= cutoff]

df = apply_time_filter(df_all, time_window)
if not df.empty:
    if selected_city != "All":
        df = df[df["city"] == selected_city]
    if selected_product != "All":
        df = df[df["product"] == selected_product]
    df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]

# ─── HEADER ─────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
        <div style='padding: 8px 0 4px;'>
            <h1 style='font-family:Syne,sans-serif; font-size:32px; font-weight:800;
                       color:#e8e8f0; margin:0; line-height:1;'>
                <span class='live-dot'></span>Sales Intelligence Hub
            </h1>
            <p style='font-family:Space Mono,monospace; font-size:11px; color:#6b6b80;
                      letter-spacing:2px; margin:6px 0 0;'>
                REAL-TIME · AUTO-REFRESH · WEATHER-AWARE
            </p>
        </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
        <div style='text-align:right; padding-top:12px;'>
            <div style='font-family:Space Mono,monospace; font-size:11px; color:#6b6b80;'>
                LAST UPDATED
            </div>
            <div style='font-family:Space Mono,monospace; font-size:13px; color:#00ff88;'>
                {datetime.now().strftime('%H:%M:%S')}
            </div>
            <div style='font-family:Space Mono,monospace; font-size:10px; color:#6b6b80; margin-top:2px;'>
                Next sale in ~{max(0, 30 - int(time.time() - st.session_state.last_generated))}s
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin: 12px 0 20px;'/>", unsafe_allow_html=True)

# ─── KPI METRICS ────────────────────────────────────────────────────────────
total_revenue = df["price"].sum() if not df.empty else 0.0
order_volume = len(df)
avg_order = df["price"].mean() if not df.empty else 0.0
top_city = df["city"].value_counts().idxmax() if not df.empty else "—"
top_product = df["product"].value_counts().idxmax() if not df.empty else "—"

# Last-sale comparison for delta
last_sale_price = df["price"].iloc[0] if not df.empty else 0

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Total Revenue</div>
        <div class='metric-value'>₹{total_revenue:,.0f}</div>
        <div class='metric-sub'>filtered window</div>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Order Volume</div>
        <div class='metric-value'>{order_volume}</div>
        <div class='metric-sub'>transactions</div>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Avg Order Value</div>
        <div class='metric-value'>₹{avg_order:,.0f}</div>
        <div class='metric-sub'>per transaction</div>
    </div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Top City</div>
        <div class='metric-value' style='font-size:24px;'>{top_city}</div>
        <div class='metric-sub'>by order count</div>
    </div>""", unsafe_allow_html=True)

with m5:
    rev_all = df_all["price"].sum() if not df_all.empty else 0
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>All-Time Revenue</div>
        <div class='metric-value'>₹{rev_all:,.0f}</div>
        <div class='metric-sub'>{len(df_all)} total orders</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ─── MAIN CONTENT: CHARTS + FEED ────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Revenue over time
    st.markdown("<div class='section-title'>Revenue Timeline</div>", unsafe_allow_html=True)
    if not df.empty and len(df) > 1:
        df_time = df.copy().sort_values("timestamp")
        df_time["cumulative_revenue"] = df_time["price"].cumsum()
        df_time["minute"] = df_time["timestamp"].dt.floor("1min")

        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=df_time["timestamp"],
            y=df_time["cumulative_revenue"],
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(0,255,136,0.06)",
            line=dict(color="#00ff88", width=2),
            hovertemplate="<b>₹%{y:,.0f}</b><br>%{x|%H:%M:%S}<extra></extra>",
        ))
        fig_timeline.add_trace(go.Scatter(
            x=df_time["timestamp"],
            y=df_time["price"],
            mode="markers",
            marker=dict(color="#7c3aed", size=6, opacity=0.7),
            name="Sale",
            hovertemplate="<b>₹%{y:.0f}</b> sale<br>%{x|%H:%M:%S}<extra></extra>",
        ))
        fig_timeline.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#6b6b80", size=10),
            margin=dict(l=0, r=0, t=10, b=0),
            height=220,
            showlegend=False,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(size=9)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickprefix="₹", tickfont=dict(size=9)),
            hovermode="x unified",
        )
        st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough data for timeline. Sales accumulating...")

    # Revenue by city + product side by side
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("<div class='section-title'>Revenue by City</div>", unsafe_allow_html=True)
        if not df.empty:
            city_rev = df.groupby("city")["price"].sum().sort_values(ascending=True).reset_index()
            fig_city = go.Figure(go.Bar(
                x=city_rev["price"],
                y=city_rev["city"],
                orientation="h",
                marker=dict(
                    color=city_rev["price"],
                    colorscale=[[0, "#1a1a26"], [0.5, "#7c3aed"], [1, "#00ff88"]],
                    showscale=False,
                ),
                hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
            ))
            fig_city.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Space Mono", color="#6b6b80", size=9),
                margin=dict(l=0, r=0, t=5, b=0), height=240,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="₹", tickfont=dict(size=8)),
                yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=9)),
            )
            st.plotly_chart(fig_city, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        st.markdown("<div class='section-title'>Top Products</div>", unsafe_allow_html=True)
        if not df.empty:
            prod_rev = df.groupby("product")["price"].sum().sort_values(ascending=False).head(8).reset_index()
            prod_rev["short"] = prod_rev["product"].apply(lambda x: x[:14] + "…" if len(x) > 14 else x)
            fig_prod = go.Figure(go.Bar(
                x=prod_rev["short"],
                y=prod_rev["price"],
                marker=dict(
                    color=prod_rev["price"],
                    colorscale=[[0, "#1a1a26"], [0.5, "#ff6b35"], [1, "#7c3aed"]],
                    showscale=False,
                ),
                hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
            ))
            fig_prod.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Space Mono", color="#6b6b80", size=9),
                margin=dict(l=0, r=0, t=5, b=0), height=240,
                xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=8), tickangle=-30),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="₹", tickfont=dict(size=8)),
            )
            st.plotly_chart(fig_prod, use_container_width=True, config={"displayModeBar": False})

with col_right:
    st.markdown("<div class='section-title'>🔴 Live Sale Feed</div>", unsafe_allow_html=True)
    feed_df = df.head(12) if not df.empty else pd.DataFrame()
    if not feed_df.empty:
        for _, row in feed_df.iterrows():
            mins_ago = int((datetime.now() - row["timestamp"]).total_seconds() / 60)
            time_str = f"{mins_ago}m ago" if mins_ago > 0 else "just now"
            st.markdown(f"""
            <div class='sale-item'>
                <div>
                    <div class='sale-product'>{row['product'][:18]}</div>
                    <div class='sale-city'>{row['city']} · {time_str}</div>
                </div>
                <div class='sale-price'>₹{row['price']:,.0f}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No sales in this window.")

st.markdown("<br/>", unsafe_allow_html=True)

# ─── WEATHER SECTION ─────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>🌦 Weather Impact Analysis</div>", unsafe_allow_html=True)

cities_to_show = CITIES if selected_city == "All" else [selected_city]

weather_rows = []
for city in cities_to_show:
    w = fetch_weather(city)
    condition = get_weather_condition(w)
    weather_rows.append({
        "city": city,
        "weather": w,
        "condition": condition,
    })

# Show alerts for rain/heat cities
rain_cities = [r["city"] for r in weather_rows if r["condition"] == "rain"]
heat_cities = [r["city"] for r in weather_rows if r["condition"] == "heat"]

if rain_cities:
    st.markdown(f"""
    <div class='alert-rain'>
        🌧 <b>RAIN ALERT</b> — {', '.join(rain_cities)}<br>
        <span style='font-size:11px; opacity:0.8;'>Expect higher demand for indoor electronics, umbrellas & delivery orders. Consider targeted push notifications.</span>
    </div>""", unsafe_allow_html=True)

if heat_cities:
    st.markdown(f"""
    <div class='alert-heat'>
        🌡 <b>HEAT ALERT</b> — {', '.join(heat_cities)}<br>
        <span style='font-size:11px; opacity:0.8;'>Temperature ≥ 38°C detected. Cooling products & beverages see 2-3× normal demand spikes.</span>
    </div>""", unsafe_allow_html=True)

# Weather grid
w_cols = st.columns(min(len(cities_to_show), 5))
for i, row in enumerate(weather_rows[:10]):
    with w_cols[i % len(w_cols)]:
        city = row["city"]
        w = row["weather"]
        cond = row["condition"]

        if w:
            badge_class = f"badge-{cond}"
            badge_icon = "🌧" if cond == "rain" else "🔥" if cond == "heat" else "✅"
            badge_text = cond.upper()
            temp_str = f"{w['temp']}°C"
            desc_str = w["description"].title()
            humidity_str = f"💧 {w['humidity']}%"
            impact = weather_sales_impact(cond)
        else:
            badge_class = "badge-normal"
            badge_icon = "❓"
            badge_text = "N/A"
            temp_str = "—"
            desc_str = "No data"
            humidity_str = ""
            impact = "Weather API not configured"

        city_rev = df[df["city"] == city]["price"].sum() if not df.empty else 0
        city_orders = len(df[df["city"] == city]) if not df.empty else 0

        st.markdown(f"""
        <div class='metric-card' style='margin-bottom:12px;'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;'>
                <div style='font-family:Syne,sans-serif; font-weight:700; font-size:14px;'>{city}</div>
                <span class='weather-badge {badge_class}'>{badge_icon} {badge_text}</span>
            </div>
            <div style='font-family:Space Mono,monospace; font-size:20px; font-weight:700; color:{"#38bdf8" if cond=="rain" else "#fb923c" if cond=="heat" else "#00ff88"};'>{temp_str}</div>
            <div style='font-family:Space Mono,monospace; font-size:10px; color:#6b6b80; margin-top:2px;'>{desc_str} {humidity_str}</div>
            <hr style='border-color:rgba(255,255,255,0.06); margin:8px 0;'/>
            <div style='font-family:Space Mono,monospace; font-size:10px; color:#6b6b80;'>
                ₹{city_rev:,.0f} · {city_orders} orders
            </div>
            <div style='font-family:Space Mono,monospace; font-size:9px; color:#6b6b80; margin-top:4px; line-height:1.4;'>{impact}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ─── BOTTOM ROW: SCATTER + HEATMAP ──────────────────────────────────────────
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("<div class='section-title'>Price Distribution by Product</div>", unsafe_allow_html=True)
    if not df.empty and len(df) > 3:
        fig_box = go.Figure()
        top_prods = df["product"].value_counts().head(6).index.tolist()
        colors = ["#00ff88", "#7c3aed", "#ff6b35", "#38bdf8", "#fb923c", "#f472b6"]
        for idx, prod in enumerate(top_prods):
            prod_df = df[df["product"] == prod]
            fig_box.add_trace(go.Box(
                y=prod_df["price"],
                name=prod[:12],
                marker_color=colors[idx % len(colors)],
                boxmean=True,
                hovertemplate="<b>%{x}</b><br>₹%{y:.0f}<extra></extra>",
            ))
        fig_box.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#6b6b80", size=9),
            margin=dict(l=0, r=0, t=5, b=0), height=280,
            showlegend=False,
            xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=8)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="₹", tickfont=dict(size=8)),
        )
        st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})

with col_b2:
    st.markdown("<div class='section-title'>City × Product Revenue Heatmap</div>", unsafe_allow_html=True)
    if not df.empty and len(df) > 3:
        top5_cities = df["city"].value_counts().head(6).index.tolist()
        top5_prods = df["product"].value_counts().head(6).index.tolist()
        heat_data = df[df["city"].isin(top5_cities) & df["product"].isin(top5_prods)]
        pivot = heat_data.pivot_table(index="city", columns="product", values="price", aggfunc="sum", fill_value=0)
        pivot.columns = [c[:10] for c in pivot.columns]
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#0a0a0f"], [0.4, "#3b1d6e"], [0.7, "#7c3aed"], [1, "#00ff88"]],
            hovertemplate="<b>%{y} × %{x}</b><br>₹%{z:,.0f}<extra></extra>",
            showscale=False,
        ))
        fig_heat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#6b6b80", size=9),
            margin=dict(l=0, r=0, t=5, b=0), height=280,
            xaxis=dict(tickfont=dict(size=8), tickangle=-30),
            yaxis=dict(tickfont=dict(size=9)),
        )
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br/>", unsafe_allow_html=True)

# ─── RAW DATA TABLE ──────────────────────────────────────────────────────────
with st.expander("📋 Raw Transactions Table"):
    if not df.empty:
        display_df = df.copy()
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
        display_df["price"] = display_df["price"].apply(lambda x: f"₹{x:,.2f}")
        display_df.columns = ["Product", "Price", "City", "Time"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.write("No data in current filter.")

# ─── AUTO REFRESH ────────────────────────────────────────────────────────────
time.sleep(0.1)
st.markdown(f"""
<div style='text-align:center; font-family:Space Mono,monospace; font-size:10px;
            color:#3a3a4a; padding: 20px 0 8px;'>
    Auto-refreshing every {refresh_rate}s · New sale every 30s · Weather cached 10min
</div>""", unsafe_allow_html=True)

# Streamlit auto-rerun
st.empty()
time.sleep(refresh_rate)
st.rerun()