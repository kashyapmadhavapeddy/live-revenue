new message from Homa Varshini  Show  Ignore 

Skip to content
Using Gmail with screen readers
Enable desktop notifications for Gmail.
   OK  No, thanks
1 of 9,949
(no subject)
Inbox

Kashyap
Attachments
Mon 16 Feb, 14:45
 
41

Kashyap
12:17 (7 minutes ago)
import streamlit as st import pandas as pd import plotly.graph_objects as go import requests, random, time from datetime import datetime, timedelta st.set_page_

Homa Varshini
Attachments
12:24 (0 minutes ago)
to me

...

[Message clipped]  View entire message
 One attachment
  •  Scanned by Gmail
"""
╔══════════════════════════════════════════════════════════════════╗
║  ⚡ REVENUE PULSE — SALES WAR ROOM COMMAND CENTER               ║
║  Run : streamlit run war_room_dashboard.py                       ║
║  Deps: pip install streamlit pandas plotly requests              ║
╚══════════════════════════════════════════════════════════════════╝

BUG FIXED: AttributeError on st.session_state.last_add
ROOT CAUSE: Session-state keys were checked before being initialised.
FIX: All keys are seeded inside a single `_init_session_state()`
     function that is called unconditionally at the top of every run,
     using `.setdefault()` so existing values are never overwritten.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import time
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="⚡ Revenue Pulse · War Room",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════
WEATHER_API_KEY = "37b1806d95a16313402bc8a89f54a3a6"

PRODUCTS = [
    ("UltraBook Pro",       "Electronics",  45000, 85000),
    ("Wireless Earbuds",    "Electronics",   2500,  8000),
    ("Smart Watch",         "Electronics",  12000, 35000),
    ("Monitor 4K",          "Electronics",  18000, 45000),
    ("Mechanical Keyboard", "Electronics",   4000, 15000),
    ("Office Chair",        "Furniture",     8000, 25000),
    ("Standing Desk",       "Furniture",    15000, 40000),
    ("Running Shoes",       "Apparel",       3000,  9000),
    ("Winter Jacket",       "Apparel",       2500,  7500),
    ("Backpack",            "Apparel",       1500,  5000),
    ("Protein Powder",      "Health",        1500,  4500),
    ("Yoga Mat",            "Health",         800,  2500),
    ("Water Bottle",        "Health",         500,  1800),
    ("Coffee Maker",        "Appliances",    3500, 12000),
    ("Air Purifier",        "Appliances",    8000, 20000),
]

CITIES = [
    ("Hyderabad", "South"),
    ("Mumbai",    "West"),
    ("Delhi",     "North"),
    ("Bangalore", "South"),
    ("Chennai",   "South"),
    ("Kolkata",   "East"),
    ("Pune",      "West"),
    ("Ahmedabad", "West"),
]

# Weather condition → (hex_color, impact_label, sales_multiplier)
WEATHER_MAP = {
    "Clear":        ("#22c55e",  "+18% SALES BOOST",   1.25),
    "Partly Cloudy":("#86efac",  "+8% MODERATE LIFT",  1.10),
    "Cloudy":       ("#94a3b8",  "±0% NEUTRAL",        0.95),
    "Drizzle":      ("#fb923c",  "−18% RAIN IMPACT",   0.80),
    "Rain":         ("#ef4444",  "−32% RAIN IMPACT",   0.65),
    "Heavy Rain":   ("#dc2626",  "−48% HEAVY RAIN",    0.50),
    "Thunderstorm": ("#991b1b",  "−58% STORM ALERT",   0.40),
    "Extreme Heat": ("#f97316",  "−28% HEAT ALERT",    0.70),
    "Foggy":        ("#a78bfa",  "−8% LOW VISIBILITY", 0.85),
    "Windy":        ("#60a5fa",  "−6% WINDY",          0.90),
}

CHART_PAL = [
    "#22d3ee", "#f59e0b", "#a78bfa", "#34d399",
    "#fb7185", "#38bdf8", "#fbbf24", "#4ade80",
]


# ══════════════════════════════════════════════════════════
#  SESSION-STATE INITIALISATION  ← THE CRITICAL FIX
#  .setdefault() only writes a key when it is ABSENT,
#  so re-runs never reset live data.
# ══════════════════════════════════════════════════════════
def _init_session_state() -> None:
    ss = st.session_state
    ss.setdefault("sales",        [])
    ss.setdefault("oid",          1001)
    ss.setdefault("last_add",     0.0)      # ← was missing; caused the crash
    ss.setdefault("weather_data", {})
    ss.setdefault("weather_ts",   0.0)

_init_session_state()


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
def _new_sale(ts: datetime | None = None) -> dict:
    product, category, lo, hi = random.choice(PRODUCTS)
    city, region               = random.choice(CITIES)
    weather, _, mult           = random.choice(list(WEATHER_MAP.values())[:10])
    # pick weather key, not value
    weather_key                = random.choice(list(WEATHER_MAP.keys()))
    _, _, mult                 = WEATHER_MAP[weather_key]
    qty     = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
    price   = random.randint(lo, hi)
    revenue = round(price * qty * (0.85 + mult * 0.15))
    rec = {
        "ts":       ts or datetime.now(),
        "oid":      f"ORD-{st.session_state.oid}",
        "product":  product,
        "category": category,
        "price":    price,
        "qty":      qty,
        "city":     city,
        "region":   region,
        "weather":  weather_key,
        "revenue":  revenue,
    }
    st.session_state.oid += 1
    return rec


def _seed_history() -> None:
    """Populate 60 historical sales spread over the last 3 hours."""
    now = datetime.now()
    for _ in range(60):
        ts = now - timedelta(minutes=random.randint(1, 180))
        st.session_state.sales.append(_new_sale(ts))
    st.session_state.sales.sort(key=lambda x: x["ts"])
    st.session_state.last_add = time.time()


def _fmt_inr(v: float) -> str:
    if v >= 1_00_00_000:
        return f"₹{v / 1_00_00_000:.2f} Cr"
    if v >= 1_00_000:
        return f"₹{v / 1_00_000:.2f} L"
    return f"₹{v:,.0f}"


def _fetch_weather() -> None:
    """Call OpenWeatherMap for all 8 cities; cache for 10 min."""
    for city, _ in CITIES:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": f"{city},IN", "appid": WEATHER_API_KEY, "units": "metric"},
                timeout=5,
            )
            if resp.status_code == 200:
                d = resp.json()
                st.session_state.weather_data[city] = {
                    "desc":     d["weather"][0]["description"].title(),
                    "main":     d["weather"][0]["main"],
                    "temp":     round(d["main"]["temp"], 1),
                    "feels":    round(d["main"]["feels_like"], 1),
                    "humidity": d["main"]["humidity"],
                    "wind":     round(d["wind"]["speed"], 1),
                    "icon":     d["weather"][0]["icon"],
                    "source":   "live",
                }
        except Exception:
            pass
    st.session_state.weather_ts = time.time()


def _weather_cls(city: str) -> tuple[str, str, str]:
    """Return (color, impact_label, condition_text) for a city."""
    wd = st.session_state.weather_data.get(city)
    if wd:
        main = wd["main"]
        # match main condition to our map
        key  = next((k for k in WEATHER_MAP if k.lower() in main.lower()), "Cloudy")
        col, lbl, _ = WEATHER_MAP[key]
        txt = f'{wd["desc"]} · {wd["temp"]}°C'
    else:
        # fall back to modal weather from simulated sales
        city_df = pd.DataFrame(st.session_state.sales)
        if not city_df.empty and city in city_df["city"].values:
            modal_key = city_df[city_df["city"] == city]["weather"].mode().iloc[0]
        else:
            modal_key = "Cloudy"
        col, lbl, _ = WEATHER_MAP.get(modal_key, ("#94a3b8", "±0% NEUTRAL", 0.95))
        txt = modal_key
    return col, lbl, txt


def _base_layout(title: str = "", h: int = 280) -> dict:
    return dict(
        title=dict(
            text=title,
            font=dict(size=11, color="#94a3b8", family="JetBrains Mono"),
            x=0.01,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748b", family="DM Sans", size=11),
        xaxis=dict(gridcolor="#1e293b", zeroline=False,
                   tickfont=dict(size=9, color="#475569")),
        yaxis=dict(gridcolor="#1e293b", zeroline=False,
                   tickfont=dict(size=9, color="#475569")),
        margin=dict(l=8, r=8, t=36, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9),
                    orientation="h", y=1.14),
        height=h,
        hovermode="x unified",
    )


# ══════════════════════════════════════════════════════════
#  SEED DATA ON FIRST RUN
# ══════════════════════════════════════════════════════════
if not st.session_state.sales:
    _seed_history()

# ══════════════════════════════════════════════════════════
#  AUTO-ADD A SALE EVERY 30 s
# ══════════════════════════════════════════════════════════
now_ts = time.time()
if now_ts - st.session_state.last_add >= 30:
    st.session_state.sales.append(_new_sale())
    st.session_state.last_add = now_ts

# ══════════════════════════════════════════════════════════
#  REFRESH WEATHER EVERY 10 MIN
# ══════════════════════════════════════════════════════════
if now_ts - st.session_state.weather_ts > 600:
    _fetch_weather()

# ══════════════════════════════════════════════════════════
#  BUILD DATAFRAME + DERIVED METRICS
# ══════════════════════════════════════════════════════════
df       = (pd.DataFrame(st.session_state.sales)
              .sort_values("ts", ascending=False)
              .reset_index(drop=True))
now_dt   = datetime.now()

total_rev  = df["revenue"].sum()
total_ord  = len(df)
aov        = df["revenue"].mean()
today_rev  = df[df["ts"].dt.date == now_dt.date()]["revenue"].sum()
ord_30m    = len(df[df["ts"] >= now_dt - timedelta(minutes=30)])

hr1 = df[df["ts"] >= now_dt - timedelta(hours=1)]["revenue"].sum()
hr2 = df[(df["ts"] >= now_dt - timedelta(hours=2)) &
         (df["ts"] <  now_dt - timedelta(hours=1))]["revenue"].sum()
trend_pct  = ((hr1 - hr2) / max(hr2, 1)) * 100

top_cat    = df.groupby("category")["revenue"].sum().idxmax()
top_prod   = df.groupby("product")["revenue"].sum().idxmax()
top_city   = df.groupby("city")["revenue"].sum().idxmax()
secs_next  = max(0, 30 - int(now_ts - st.session_state.last_add))
is_live_wx = bool(st.session_state.weather_data)


# ══════════════════════════════════════════════════════════
#  CSS — DEEP SLATE × CYAN × AMBER  ·  Bebas Neue headline
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg0:     #020817;
    --bg1:     #0a1628;
    --bg2:     #0f1e35;
    --card:    #0d1b2e;
    --border:  #162035;
    --border2: #1e3050;
    --cyan:    #22d3ee;
    --amber:   #f59e0b;
    --rose:    #fb7185;
    --green:   #22c55e;
    --purple:  #a78bfa;
    --text:    #e2e8f0;
    --muted:   #64748b;
    --dim:     #334155;
    --fh:  'Bebas Neue', sans-serif;
    --fb:  'DM Sans', sans-serif;
    --fm:  'JetBrains Mono', monospace;
}

/* ── reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    background: var(--bg0) !important;
    color: var(--text) !important;
    font-family: var(--fb) !important;
}
.block-container { padding: 1.4rem 2rem !important; max-width: 100% !important; }
#MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ══ HERO BANNER ══ */
.hero {
    background: linear-gradient(120deg, #050f22 0%, #0a1628 60%, #0d1e38 100%);
    border: 1px solid var(--border2);
    border-bottom: 3px solid var(--amber);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.2rem;
}
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 60% 80% at 90% 50%, rgba(34,211,238,0.05) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eye {
    font-family: var(--fm);
    font-size: 0.62rem;
    color: var(--amber);
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.hero-h1 {
    font-family: var(--fh);
    font-size: 3rem;
    letter-spacing: 0.08em;
    color: #fff;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.hero-h1 em { color: var(--cyan); font-style: normal; }
.hero-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.9rem;
    font-family: var(--fm);
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.12em;
}
.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 20px;
    padding: 0.22rem 0.7rem;
    color: var(--green);
    font-size: 0.6rem;
}
.live-dot {
    width: 6px; height: 6px;
    background: var(--green);
    border-radius: 50%;
    box-shadow: 0 0 6px var(--green);
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }
.tag {
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.2);
    border-radius: 20px;
    padding: 0.18rem 0.65rem;
    color: var(--cyan);
    font-size: 0.58rem;
}

/* ══ SECTION LABEL ══ */
.sec {
    font-family: var(--fm);
    font-size: 0.58rem;
    font-weight: 600;
    color: var(--cyan);
    letter-spacing: 0.35em;
    text-transform: uppercase;
    border-left: 3px solid var(--cyan);
    padding-left: 0.65rem;
    margin: 1.4rem 0 0.8rem;
}

/* ══ KPI CARD ══ */
.kpi {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.15rem 1.3rem 1rem;
    position: relative;
    overflow: hidden;
    min-height: 128px;
}
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
}
.kpi::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 1.5px;
}
.kpi.cyan::before, .kpi.cyan::after  { background: var(--cyan); }
.kpi.amber::before,.kpi.amber::after { background: var(--amber); }
.kpi.rose::before, .kpi.rose::after  { background: var(--rose); }
.kpi.green::before,.kpi.green::after { background: var(--green); }
.kpi.purple::before,.kpi.purple::after{ background: var(--purple); }
.kpi-bg-icon {
    position: absolute; top: 10px; right: 12px;
    font-size: 2.2rem; opacity: 0.06; pointer-events: none;
}
.kpi-lbl {
    font-family: var(--fm);
    font-size: 0.56rem;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}
.kpi-val {
    font-family: var(--fh);
    font-size: 2rem;
    letter-spacing: 0.04em;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.kpi-val.cyan   { color: var(--cyan); }
.kpi-val.amber  { color: var(--amber); }
.kpi-val.rose   { color: var(--rose); }
.kpi-val.green  { color: var(--green); }
.kpi-val.purple { color: var(--purple); }
.kpi-foot {
    font-family: var(--fm);
    font-size: 0.56rem;
    color: var(--muted);
}

/* ══ WEATHER CARD ══ */
.wx-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.7rem;
    margin-top: 0.5rem;
}
.wx-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 0.9rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.wx-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent-color, var(--cyan));
}
.wx-city {
    font-family: var(--fh);
    font-size: 1.1rem;
    letter-spacing: 0.08em;
    color: #fff;
    margin-bottom: 0.15rem;
}
.wx-emoji { font-size: 2rem; display: block; margin-bottom: 0.3rem; }
.wx-temp {
    font-family: var(--fh);
    font-size: 1.8rem;
    letter-spacing: 0.04em;
    line-height: 1;
    color: var(--accent-color, var(--cyan));
    margin-bottom: 0.1rem;
}
.wx-desc {
    font-family: var(--fm);
    font-size: 0.55rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.wx-stats {
    font-family: var(--fm);
    font-size: 0.52rem;
    color: var(--dim);
    margin-bottom: 0.45rem;
}
.wx-impact {
    display: inline-block;
    border-radius: 20px;
    padding: 0.18rem 0.6rem;
    font-family: var(--fm);
    font-size: 0.54rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: var(--accent-color, var(--cyan));
    border: 1px solid var(--accent-color, var(--cyan));
    background: rgba(255,255,255,0.03);
    text-transform: uppercase;
}

/* ══ ALERT STRIP ══ */
.alrt {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin-bottom: 5px;
    font-family: var(--fm);
    font-size: 0.68rem;
    line-height: 1.5;
}
.alrt.green { background: rgba(34,197,94,0.07);  border: 1px solid rgba(34,197,94,0.2);  color: #86efac; }
.alrt.amber { background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2); color: #fcd34d; }
.alrt.rose  { background: rgba(251,113,133,0.08);border: 1px solid rgba(251,113,133,0.2);color: #fda4af; }
.alrt-badge {
    flex-shrink: 0;
    padding: 0.12rem 0.5rem;
    border-radius: 4px;
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
}
.alrt.green .alrt-badge { background: #166534; color: #86efac; }
.alrt.amber .alrt-badge { background: #78350f; color: #fcd34d; }
.alrt.rose  .alrt-badge { background: #881337; color: #fda4af; }

/* ══ PROGRESS BAR ══ */
.pbar-wrap { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 0.85rem; margin-bottom: 5px; }
.pbar-header { display: flex; justify-content: space-between; margin-bottom: 5px; }
.pbar-name { font-size: 0.82rem; font-weight: 600; color: var(--text); }
.pbar-rev  { font-family: var(--fm); font-size: 0.62rem; color: var(--cyan); }
.pbar-bg   { background: var(--bg0); border-radius: 4px; height: 4px; }
.pbar-fill { height: 4px; border-radius: 4px; background: linear-gradient(90deg, var(--cyan), var(--amber)); }
.pbar-foot { font-family: var(--fm); font-size: 0.52rem; color: var(--muted); margin-top: 3px; }

/* ══ DECISION CARD ══ */
.dec-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
.dec-label {
    font-family: var(--fm);
    font-size: 0.55rem;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.dec-val {
    font-family: var(--fh);
    font-size: 1.4rem;
    letter-spacing: 0.06em;
    color: var(--cyan);
    margin-bottom: 0.25rem;
}
.dec-sub { font-size: 0.75rem; color: var(--muted); line-height: 1.4; }

/* ══ TICKER ══ */
.ticker-wrap {
    background: var(--bg1);
    border-top: 2px solid var(--amber);
    border-bottom: 1px solid var(--border);
    padding: 0.4rem 0;
    overflow: hidden;
    white-space: nowrap;
    border-radius: 6px;
    margin-bottom: 1rem;
}
.ticker-inner { display: inline-block; animation: tick 50s linear infinite; }
@keyframes tick { 0%{transform:translateX(50vw)} 100%{transform:translateX(-100%)} }
.tick-item { font-family: var(--fm); font-size: 0.65rem; display: inline-block; padding: 0 2.5rem; color: var(--amber); }
.tick-item .tp { color: var(--green); font-weight: 600; }
.tick-item .tc { color: var(--cyan); }

/* ── misc ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ━━━━━━━━━━━━━━  RENDER  ━━━━━━━━━━━━━━
# ══════════════════════════════════════════════════════════

# ── HERO ──────────────────────────────────────────────────
wx_src = "🛰 OPENWEATHERMAP LIVE" if is_live_wx else "◌ SIMULATED"
st.markdown(f"""
<div class="hero">
  <div class="hero-eye">🎯 Sales Command Center &nbsp;·&nbsp; War Room Operations &nbsp;·&nbsp; Manager Dashboard</div>
  <div class="hero-h1">⚡ REVENUE <em>PULSE</em></div>
  <div class="hero-row">
    <span class="live-pill"><span class="live-dot"></span>&nbsp;LIVE · {total_ord} ORDERS</span>
    <span>📅 {now_dt.strftime('%A, %d %B %Y')}</span>
    <span>🕐 {now_dt.strftime('%H:%M:%S')}</span>
    <span class="tag">WEATHER: {wx_src}</span>
    <span class="tag">NEXT SALE: {secs_next}s</span>
    <span class="tag">AUTO-REFRESH: 5s</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TICKER ────────────────────────────────────────────────
tick_html = "".join([
    f'<span class="tick-item">'
    f'⚡ {s["oid"]} &nbsp; {s["product"]} &nbsp; '
    f'<span class="tp">₹{s["revenue"]:,}</span> &nbsp; '
    f'<span class="tc">{s["city"]}</span> &nbsp; {s["ts"].strftime("%H:%M:%S")}'
    f'</span>'
    for s in st.session_state.sales[-14:]
])
st.markdown(
    f'<div class="ticker-wrap"><div class="ticker-inner">{tick_html}</div></div>',
    unsafe_allow_html=True,
)

# ── KPIs ──────────────────────────────────────────────────
st.markdown('<div class="sec">📊 LIVE COMMAND METRICS</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

trend_arrow = "▲" if trend_pct >= 0 else "▼"
trend_color = "green" if trend_pct >= 0 else "rose"

def _kpi(col, icon, lbl, val, foot, color):
    col.markdown(f"""
    <div class="kpi {color}">
      <div class="kpi-bg-icon">{icon}</div>
      <div class="kpi-lbl">{lbl}</div>
      <div class="kpi-val {color}">{val}</div>
      <div class="kpi-foot">{foot}</div>
    </div>""", unsafe_allow_html=True)

_kpi(k1, "💰", "Total Revenue",    _fmt_inr(total_rev),       f"Across {total_ord} orders",   "cyan")
_kpi(k2, "📦", "Orders · Last 30m", str(ord_30m),             "Live volume",                   "amber")
_kpi(k3, "🧾", "Avg Order Value",  _fmt_inr(aov),             "Per transaction",               "purple")
_kpi(k4, "📈", "Revenue Trend",
     f"{trend_arrow} {abs(trend_pct):.1f}%",                   "vs previous hour",              trend_color)
_kpi(k5, "🏅", "Today Revenue",    _fmt_inr(today_rev),       f"Leader: {top_city}",           "green")


# ══════════════════════════════════════════════════════════
#  WEATHER INTELLIGENCE
# ══════════════════════════════════════════════════════════
st.markdown('<div class="sec">🌦️ WEATHER INTELLIGENCE — REAL-TIME CITY IMPACT</div>',
            unsafe_allow_html=True)

# Determine colour per-card
def _wx_emoji(col: str) -> str:
    c = col.lstrip("#").lower()
    if c in ("22c55e","86efac"):          return "☀️"
    if c in ("22d3ee","60a5fa","38bdf8"): return "💨"
    if c in ("94a3b8","a78bfa"):          return "☁️"
    if c in ("fb923c","f97316"):          return "🌧️"
    if c in ("ef4444","dc2626","991b1b"): return "⛈️"
    return "🌡️"

# Two rows: first 4 cities, then last 4
for row_cities in [CITIES[:4], CITIES[4:]]:
    cols = st.columns(4)
    for ci, (city, region) in enumerate(row_cities):
        col, impact_lbl, cond_txt = _weather_cls(city)
        city_total = df[df["city"] == city]["revenue"].sum()
        wd = st.session_state.weather_data.get(city, {})
        emoji = _wx_emoji(col)
        temp_txt  = f'{wd["temp"]}°C' if wd else "—"
        stats_txt = f'💧 {wd.get("humidity","—")}% &nbsp; 💨 {wd.get("wind","—")} m/s' if wd else ""
        with cols[ci]:
            st.markdown(f"""
            <div class="wx-card" style="--accent-color:{col}">
              <span class="wx-emoji">{emoji}</span>
              <div class="wx-city">{city}</div>
              <div class="wx-temp">{temp_txt}</div>
              <div class="wx-desc">{cond_txt}</div>
              <div class="wx-stats">{stats_txt}</div>
              <div class="wx-impact">{impact_lbl}</div>
              <div style="font-family:var(--fm);font-size:0.54rem;color:var(--muted);margin-top:0.35rem;">
                Revenue: {_fmt_inr(city_total)}
              </div>
            </div>""", unsafe_allow_html=True)

# ── WEATHER ALERTS ─────────────────────────────────────────
rain_cities = [
    c for c, _ in CITIES
    if any(x in df[df["city"] == c]["weather"].values
           for x in ("Rain", "Heavy Rain", "Thunderstorm", "Drizzle"))
]
heat_cities = [c for c, _ in CITIES if "Extreme Heat" in df[df["city"] == c]["weather"].values]

st.markdown('<div class="sec">⚠️ SMART ALERTS &amp; COMMANDER DECISIONS</div>',
            unsafe_allow_html=True)

alerts = []
if trend_pct > 20:
    alerts.append(("green", "SURGE",  f"Revenue up {trend_pct:.1f}% vs last hour — sustain push."))
elif trend_pct < -20:
    alerts.append(("rose",  "DROP",   f"Revenue down {abs(trend_pct):.1f}% vs last hour — investigate."))

if rain_cities:
    alerts.append(("amber", "🌧️ RAIN",
                   f"Online surge expected: {', '.join(rain_cities)}. Launch digital-only promos NOW."))
if heat_cities:
    alerts.append(("rose",  "🔥 HEAT",
                   f"Foot-traffic risk: {', '.join(heat_cities)}. Redirect budget to delivery & online."))
if ord_30m == 0:
    alerts.append(("rose",  "NO ORDERS", "Zero orders in last 30 min — check pipeline immediately."))
elif ord_30m < 3:
    alerts.append(("amber", "LOW VOL",  f"Only {ord_30m} orders in last 30 min — consider promo push."))

alerts.append(("green", "LEADER",
               f"Top category: {top_cat} · Best product: {top_prod} · Best city: {top_city}"))

for color, badge, msg in alerts:
    st.markdown(f"""
    <div class="alrt {color}">
      <span class="alrt-badge">{badge}</span>
      <span>{msg}</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  CHARTS ROW 1 — Revenue Timeline + Category Donut
# ══════════════════════════════════════════════════════════
st.markdown('<div class="sec">📉 REVENUE ANALYTICS</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns([2, 1])

with ch1:
    dft = df.copy()
    dft["bucket"] = dft["ts"].dt.floor("15min")
    rt = dft.groupby("bucket")["revenue"].sum().reset_index().sort_values("bucket")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=rt["bucket"], y=rt["revenue"],
        fill="tozeroy",
        line=dict(color="#22d3ee", width=2.5, shape="spline"),
        fillcolor="rgba(34,211,238,0.07)",
        name="Revenue",
        hovertemplate="<b>%{x|%H:%M}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    if len(rt) > 3:
        rt["ma"] = rt["revenue"].rolling(3, min_periods=1).mean()
        fig1.add_trace(go.Scatter(
            x=rt["bucket"], y=rt["ma"],
            line=dict(color="#f59e0b", width=1.5, dash="dot"),
            name="3-period MA",
            hovertemplate="MA: ₹%{y:,.0f}<extra></extra>",
        ))
    lo1 = _base_layout("REVENUE · 15-MIN BUCKETS", 290)
    lo1["xaxis"]["tickangle"] = -30
    fig1.update_layout(**lo1)
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

with ch2:
    cr = df.groupby("category")["revenue"].sum().reset_index()
    fig2 = go.Figure(go.Pie(
        labels=cr["category"],
        values=cr["revenue"],
        hole=0.58,
        marker=dict(colors=CHART_PAL[:len(cr)], line=dict(color="#020817", width=2)),
        textfont=dict(size=10),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig2.add_annotation(
        text=f"<b>{top_cat}</b>", x=0.5, y=0.5, showarrow=False,
        font=dict(size=10, color="#22d3ee", family="JetBrains Mono"),
    )
    lo2 = _base_layout("REVENUE BY CATEGORY", 290)
    lo2["showlegend"] = True
    lo2["legend"]["orientation"] = "v"
    lo2["legend"]["x"] = 1.0
    fig2.update_layout(**lo2)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ── Charts Row 2 ───────────────────────────────────────────
ch3, ch4 = st.columns(2)

with ch3:
    cir = df.groupby("city")["revenue"].sum().sort_values().reset_index()
    fig3 = go.Figure(go.Bar(
        y=cir["city"],
        x=cir["revenue"],
        orientation="h",
        marker=dict(
            color=cir["revenue"],
            colorscale=[[0, "#0c3249"], [0.5, "#22d3ee"], [1, "#f59e0b"]],
            line=dict(width=0),
        ),
        text=[_fmt_inr(v) for v in cir["revenue"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=9),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    lo3 = _base_layout("REVENUE BY CITY", 270)
    lo3["yaxis"]["showgrid"] = False
    lo3["xaxis"]["title"] = "Revenue ₹"
    fig3.update_layout(**lo3)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with ch4:
    wr = df.groupby("weather")["revenue"].sum().sort_values(ascending=False).reset_index()
    w_colors = [WEATHER_MAP.get(w, ("", "#94a3b8", 1))[0] for w in wr["weather"]]
    fig4 = go.Figure(go.Bar(
        x=wr["weather"],
        y=wr["revenue"],
        marker=dict(color=w_colors, line=dict(width=0)),
        text=[_fmt_inr(v) for v in wr["revenue"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=9),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    lo4 = _base_layout("REVENUE BY WEATHER CONDITION", 270)
    lo4["xaxis"]["tickangle"] = -35
    fig4.update_layout(**lo4)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# ── Charts Row 3 — Heatmap + Scatter ──────────────────────
ch5, ch6 = st.columns([3, 2])

with ch5:
    dfh = df.copy()
    dfh["hour"] = dfh["ts"].dt.hour
    pivot = (
        dfh.groupby(["city", "hour"])["revenue"]
        .sum().reset_index()
        .pivot(index="city", columns="hour", values="revenue")
        .fillna(0)
    )
    fig5 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[[0, "#020817"], [0.3, "#0c3249"], [0.7, "#22d3ee"], [1, "#f59e0b"]],
        hovertemplate="<b>%{y}</b> @ %{x}<br>₹%{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(thickness=8, tickfont=dict(size=8, color="#64748b")),
    ))
    lo5 = _base_layout("HEATMAP — CITY × HOUR OF DAY", 310)
    lo5["xaxis"]["showgrid"] = False
    lo5["yaxis"]["showgrid"] = False
    fig5.update_layout(**lo5)
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

with ch6:
    # Scatter: price vs revenue, coloured by category
    cats = df["category"].unique().tolist()
    fig6 = go.Figure()
    for i, cat in enumerate(cats):
        sub = df[df["category"] == cat]
        fig6.add_trace(go.Scatter(
            x=sub["price"],
            y=sub["revenue"],
            mode="markers",
            name=cat,
            marker=dict(size=6, color=CHART_PAL[i % len(CHART_PAL)], opacity=0.75),
            hovertemplate=f"<b>{cat}</b><br>Price: ₹%{{x:,}}<br>Revenue: ₹%{{y:,}}<extra></extra>",
        ))
    lo6 = _base_layout("PRICE vs REVENUE · BY CATEGORY", 310)
    lo6["xaxis"]["title"] = "Unit Price ₹"
    lo6["yaxis"]["title"] = "Order Revenue ₹"
    lo6["legend"]["orientation"] = "v"
    lo6["legend"]["x"] = 1.0
    fig6.update_layout(**lo6)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════
#  BOTTOM — Top Products + Live Order Feed
# ══════════════════════════════════════════════════════════
st.markdown('<div class="sec">🏆 TOP PRODUCTS &amp; 📡 LIVE ORDER FEED</div>',
            unsafe_allow_html=True)
b1, b2 = st.columns([1, 2])

with b1:
    pr = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(7).reset_index()
    for _, row in pr.iterrows():
        pct  = (row["revenue"] / total_rev) * 100
        fill = min(int(pct * 4), 100)
        st.markdown(f"""
        <div class="pbar-wrap">
          <div class="pbar-header">
            <span class="pbar-name">{row["product"]}</span>
            <span class="pbar-rev">{_fmt_inr(row["revenue"])}</span>
          </div>
          <div class="pbar-bg">
            <div class="pbar-fill" style="width:{fill}%"></div>
          </div>
          <div class="pbar-foot">{pct:.1f}% of total revenue</div>
        </div>""", unsafe_allow_html=True)

with b2:
    feed = df.head(15)[["ts","oid","product","category","qty","price","city","weather","revenue"]].copy()
    feed["ts"]      = feed["ts"].dt.strftime("%H:%M:%S")
    feed["revenue"] = feed["revenue"].apply(lambda x: f"₹{x:,.0f}")
    feed["price"]   = feed["price"].apply(lambda x: f"₹{x:,.0f}")
    feed.columns    = ["Time", "Order ID", "Product", "Category", "Qty", "Price", "City", "Weather", "Revenue"]
    st.dataframe(feed.reset_index(drop=True), use_container_width=True,
                 height=380, hide_index=True)


# ══════════════════════════════════════════════════════════
#  MANAGER DECISION BOARD
# ══════════════════════════════════════════════════════════
st.markdown('<div class="sec">📋 MANAGER DECISION BOARD</div>', unsafe_allow_html=True)

dfh2   = df.copy(); dfh2["hour"] = dfh2["ts"].dt.hour
worst_wx  = df.groupby("weather")["revenue"].mean().idxmin() if not df.empty else "Rain"
best_hr   = dfh2.groupby("hour")["revenue"].sum().idxmax() if not df.empty else 12
best_reg  = df.groupby("region")["revenue"].sum().idxmax() if not df.empty else "South"
low_cats  = df.groupby("category")["revenue"].sum().nsmallest(2).index.tolist()

d1, d2, d3, d4 = st.columns(4)
for col, lbl, val, sub in [
    (d1, "TOP OPPORTUNITY",   f"Expand {top_cat}",
     f"Highest revenue category — push premium SKUs"),
    (d2, "WEATHER ACTION",    f"Avoid {worst_wx}",
     f"Worst avg revenue condition — pause outdoor campaigns"),
    (d3, "PEAK SALES HOUR",   f"{best_hr:02d}:00 – {(best_hr+1)%24:02d}:00",
     f"Schedule flash-sales & email blasts in this window"),
    (d4, "REGION FOCUS",      f"{best_reg} Region",
     f"Top revenue region · Low performers: {', '.join(low_cats)}"),
]:
    col.markdown(f"""
    <div class="dec-card">
      <div class="dec-label">{lbl}</div>
      <div class="dec-val">{val}</div>
      <div class="dec-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;
            color:#334155;text-align:center;padding:1.2rem 0 0.5rem;
            border-top:1px solid #162035;margin-top:1rem;letter-spacing:0.2em;">
  ⚡ REVENUE PULSE · WAR ROOM COMMAND CENTER
  &nbsp;|&nbsp; WEATHER: OPENWEATHERMAP API
  &nbsp;|&nbsp; SALE ENGINE: 30s AUTO-GENERATE
  &nbsp;|&nbsp; AUTO-REFRESH: 5s
  &nbsp;|&nbsp; BUILT FOR COMMAND-LEVEL DECISIONS
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  AUTO-REFRESH  (keeps dashboard alive without manual click)
# ══════════════════════════════════════════════════════════
time.sleep(5)
st.rerun()
war_room_dashboard.py
Displaying war_room_dashboard.py.