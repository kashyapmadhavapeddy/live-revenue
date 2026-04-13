"""
app.py — Revenue Pulse War Room Dashboard
Live sales command center with weather integration
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import os
import time
from datetime import datetime, timedelta

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Revenue Pulse · War Room",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif !important;
    background-color: #030712;
    color: #e2e8f0;
}

.stApp {
    background: #030712;
    background-image:
        radial-gradient(ellipse 60% 40% at 10% 0%, rgba(16,185,129,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 90% 100%, rgba(245,158,11,0.05) 0%, transparent 60%);
}

header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1600px; }

/* ── WAR ROOM HEADER ── */
.wr-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid #10b98130;
    margin-bottom: 1rem;
}
.wr-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #10b981;
    letter-spacing: 3px;
    text-transform: uppercase;
    text-shadow: 0 0 30px rgba(16,185,129,0.4);
}
.wr-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #374151;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #10b981;
    letter-spacing: 2px;
}
.live-dot {
    width: 7px; height: 7px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
    display: inline-block;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

/* ── KPI CARDS ── */
.kpi-card {
    background: linear-gradient(145deg, #0d1117, #111827);
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    height: 130px;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
}
.kpi-card.green::after  { background: linear-gradient(90deg, transparent, #10b981, transparent); }
.kpi-card.amber::after  { background: linear-gradient(90deg, transparent, #f59e0b, transparent); }
.kpi-card.blue::after   { background: linear-gradient(90deg, transparent, #38bdf8, transparent); }
.kpi-card.red::after    { background: linear-gradient(90deg, transparent, #ef4444, transparent); }
.kpi-card.purple::after { background: linear-gradient(90deg, transparent, #a78bfa, transparent); }

.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
}
.kpi-value.green  { color: #10b981; text-shadow: 0 0 20px rgba(16,185,129,0.3); }
.kpi-value.amber  { color: #f59e0b; text-shadow: 0 0 20px rgba(245,158,11,0.3); }
.kpi-value.blue   { color: #38bdf8; text-shadow: 0 0 20px rgba(56,189,248,0.3); }
.kpi-value.red    { color: #ef4444; text-shadow: 0 0 20px rgba(239,68,68,0.3); }
.kpi-value.purple { color: #a78bfa; text-shadow: 0 0 20px rgba(167,139,250,0.3); }
.kpi-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #6b7280;
    margin-top: 0.3rem;
}
.kpi-icon {
    position: absolute;
    top: 1rem; right: 1rem;
    font-size: 1.6rem;
    opacity: 0.15;
}

/* ── SECTION HEADER ── */
.sec-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #10b981;
    border-left: 2px solid #10b981;
    padding-left: 0.7rem;
    margin: 1.5rem 0 0.8rem 0;
}

/* ── WEATHER IMPACT CARD ── */
.weather-impact {
    background: linear-gradient(145deg, #0d1117, #111827);
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.weather-impact.boost  { border-left: 3px solid #10b981; }
.weather-impact.hurt   { border-left: 3px solid #ef4444; }
.weather-impact.neutral{ border-left: 3px solid #f59e0b; }

/* ── ALERT TICKER ── */
.alert-ticker {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #fcd34d;
    margin-bottom: 0.4rem;
}
.alert-ticker.green {
    background: rgba(16,185,129,0.08);
    border-color: rgba(16,185,129,0.2);
    color: #6ee7b7;
}
.alert-ticker.red {
    background: rgba(239,68,68,0.08);
    border-color: rgba(239,68,68,0.2);
    color: #fca5a5;
}

/* ── TABLE STYLING ── */
.stDataFrame { border: 1px solid #1f2937 !important; border-radius: 10px !important; }
[data-testid="stDataFrameResizable"] { background: #0d1117 !important; }

/* ── TIMESTAMP ── */
.timestamp {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: #1f2937;
    letter-spacing: 1px;
}

/* ── BUTTON ── */
.stButton button {
    background: linear-gradient(135deg, #059669, #047857) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    padding: 0.4rem 1.2rem !important;
}

hr { border-color: #1f2937 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #030712; }
::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── CONFIG ───────────────────────────────────────────────────────────────────────
SALES_FILE   = "sales_data.csv"
API_KEY      = st.secrets.get("OPENWEATHER_API_KEY", "")
REFRESH_SECS = 30

WEATHER_IMPACT = {
    "Clear":         ("boost",   "+18% vs avg",  "🟢"),
    "Partly Cloudy": ("boost",   "+8% vs avg",   "🟢"),
    "Cloudy":        ("neutral", "±0% vs avg",   "🟡"),
    "Drizzle":       ("hurt",    "-18% vs avg",  "🔴"),
    "Rain":          ("hurt",    "-32% vs avg",  "🔴"),
    "Heavy Rain":    ("hurt",    "-48% vs avg",  "🔴"),
    "Thunderstorm":  ("hurt",    "-58% vs avg",  "🔴"),
    "Extreme Heat":  ("hurt",    "-28% vs avg",  "🔴"),
    "Foggy":         ("neutral", "-8% vs avg",   "🟡"),
    "Windy":         ("neutral", "-6% vs avg",   "🟡"),
}

CITIES_WEATHER = ["Hyderabad", "Mumbai", "Delhi", "Bangalore", "Chennai"]

# ── HELPERS ──────────────────────────────────────────────────────────────────────
def load_sales():
    if not os.path.exists(SALES_FILE):
        return pd.DataFrame()
    try:
        df = pd.read_csv(SALES_FILE, parse_dates=["timestamp"])
        return df.sort_values("timestamp", ascending=False)
    except:
        return pd.DataFrame()

def fmt_inr(val):
    if val >= 1_00_00_000: return f"₹{val/1_00_00_000:.2f}Cr"
    elif val >= 1_00_000:  return f"₹{val/1_00_000:.2f}L"
    else:                  return f"₹{val:,.0f}"

def get_weather(city):
    if not API_KEY: return None
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city+",IN", "appid": API_KEY, "units": "metric"},
            timeout=5
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "city":    city,
                "desc":    d["weather"][0]["description"].title(),
                "temp":    round(d["main"]["temp"], 1),
                "icon":    d["weather"][0]["icon"],
                "main":    d["weather"][0]["main"],
            }
    except:
        pass
    return None

def base_layout(title="", height=300):
    return dict(
        title=dict(text=title, font=dict(size=11, color="#10b981", family="Share Tech Mono, monospace"), x=0.01),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#6b7280", family="Rajdhani, sans-serif", size=11),
        xaxis=dict(showgrid=True, gridcolor="#111827", zeroline=False, tickfont=dict(size=9, color="#4b5563")),
        yaxis=dict(showgrid=True, gridcolor="#111827", zeroline=False, tickfont=dict(size=9, color="#4b5563")),
        margin=dict(l=10, r=10, t=35, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), orientation="h", y=1.1),
        height=height,
    )

# ── SESSION STATE ─────────────────────────────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = {}
if "weather_last_fetch" not in st.session_state:
    st.session_state.weather_last_fetch = 0

# ── AUTO REFRESH LOGIC ────────────────────────────────────────────────────────────
now_ts = time.time()
auto_refresh = (now_ts - st.session_state.last_refresh) > REFRESH_SECS

# ── HEADER ───────────────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([3, 2, 1])
with h1:
    st.markdown("""
    <div>
        <div class="wr-title">⚡ Revenue Pulse</div>
        <div class="wr-subtitle">Live Sales Command Center · Auto-refresh every 30s</div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    now_str = datetime.now().strftime("%d %b %Y · %H:%M:%S")
    st.markdown(f"""
    <div style="text-align:right; padding-top:0.8rem;">
        <div class="live-badge"><span class="live-dot"></span> LIVE</div>
        <div class="timestamp" style="margin-top:6px;">LAST SYNC · {now_str}</div>
    </div>
    """, unsafe_allow_html=True)
with h3:
    manual_refresh = st.button("⟳ Sync Now")

if auto_refresh or manual_refresh:
    st.session_state.last_refresh = now_ts

st.markdown("---")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────────
df = load_sales()

if df.empty:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0; font-family: Share Tech Mono, monospace; color: #374151;">
        <div style="font-size:3rem;">📡</div>
        <div style="font-size:1rem; letter-spacing:3px; margin-top:1rem;">AWAITING DATA FEED</div>
        <div style="font-size:0.75rem; margin-top:0.5rem; color:#1f2937;">
            Run: <span style="color:#10b981;">python generate_sales.py</span> in your terminal
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── CALCULATIONS ──────────────────────────────────────────────────────────────────
total_revenue   = df["revenue"].sum()
total_orders    = len(df)
avg_order_value = df["revenue"].mean()
top_city        = df.groupby("city")["revenue"].sum().idxmax()
top_product     = df.groupby("product")["revenue"].sum().idxmax()
top_category    = df.groupby("category")["revenue"].sum().idxmax()

# Last 1 hour vs previous 1 hour for trend
now_dt   = datetime.now()
one_hr   = df[df["timestamp"] >= now_dt - timedelta(hours=1)]
prev_hr  = df[(df["timestamp"] >= now_dt - timedelta(hours=2)) & (df["timestamp"] < now_dt - timedelta(hours=1))]
rev_trend = ((one_hr["revenue"].sum() - prev_hr["revenue"].sum()) / max(prev_hr["revenue"].sum(), 1)) * 100

# Today vs yesterday
today     = df[df["timestamp"].dt.date == now_dt.date()]
yesterday = df[df["timestamp"].dt.date == (now_dt - timedelta(days=1)).date()]
today_rev = today["revenue"].sum()

# Orders in last 30 min
last_30   = df[df["timestamp"] >= now_dt - timedelta(minutes=30)]
orders_30 = len(last_30)

# ── KPI ROW ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">LIVE METRICS · COMMAND OVERVIEW</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

trend_arrow = "▲" if rev_trend >= 0 else "▼"
trend_color_cls = "green" if rev_trend >= 0 else "red"

with k1:
    st.markdown(f"""<div class="kpi-card green">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value green">{fmt_inr(total_revenue)}</div>
        <div class="kpi-sub">All time · {total_orders} orders</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="kpi-card amber">
        <div class="kpi-icon">📦</div>
        <div class="kpi-label">Orders · Last 30 Min</div>
        <div class="kpi-value amber">{orders_30}</div>
        <div class="kpi-sub">Live order volume</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card blue">
        <div class="kpi-icon">🧾</div>
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value blue">{fmt_inr(avg_order_value)}</div>
        <div class="kpi-sub">Per transaction</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card {'green' if rev_trend >= 0 else 'red'}">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Revenue Trend</div>
        <div class="kpi-value {'green' if rev_trend >= 0 else 'red'}">{trend_arrow} {abs(rev_trend):.1f}%</div>
        <div class="kpi-sub">vs previous hour</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""<div class="kpi-card purple">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Today's Revenue</div>
        <div class="kpi-value purple">{fmt_inr(today_rev)}</div>
        <div class="kpi-sub">Top city: {top_city}</div>
    </div>""", unsafe_allow_html=True)

# ── WEATHER IMPACT SECTION ────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">🌦 WEATHER × SALES IMPACT · LIVE CITY FEED</div>', unsafe_allow_html=True)

# Fetch weather for cities (cache for 10 min)
if API_KEY and (now_ts - st.session_state.weather_last_fetch) > 600:
    weather_data = {}
    for city in CITIES_WEATHER:
        w = get_weather(city)
        if w: weather_data[city] = w
    st.session_state.weather_cache      = weather_data
    st.session_state.weather_last_fetch = now_ts

weather_data = st.session_state.weather_cache

if weather_data:
    wc1, wc2, wc3, wc4, wc5 = st.columns(5)
    cols = [wc1, wc2, wc3, wc4, wc5]
    for i, (city, wd) in enumerate(weather_data.items()):
        if i >= 5: break
        main_w = wd["main"]
        impact_key = None
        for k in WEATHER_IMPACT:
            if k.lower() in wd["desc"].lower() or k.lower() == main_w.lower():
                impact_key = k; break
        if not impact_key:
            impact_key = "Cloudy"
        impact_cls, impact_pct, dot = WEATHER_IMPACT[impact_key]
        city_rev = df[df["city"] == city]["revenue"].sum()

        border = "#10b981" if impact_cls == "boost" else "#ef4444" if impact_cls == "hurt" else "#f59e0b"
        with cols[i]:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-top:2px solid {border};border-radius:12px;padding:1rem;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.4);">
                <img src="https://openweathermap.org/img/wn/{wd['icon']}@2x.png" style="width:40px;height:40px;filter:drop-shadow(0 0 8px {border}60);">
                <div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#e2e8f0;">{city}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#6b7280;">{wd['desc']} · {wd['temp']}°C</div>
                <div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;color:{border};margin-top:0.3rem;">{dot} {impact_pct}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#4b5563;margin-top:2px;">Rev: {fmt_inr(city_rev)}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    # Show weather from sales data if no API
    city_weather = df.groupby(["city","weather_condition"])["revenue"].sum().reset_index()
    city_best    = city_weather.loc[city_weather.groupby("city")["revenue"].idxmax()]
    wc1, wc2, wc3, wc4, wc5 = st.columns(5)
    cols_w = [wc1, wc2, wc3, wc4, wc5]
    for i, row in city_best.head(5).iterrows():
        impact_cls, impact_pct, dot = WEATHER_IMPACT.get(row["weather_condition"], ("neutral","±0%","🟡"))
        border = "#10b981" if impact_cls == "boost" else "#ef4444" if impact_cls == "hurt" else "#f59e0b"
        with cols_w[i % 5]:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-top:2px solid {border};border-radius:12px;padding:1rem;text-align:center;">
                <div style="font-size:1.8rem;">{'🌦️' if 'Rain' in row['weather_condition'] else '☀️' if 'Clear' in row['weather_condition'] else '⛅'}</div>
                <div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#e2e8f0;">{row['city']}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#6b7280;">{row['weather_condition']}</div>
                <div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;color:{border};margin-top:0.3rem;">{dot} {impact_pct}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#4b5563;">Rev: {fmt_inr(row['revenue'])}</div>
            </div>
            """, unsafe_allow_html=True)

# ── SMART ALERTS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">⚠ SMART ALERTS · MANAGER ACTION REQUIRED</div>', unsafe_allow_html=True)

alerts = []

# Revenue trend alert
if rev_trend > 20:
    alerts.append(("green", f"🚀 SURGE DETECTED — Revenue up {rev_trend:.1f}% vs last hour. Consider increasing ad spend."))
elif rev_trend < -20:
    alerts.append(("red", f"📉 REVENUE DROP — Down {abs(rev_trend):.1f}% vs last hour. Investigate top city performance."))

# Weather impact alerts
rain_cities = df[df["weather_condition"].isin(["Rain","Heavy Rain","Thunderstorm"])]["city"].unique()
if len(rain_cities) > 0:
    alerts.append(("amber", f"🌧️ WEATHER IMPACT — Rain detected in: {', '.join(rain_cities)}. Expect 30-50% lower sales in these cities."))

heat_cities = df[df["weather_condition"] == "Extreme Heat"]["city"].unique()
if len(heat_cities) > 0:
    alerts.append(("amber", f"🔥 HEAT ALERT — Extreme heat in: {', '.join(heat_cities)}. Boost online promotions to compensate."))

# Low order volume
if orders_30 == 0:
    alerts.append(("red", "⚡ NO ORDERS in last 30 minutes. Check data pipeline and API connection."))
elif orders_30 < 3:
    alerts.append(("amber", f"📊 LOW VOLUME — Only {orders_30} orders in last 30 min. Monitor closely."))

# Top category
alerts.append(("green", f"🏆 TOP PERFORMER — {top_category} leading all categories. {top_product} is best-selling product."))

if not alerts:
    alerts.append(("green", "✅ ALL SYSTEMS NORMAL — Revenue flowing steadily. No action required."))

for cls, msg in alerts:
    st.markdown(f'<div class="alert-ticker {cls}">{msg}</div>', unsafe_allow_html=True)

# ── CHARTS ROW 1 ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">📊 REVENUE ANALYTICS</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns([2, 1])

with ch1:
    # Revenue over time (30-min buckets)
    df_time = df.copy()
    df_time["bucket"] = df_time["timestamp"].dt.floor("30min")
    rev_time = df_time.groupby("bucket")["revenue"].sum().reset_index()

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=rev_time["bucket"], y=rev_time["revenue"],
        fill="tozeroy",
        line=dict(color="#10b981", width=2.5),
        fillcolor="rgba(16,185,129,0.07)",
        name="Revenue",
        hovertemplate="<b>%{x|%H:%M}</b><br>₹%{y:,.0f}<extra></extra>"
    ))
    # Add moving average
    if len(rev_time) > 3:
        rev_time["ma"] = rev_time["revenue"].rolling(3, min_periods=1).mean()
        fig_rev.add_trace(go.Scatter(
            x=rev_time["bucket"], y=rev_time["ma"],
            line=dict(color="#f59e0b", width=1.5, dash="dot"),
            name="Trend (MA)",
            hovertemplate="<b>%{x|%H:%M}</b><br>Trend: ₹%{y:,.0f}<extra></extra>"
        ))
    layout_r = base_layout("REVENUE OVER TIME (30-MIN BUCKETS)", 280)
    fig_rev.update_layout(**layout_r)
    st.plotly_chart(fig_rev, use_container_width=True)

with ch2:
    # Category breakdown donut
    cat_rev = df.groupby("category")["revenue"].sum().reset_index()
    colors  = ["#10b981","#f59e0b","#38bdf8","#a78bfa","#ef4444","#34d399"]
    fig_cat = go.Figure(go.Pie(
        labels=cat_rev["category"],
        values=cat_rev["revenue"],
        hole=0.65,
        marker=dict(colors=colors[:len(cat_rev)], line=dict(color="#030712", width=2)),
        textfont=dict(size=10, family="Rajdhani"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
    ))
    fig_cat.update_layout(
        **base_layout("REVENUE BY CATEGORY", 280),
        showlegend=True,
        annotations=[dict(text=f"<b>{top_category}</b>", x=0.5, y=0.5, font=dict(size=11, color="#10b981", family="Rajdhani"), showarrow=False)]
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ── CHARTS ROW 2 ──────────────────────────────────────────────────────────────────
ch3, ch4 = st.columns(2)

with ch3:
    # City revenue bar chart
    city_rev = df.groupby("city")["revenue"].sum().sort_values(ascending=True).reset_index()
    fig_city = go.Figure(go.Bar(
        y=city_rev["city"],
        x=city_rev["revenue"],
        orientation="h",
        marker=dict(
            color=city_rev["revenue"],
            colorscale=[[0,"#064e3b"],[0.5,"#10b981"],[1,"#34d399"]],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
    ))
    layout_c = base_layout("REVENUE BY CITY", 260)
    layout_c["xaxis"]["title"] = "Revenue (₹)"
    layout_c["yaxis"]["showgrid"] = False
    fig_city.update_layout(**layout_c)
    st.plotly_chart(fig_city, use_container_width=True)

with ch4:
    # Weather vs Revenue impact bar
    weather_rev = df.groupby("weather_condition")["revenue"].sum().sort_values(ascending=False).reset_index()
    w_colors = []
    for w in weather_rev["weather_condition"]:
        imp = WEATHER_IMPACT.get(w, ("neutral","","🟡"))[0]
        w_colors.append("#10b981" if imp == "boost" else "#ef4444" if imp == "hurt" else "#f59e0b")

    fig_weather = go.Figure(go.Bar(
        x=weather_rev["weather_condition"],
        y=weather_rev["revenue"],
        marker=dict(color=w_colors, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
    ))
    layout_w = base_layout("REVENUE BY WEATHER CONDITION", 260)
    layout_w["xaxis"]["tickangle"] = -30
    fig_weather.update_layout(**layout_w)
    st.plotly_chart(fig_weather, use_container_width=True)

# ── CHARTS ROW 3 ──────────────────────────────────────────────────────────────────
ch5, ch6 = st.columns([1, 2])

with ch5:
    # Top 5 products
    prod_rev = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(5).reset_index()
    st.markdown('<div class="sec-header">🏆 TOP 5 PRODUCTS</div>', unsafe_allow_html=True)
    for i, row in prod_rev.iterrows():
        pct = (row["revenue"] / total_revenue) * 100
        bar_w = int(pct * 3)
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1f2937;border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.4rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-family:Rajdhani,sans-serif;font-size:0.9rem;font-weight:600;color:#e2e8f0;">{row['product']}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#10b981;">{fmt_inr(row['revenue'])}</div>
            </div>
            <div style="background:#1f2937;border-radius:4px;height:4px;margin-top:0.3rem;">
                <div style="background:linear-gradient(90deg,#10b981,#34d399);width:{min(bar_w,100)}%;height:4px;border-radius:4px;"></div>
            </div>
            <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4b5563;margin-top:2px;">{pct:.1f}% of total revenue</div>
        </div>
        """, unsafe_allow_html=True)

with ch6:
    # Order volume heatmap by hour and city
    if len(df) > 5:
        df_heat = df.copy()
        df_heat["hour"] = df_heat["timestamp"].dt.hour
        heatmap_data = df_heat.groupby(["city","hour"])["revenue"].sum().reset_index()
        pivot = heatmap_data.pivot(index="city", columns="hour", values="revenue").fillna(0)

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"{h:02d}:00" for h in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0,"#030712"],[0.3,"#064e3b"],[0.6,"#10b981"],[1,"#34d399"]],
            hovertemplate="<b>%{y}</b> at %{x}<br>₹%{z:,.0f}<extra></extra>",
        ))
        layout_h = base_layout("REVENUE HEATMAP · CITY × HOUR", 260)
        layout_h["xaxis"]["showgrid"] = False
        layout_h["yaxis"]["showgrid"] = False
        fig_heat.update_layout(**layout_h)
        st.plotly_chart(fig_heat, use_container_width=True)

# ── LIVE ORDER FEED ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">📡 LIVE ORDER FEED · LAST 10 TRANSACTIONS</div>', unsafe_allow_html=True)

recent = df.head(10)[["timestamp","order_id","product","category","quantity","price","city","weather_condition","revenue"]].copy()
recent["revenue"] = recent["revenue"].apply(lambda x: f"₹{x:,.0f}")
recent["price"]   = recent["price"].apply(lambda x: f"₹{x:,.0f}")
recent.columns    = ["Time","Order ID","Product","Category","Qty","Price","City","Weather","Revenue"]
recent["Time"]    = recent["Time"].dt.strftime("%H:%M:%S")

st.dataframe(
    recent,
    use_container_width=True,
    hide_index=True,
)

# ── MANAGER SUMMARY ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header">📋 MANAGER DECISION SUMMARY</div>', unsafe_allow_html=True)

ms1, ms2, ms3 = st.columns(3)
with ms1:
    st.markdown(f"""
    <div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-left:3px solid #10b981;border-radius:12px;padding:1rem 1.2rem;">
        <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;letter-spacing:2px;color:#4b5563;margin-bottom:0.5rem;">TOP OPPORTUNITY</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#10b981;">Push more {top_category}</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#6b7280;margin-top:0.3rem;">Highest revenue category this session</div>
    </div>
    """, unsafe_allow_html=True)

with ms2:
    worst_weather = df.groupby("weather_condition")["revenue"].mean().idxmin() if not df.empty else "Rain"
    st.markdown(f"""
    <div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-left:3px solid #f59e0b;border-radius:12px;padding:1rem 1.2rem;">
        <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;letter-spacing:2px;color:#4b5563;margin-bottom:0.5rem;">WEATHER RISK</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#f59e0b;">Watch {worst_weather} cities</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#6b7280;margin-top:0.3rem;">Lowest avg revenue during {worst_weather}</div>
    </div>
    """, unsafe_allow_html=True)

with ms3:
    best_hour_data = df.copy()
    best_hour_data["hour"] = best_hour_data["timestamp"].dt.hour
    best_hour = best_hour_data.groupby("hour")["revenue"].sum().idxmax() if not df.empty else 12
    st.markdown(f"""
    <div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-left:3px solid #38bdf8;border-radius:12px;padding:1rem 1.2rem;">
        <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;letter-spacing:2px;color:#4b5563;margin-bottom:0.5rem;">PEAK HOUR</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#38bdf8;">{best_hour:02d}:00 — {best_hour+1:02d}:00</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#6b7280;margin-top:0.3rem;">Highest revenue hour today</div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:#1f2937;text-align:center;margin-top:2rem;padding-top:1rem;border-top:1px solid #111827;letter-spacing:2px;">
REVENUE PULSE WAR ROOM · POWERED BY OPENWEATHERMAP + LIVE DATA PIPELINE · AUTO-REFRESH 30s
</div>
""", unsafe_allow_html=True)

# ── FORCE RERUN EVERY 30 SECONDS ─────────────────────────────────────────────────
time.sleep(1)
if (time.time() - st.session_state.last_refresh) >= REFRESH_SECS:
    st.rerun()