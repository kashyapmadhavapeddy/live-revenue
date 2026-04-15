
import plotly.express as px @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@400;600;700&family=Share+Tech+Mono


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests, random, time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Revenue Pulse · War Room",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@400;600;700&family=Share+Tech+Mono&display=swap');

*, html, body, [class*="css"], .stApp {
    font-family: 'Exo 2', sans-serif !important;
    background-color: #020408 !important;
    color: #c8d8e8 !important;
}
.stApp { background: #020408 !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 0.8rem 1.5rem 2rem !important; max-width: 1800px !important; }
footer, [data-testid="stSidebar"] { display: none !important; }

.cmd-bar {
    background: linear-gradient(90deg, rgba(0,20,10,.97), rgba(0,15,30,.97));
    border-bottom: 1px solid rgba(0,255,136,.2);
    padding: 0.7rem 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
    margin: -0.8rem -1.5rem 1rem -1.5rem;
}
.brand { font-family: 'Orbitron', monospace; font-size: 1.5rem; font-weight: 900; color: #00ff88; letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,255,136,.7); }
.brand-sub { font-family: 'Share Tech Mono', monospace; font-size: .52rem; color: rgba(0,255,136,.45); letter-spacing: 3px; margin-top: 1px; }
.spill { display: inline-flex; align-items: center; gap: 6px; background: rgba(0,255,136,.08); border: 1px solid rgba(0,255,136,.25); border-radius: 3px; padding: 4px 12px; font-family: 'Share Tech Mono', monospace; font-size: .6rem; color: #00ff88; letter-spacing: 2px; }
.spill.w { background: rgba(255,170,0,.08); border-color: rgba(255,170,0,.25); color: #ffaa00; }
.spill.d { background: rgba(255,80,80,.08); border-color: rgba(255,80,80,.25); color: #ff5050; }
.blink { width: 6px; height: 6px; border-radius: 50%; background: #00ff88; animation: bl 1.2s infinite; box-shadow: 0 0 6px #00ff88; display: inline-block; }
@keyframes bl { 0%,100%{opacity:1} 50%{opacity:.2} }
.clk { font-family: 'Orbitron', monospace; font-size: .95rem; font-weight: 700; color: #00ccff; letter-spacing: 2px; }

.sec { font-family: 'Share Tech Mono', monospace; font-size: .55rem; letter-spacing: 4px; color: rgba(0,255,136,.6); display: flex; align-items: center; gap: .8rem; margin: 1.3rem 0 .7rem; }
.sec::before { content: ''; width: 3px; height: 12px; background: #00ff88; box-shadow: 0 0 8px #00ff88; }
.sec::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0,255,136,.3), transparent); }

.kcard { background: linear-gradient(135deg, rgba(0,20,12,.95), rgba(0,10,20,.95)); border: 1px solid rgba(0,255,136,.13); border-radius: 4px; padding: 1.1rem 1.3rem; position: relative; overflow: hidden; height: 128px; }
.kcard::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kcard.g::before { background: linear-gradient(90deg, transparent, #00ff88, transparent); }
.kcard.b::before { background: linear-gradient(90deg, transparent, #00ccff, transparent); }
.kcard.a::before { background: linear-gradient(90deg, transparent, #ffaa00, transparent); }
.kcard.r::before { background: linear-gradient(90deg, transparent, #ff5050, transparent); }
.kcard.p::before { background: linear-gradient(90deg, transparent, #aa88ff, transparent); }
.ktag { font-family: 'Share Tech Mono', monospace; font-size: .52rem; letter-spacing: 2px; color: rgba(180,200,180,.4); margin-bottom: .45rem; text-transform: uppercase; }
.knum { font-family: 'Orbitron', monospace; font-size: 1.7rem; font-weight: 700; line-height: 1; }
.knum.g { color: #00ff88; } .knum.b { color: #00ccff; } .knum.a { color: #ffaa00; } .knum.r { color: #ff5050; } .knum.p { color: #aa88ff; }
.kfoot { font-family: 'Share Tech Mono', monospace; font-size: .58rem; color: rgba(160,190,160,.4); margin-top: .35rem; }
.kdelta { font-family: 'Share Tech Mono', monospace; font-size: .62rem; margin-top: .18rem; }
.kdelta.u { color: #00ff88; } .kdelta.d { color: #ff5050; }
.kico { position: absolute; right: .9rem; bottom: .6rem; font-size: 2rem; opacity: .07; }

.ticker { background: rgba(0,8,4,.9); border: 1px solid rgba(0,255,136,.13); border-radius: 3px; padding: .4rem 0; overflow: hidden; margin-bottom: .5rem; position: relative; }
.tlbl { position: absolute; left: 0; top: 0; bottom: 0; background: rgba(0,255,136,.1); border-right: 1px solid rgba(0,255,136,.18); display: flex; align-items: center; padding: 0 .6rem; font-family: 'Orbitron', monospace; font-size: .48rem; color: #00ff88; letter-spacing: 2px; z-index: 2; }
.tscr { padding-left: 70px; font-family: 'Share Tech Mono', monospace; font-size: .65rem; white-space: nowrap; animation: tick 30s linear infinite; color: #90b890; letter-spacing: 1px; }
@keyframes tick { 0%{transform:translateX(100%)} 100%{transform:translateX(-100%)} }

.arow { display: flex; align-items: flex-start; gap: .5rem; background: rgba(0,255,136,.04); border: 1px solid rgba(0,255,136,.12); border-left: 3px solid #00ff88; border-radius: 3px; padding: .6rem .9rem; margin-bottom: .35rem; font-family: 'Share Tech Mono', monospace; font-size: .65rem; color: #88c890; }
.arow.w { background: rgba(255,170,0,.04); border-color: rgba(255,170,0,.15); border-left-color: #ffaa00; color: #d8b860; }
.arow.c { background: rgba(255,80,80,.04); border-color: rgba(255,80,80,.15); border-left-color: #ff5050; color: #e88888; }

.ccrd { background: linear-gradient(135deg, rgba(0,15,10,.92), rgba(0,8,18,.92)); border: 1px solid rgba(0,200,136,.1); border-radius: 4px; padding: .85rem .95rem; text-align: center; position: relative; overflow: hidden; }
.ccrd::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; }
.ccrd.boost::before { background: linear-gradient(90deg, transparent, #00ff88, transparent); }
.ccrd.hurt::before { background: linear-gradient(90deg, transparent, #ff5050, transparent); }
.ccrd.neutral::before { background: linear-gradient(90deg, transparent, #ffaa00, transparent); }
.cname { font-family: 'Orbitron', monospace; font-size: .68rem; font-weight: 700; color: #c8e8d8; letter-spacing: 2px; margin-bottom: .25rem; }
.cwea { font-family: 'Share Tech Mono', monospace; font-size: .55rem; color: rgba(140,190,150,.55); margin-bottom: .25rem; }
.cimpact { font-family: 'Exo 2', sans-serif; font-size: .95rem; font-weight: 700; margin-bottom: .18rem; }
.cimpact.boost { color: #00ff88; } .cimpact.hurt { color: #ff5050; } .cimpact.neutral { color: #ffaa00; }
.crev { font-family: 'Share Tech Mono', monospace; font-size: .57rem; color: rgba(140,190,140,.45); }

.prow { display: flex; align-items: center; gap: .7rem; background: rgba(0,12,8,.7); border: 1px solid rgba(0,255,136,.07); border-radius: 3px; padding: .5rem .7rem; margin-bottom: .3rem; }
.prnk { font-family: 'Orbitron', monospace; font-size: .6rem; color: rgba(0,255,136,.35); width: 16px; text-align: center; }
.pname { font-family: 'Exo 2', sans-serif; font-size: .78rem; font-weight: 600; color: #c8d8e8; flex: 1; }
.pcat { font-family: 'Share Tech Mono', monospace; font-size: .5rem; color: rgba(140,170,140,.45); letter-spacing: 1px; }
.pbg { width: 70px; height: 3px; background: rgba(0,255,136,.08); border-radius: 2px; overflow: hidden; }
.pfill { height: 100%; background: linear-gradient(90deg, #00ff88, #00ccff); border-radius: 2px; }
.prev { font-family: 'Orbitron', monospace; font-size: .6rem; color: #00ff88; min-width: 52px; text-align: right; }

.otbl { width: 100%; border-collapse: collapse; font-family: 'Share Tech Mono', monospace; font-size: .63rem; }
.otbl th { background: rgba(0,255,136,.05); border-bottom: 1px solid rgba(0,255,136,.13); color: rgba(0,255,136,.55); padding: .45rem .65rem; text-align: left; letter-spacing: 2px; font-size: .5rem; text-transform: uppercase; }
.otbl td { padding: .42rem .65rem; border-bottom: 1px solid rgba(0,255,136,.04); color: #88a888; }
.otbl tr:hover td { background: rgba(0,255,136,.03); color: #a8c8a8; }
.rc { color: #00ff88 !important; font-weight: 700; }
.wb { color: #00ff88 !important; } .wh { color: #ff5050 !important; } .wn { color: #ffaa00 !important; }

.icrd { background: linear-gradient(135deg, rgba(0,15,10,.92), rgba(0,8,18,.92)); border: 1px solid rgba(0,200,136,.1); border-radius: 4px; padding: .9rem 1rem; height: 100%; }
.itag { font-family: 'Share Tech Mono', monospace; font-size: .52rem; letter-spacing: 2.5px; color: rgba(140,190,140,.45); margin-bottom: .4rem; text-transform: uppercase; }
.ival { font-family: 'Orbitron', monospace; font-size: .95rem; font-weight: 700; color: #00ff88; margin-bottom: .28rem; }
.idesc { font-family: 'Share Tech Mono', monospace; font-size: .58rem; color: rgba(140,170,140,.45); line-height: 1.5; }

.stButton button { background: linear-gradient(135deg, rgba(0,255,136,.12), rgba(0,200,255,.08)) !important; border: 1px solid rgba(0,255,136,.28) !important; border-radius: 3px !important; color: #00ff88 !important; font-family: 'Share Tech Mono', monospace !important; font-size: .62rem !important; letter-spacing: 2px !important; }
hr { border-color: rgba(0,255,136,.1) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #020408; }
::-webkit-scrollbar-thumb { background: rgba(0,255,136,.18); border-radius: 2px; }
.ftr { font-family: 'Share Tech Mono', monospace; font-size: .5rem; color: rgba(0,255,136,.18); text-align: center; letter-spacing: 3px; margin-top: 2rem; padding: .7rem; border-top: 1px solid rgba(0,255,136,.07); }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
PRODUCTS = [
    ("UltraBook Pro",       "Electronics", 55000, 95000),
    ("Wireless Earbuds X",  "Electronics",  3500,  9500),
    ("Smart Watch Elite",   "Electronics", 14000, 42000),
    ("Gaming Monitor 4K",   "Electronics", 22000, 58000),
    ("Mechanical Keyboard", "Electronics",  5000, 18000),
    ("Office Chair Pro",    "Furniture",   10000, 28000),
    ("Standing Desk",       "Furniture",   18000, 45000),
    ("Running Shoes Z7",    "Apparel",      4500, 12000),
    ("Winter Jacket Pro",   "Apparel",      3500,  9500),
    ("Protein Powder 2kg",  "Health",       2200,  5500),
    ("Yoga Mat Premium",    "Health",       1200,  3500),
    ("Coffee Maker Pro",    "Appliances",   5500, 16000),
    ("Air Purifier 360",    "Appliances",   9500, 24000),
    ("USB-C Hub 10-in-1",   "Accessories",  2500,  7000),
    ("Noise Cancel ANC",    "Electronics",  8000, 25000),
    ("Backpack Ultra",      "Apparel",      2000,  6500),
]
CITIES = [
    ("Hyderabad", "South",  17.38,  78.47),
    ("Mumbai",    "West",   19.08,  72.88),
    ("Delhi",     "North",  28.70,  77.10),
    ("Bangalore", "South",  12.97,  77.59),
    ("Chennai",   "South",  13.08,  80.27),
    ("Kolkata",   "East",   22.57,  88.36),
    ("Pune",      "West",   18.52,  73.86),
    ("Ahmedabad", "West",   23.02,  72.57),
]
WEATHER = [
    ("Clear",         1.30, "☀️"),
    ("Partly Cloudy", 1.12, "⛅"),
    ("Cloudy",        0.92, "☁️"),
    ("Drizzle",       0.78, "🌦️"),
    ("Rain",          0.60, "🌧️"),
    ("Heavy Rain",    0.45, "⛈️"),
    ("Thunderstorm",  0.35, "⛈️"),
    ("Extreme Heat",  0.68, "🔥"),
    ("Foggy",         0.82, "🌫️"),
    ("Windy",         0.88, "💨"),
]
WIMPACT = {
    "Clear":         ("boost",   "+28%", "#00ff88"),
    "Partly Cloudy": ("boost",   "+10%", "#00dd66"),
    "Cloudy":        ("neutral", "±0%",  "#ffaa00"),
    "Drizzle":       ("hurt",    "-20%", "#ff8844"),
    "Rain":          ("hurt",    "-38%", "#ff5050"),
    "Heavy Rain":    ("hurt",    "-52%", "#ff3030"),
    "Thunderstorm":  ("hurt",    "-62%", "#ff1010"),
    "Extreme Heat":  ("hurt",    "-30%", "#ff6600"),
    "Foggy":         ("neutral", "-15%", "#ffcc00"),
    "Windy":         ("neutral", "-8%",  "#ffaa00"),
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [("sales", []), ("oc", 10001), ("lts", 0.0), ("wc", {}), ("wts", 0.0), ("tg", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

def gen_sale(ts=None):
    prod, cat, pmin, pmax = random.choice(PRODUCTS)
    city, reg, lat, lon   = random.choice(CITIES)
    weather, mult, emoji  = random.choice(WEATHER)
    qty   = random.choices([1, 2, 3, 4, 5], weights=[55, 25, 12, 5, 3])[0]
    price = random.randint(pmin, pmax)
    rev   = round(price * qty * (0.80 + mult * 0.20))
    oid   = f"RP-{st.session_state.oc:05d}"
    st.session_state.oc  += 1
    st.session_state.tg  += 1
    return {
        "timestamp": ts or datetime.now(),
        "order_id": oid, "product": prod, "category": cat,
        "price": price, "quantity": qty, "city": city,
        "region": reg, "weather_condition": weather,
        "weather_emoji": emoji, "revenue": rev,
    }

if not st.session_state.sales:
    now = datetime.now()
    for i in range(120):
        mins = (120 - i) * 3
        st.session_state.sales.append(gen_sale(now - timedelta(minutes=mins)))
    st.session_state.lts = time.time()

now_ts = time.time()
if (now_ts - st.session_state.lts) >= 30:
    st.session_state.sales.append(gen_sale())
    st.session_state.lts = now_ts

df = pd.DataFrame(st.session_state.sales).sort_values("timestamp", ascending=False).reset_index(drop=True)

# ── WEATHER API ───────────────────────────────────────────────────────────────
API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "") if hasattr(st, "secrets") else ""

def get_wx(city, lat, lon):
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"},
            timeout=5
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "desc": d["weather"][0]["description"].title(),
                "temp": round(d["main"]["temp"], 1),
                "humid": d["main"]["humidity"],
                "icon": d["weather"][0]["icon"],
            }
    except Exception:
        pass
    return None

if API_KEY and (now_ts - st.session_state.wts) > 600:
    for city, _, lat, lon in CITIES[:5]:
        w = get_wx(city, lat, lon)
        if w:
            st.session_state.wc[city] = w
    st.session_state.wts = now_ts

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fi(v):
    v = float(v)
    if v >= 1_00_00_000: return f"₹{v/1_00_00_000:.2f}Cr"
    if v >= 1_00_000:    return f"₹{v/1_00_000:.1f}L"
    if v >= 1000:        return f"₹{v/1000:.1f}K"
    return f"₹{v:,.0f}"

# ── FIXED chart layout — solid dark background so charts are always visible ───
PLOT_BG   = "#030d06"
PAPER_BG  = "#0a0f0a"
GRID_CLR  = "#0d2d14"
TICK_CLR  = "#4a8a5a"
TITLE_CLR = "#00cc66"

def chart_layout(title="", h=300, tickfmt=None):
    lo = dict(
        title=dict(text=title, font=dict(size=11, color=TITLE_CLR, family="Share Tech Mono"), x=0.01),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color="#6a9a6a", family="Exo 2", size=10),
        xaxis=dict(
            showgrid=True, gridcolor=GRID_CLR, zeroline=False,
            tickfont=dict(size=9, color=TICK_CLR),
            showline=True, linecolor="#1a3d20",
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_CLR, zeroline=True,
            zerolinecolor="#1a3d20",
            tickfont=dict(size=9, color=TICK_CLR),
            rangemode="tozero",
        ),
        margin=dict(l=50, r=20, t=45, b=40),
        legend=dict(
            bgcolor="rgba(10,15,10,.9)", bordercolor="#1a3d20", borderwidth=1,
            font=dict(size=9, color="#7ab87a"), orientation="h", y=1.08, x=0,
        ),
        height=h,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#051a09", bordercolor="#00ff88", font=dict(color="#c8e8c8", size=10)),
    )
    if tickfmt:
        lo["xaxis"]["tickformat"] = tickfmt
    return lo

# ── ANALYTICS ─────────────────────────────────────────────────────────────────
now_dt   = datetime.now()
tot_rev  = df["revenue"].sum()
tot_ord  = len(df)
aov      = df["revenue"].mean()
df_1h    = df[df["timestamp"] >= now_dt - timedelta(hours=1)]
df_ph    = df[(df["timestamp"] >= now_dt - timedelta(hours=2)) & (df["timestamp"] < now_dt - timedelta(hours=1))]
rev_1h   = df_1h["revenue"].sum()
rev_ph   = df_ph["revenue"].sum()
trend    = ((rev_1h - rev_ph) / max(rev_ph, 1)) * 100
df_30    = df[df["timestamp"] >= now_dt - timedelta(minutes=30)]
ord_30   = len(df_30)
rev_30   = df_30["revenue"].sum()
today_df = df[df["timestamp"].dt.date == now_dt.date()]
today_rev = today_df["revenue"].sum()
today_ord = len(today_df)
top_city = df.groupby("city")["revenue"].sum().idxmax()
top_prod = df.groupby("product")["revenue"].sum().idxmax()
top_cat  = df.groupby("category")["revenue"].sum().idxmax()
top_reg  = df.groupby("region")["revenue"].sum().idxmax()

# ── COMMAND BAR ───────────────────────────────────────────────────────────────
arrow = "▲" if trend >= 0 else "▼"
tc    = "spill" if trend >= 0 else ("spill w" if trend > -15 else "spill d")
st.markdown(f"""
<div class="cmd-bar">
  <div>
    <div class="brand">⚡ Revenue Pulse</div>
    <div class="brand-sub">Live Sales Intelligence · War Room</div>
  </div>
  <div style="display:flex;align-items:center;gap:1.2rem;">
    <div class="{tc}"><span class="blink"></span>&nbsp;LIVE · {tot_ord} ORDERS</div>
    <div class="spill">TREND {arrow} {abs(trend):.1f}%</div>
    <div>
      <div class="clk">{now_dt.strftime('%H:%M:%S')}</div>
      <div style="font-family:Share Tech Mono,monospace;font-size:.52rem;color:rgba(0,200,255,.45);letter-spacing:2px;text-align:right;">{now_dt.strftime('%d %b %Y')}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TICKER ────────────────────────────────────────────────────────────────────
tick_items = "   ·   ".join([
    f"🟢 {r['order_id']} · {r['product']} · {r['city']} · {fi(r['revenue'])}"
    for _, r in df.head(6).iterrows()
])
tick_items += f"   ·   📊 TODAY {fi(today_rev)} · TOP {top_city} · BEST {top_prod}"
st.markdown(
    f'<div class="ticker"><div class="tlbl">LIVE</div><div class="tscr">{tick_items}</div></div>',
    unsafe_allow_html=True
)

_, bc = st.columns([8, 1])
with bc:
    if st.button("⟳ REFRESH"):
        st.rerun()

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">COMMAND METRICS · REAL-TIME</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)

def kcard(col, cls, tag, num, delta, foot, ico, dcls="u"):
    col.markdown(
        f'<div class="kcard {cls}">'
        f'<div class="ktag">{tag}</div>'
        f'<div class="knum {cls}">{num}</div>'
        f'<div class="kdelta {dcls}">{delta}</div>'
        f'<div class="kfoot">{foot}</div>'
        f'<div class="kico">{ico}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

kcard(k1, "g", "Total Revenue",   fi(tot_rev),               "▲ All time",         f"{tot_ord} orders",                  "💰")
kcard(k2, "g" if trend >= 0 else "r", "Revenue Trend",
      f"{'▲' if trend >= 0 else '▼'}{abs(trend):.1f}%",
      f"{fi(rev_1h)} this hr", f"prev: {fi(rev_ph)}", "📈", "u" if trend >= 0 else "d")
kcard(k3, "a", "Orders · 30 Min", str(ord_30),                f"{fi(rev_30)} revenue", f"avg {fi(rev_30/max(ord_30,1))}/order", "📦")
kcard(k4, "b", "Avg Order Value",  fi(aov),                   "Per transaction",    f"Best: {top_prod[:14]}",              "🧾")
kcard(k5, "p", "Today Revenue",    fi(today_rev),             f"{today_ord} orders", f"Top: {top_city}",                  "🏆")
kcard(k6, "b", "Conv. Rate",       f"{round(random.uniform(3.2,4.8),1)}%", "Session avg", f"Top: {top_reg}",             "🎯")

# ── WEATHER CARDS ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec">🌦 WEATHER INTELLIGENCE · CITY SALES IMPACT</div>', unsafe_allow_html=True)
wcols = st.columns(5)
for i, (city, reg, lat, lon) in enumerate(CITIES[:5]):
    city_rev = df[df["city"] == city]["revenue"].sum()
    city_ord = len(df[df["city"] == city])
    wd = st.session_state.wc.get(city)
    if wd:
        ik = next((k for k in WIMPACT if k.lower() in wd["desc"].lower()), "Cloudy")
        ic, ip, icolor = WIMPACT[ik]
        icon_h = f'<img src="https://openweathermap.org/img/wn/{wd["icon"]}@2x.png" style="width:36px;height:36px;">'
        detail = f'{wd["desc"]} · {wd["temp"]}°C'
    else:
        cdf = df[df["city"] == city]
        tw  = cdf["weather_condition"].mode().iloc[0] if not cdf.empty else "Cloudy"
        ic, ip, icolor = WIMPACT.get(tw, ("neutral", "±0%", "#ffaa00"))
        emoji  = next((e for w, _, e in WEATHER if w == tw), "🌡️")
        icon_h = f'<div style="font-size:2rem;line-height:1;">{emoji}</div>'
        detail = tw
    with wcols[i]:
        st.markdown(
            f'<div class="ccrd {ic}">{icon_h}'
            f'<div class="cname">{city.upper()}</div>'
            f'<div class="cwea">{detail}</div>'
            f'<div class="cimpact {ic}" style="color:{icolor};">{ip}</div>'
            f'<div class="crev">{fi(city_rev)} · {city_ord} orders</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ── ALERTS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">⚠ SMART ALERT ENGINE</div>', unsafe_allow_html=True)
t = now_dt.strftime("%H:%M:%S")
alerts = []
if trend > 20:
    alerts.append(("", f"🚀 SURGE [{t}] — Revenue ▲{abs(trend):.1f}% vs last hour. Increase ad spend on {top_cat} now."))
elif trend < -20:
    alerts.append(("c", f"🚨 CRITICAL DROP [{t}] — Revenue ▼{abs(trend):.1f}%. Immediate investigation in {top_city}."))
elif trend < -8:
    alerts.append(("w", f"📉 DECLINE [{t}] — Down {abs(trend):.1f}%. Consider flash discount push."))
else:
    alerts.append(("", f"📈 STABLE [{t}] — Revenue flowing steadily. {top_cat} leading all categories."))

rc2 = df[df["weather_condition"].isin(["Rain", "Heavy Rain", "Thunderstorm"])]["city"].unique().tolist()
if rc2:
    alerts.append(("w", f"🌧️ WEATHER [{t}] — Rain in {', '.join(rc2)}. Boost online deals to offset 30–60% drop."))

hc2 = df[df["weather_condition"] == "Extreme Heat"]["city"].unique().tolist()
if hc2:
    alerts.append(("w", f"🔥 HEAT [{t}] — Extreme heat in {', '.join(hc2)}. Push home delivery offers."))

cc2 = df[df["weather_condition"] == "Clear"]["city"].unique().tolist()
if cc2:
    alerts.append(("", f"☀️ OPPORTUNITY [{t}] — Clear skies in {', '.join(cc2[:3])}. +28% avg conversion expected."))

if ord_30 == 0:
    alerts.append(("c", f"⛔ PIPELINE DEAD [{t}] — Zero orders in 30 min. Check payment gateway."))
elif ord_30 < 3:
    alerts.append(("w", f"⚠️ LOW VOLUME [{t}] — Only {ord_30} orders in 30 min. Deploy push campaign."))
elif ord_30 > 8:
    alerts.append(("", f"⚡ HIGH VELOCITY [{t}] — {ord_30} orders in 30 min. Monitor inventory for {top_prod}."))

alerts.append(("", f"🏆 LEADER [{t}] — {top_cat} dominates. {top_prod} is #1 SKU. {top_reg} region outperforming."))

for cls, msg in alerts:
    st.markdown(f'<div class="arow {cls}">{msg}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# CHARTS
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📊 REVENUE ANALYTICS</div>', unsafe_allow_html=True)

# ── ROW 1: Time-series + Pie ───────────────────────────────────────
ch1, ch2 = st.columns([2.2, 1])

with ch1:
    dft = df.copy()
    dft["b"] = dft["timestamp"].dt.floor("5min")
    rt = (dft.groupby("b")
             .agg(rev=("revenue", "sum"), ord=("order_id", "count"))
             .reset_index()
             .sort_values("b"))
    rt["ma"] = rt["rev"].rolling(3, min_periods=1).mean()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=rt["b"], y=rt["rev"],
        fill="tozeroy", fillcolor="rgba(0,200,100,.10)",
        line=dict(color="#00ff88", width=2.5),
        mode="lines+markers",
        marker=dict(size=5, color="#00ff88", line=dict(width=1, color="#002a10")),
        name="Revenue",
        hovertemplate="<b>%{x|%H:%M}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig1.add_trace(go.Scatter(
        x=rt["b"], y=rt["ma"],
        line=dict(color="#ffaa00", width=2, dash="dot"),
        mode="lines", name="Trend (MA3)",
        hovertemplate="Trend ₹%{y:,.0f}<extra></extra>",
    ))
    fig1.add_trace(go.Bar(
        x=rt["b"], y=rt["ord"],
        marker_color="rgba(0,180,255,.22)", marker_line_width=0,
        name="Orders", yaxis="y2",
        hovertemplate="Orders: %{y}<extra></extra>",
    ))
    lo1 = chart_layout("REVENUE + ORDER VOLUME  (5-MIN BUCKETS)", 310, tickfmt="%H:%M")
    lo1["yaxis2"] = dict(
        overlaying="y", side="right", showgrid=False, zeroline=False,
        tickfont=dict(size=8, color="rgba(0,180,255,.5)"), rangemode="tozero",
    )
    lo1["bargap"] = 0.05
    fig1.update_layout(**lo1)
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

with ch2:
    cr = df.groupby("category")["revenue"].sum().reset_index()
    CLR = ["#00ff88", "#00ccff", "#ffaa00", "#aa88ff", "#ff8844", "#ff5088"]
    fig2 = go.Figure(go.Pie(
        labels=cr["category"], values=cr["revenue"], hole=0.65,
        marker=dict(colors=CLR[:len(cr)], line=dict(color=PAPER_BG, width=3)),
        textfont=dict(size=9, family="Share Tech Mono", color="#c8e8c8"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
        textposition="outside",
    ))
    lo2 = chart_layout("CATEGORY REVENUE SPLIT", 310)
    lo2["showlegend"] = True
    lo2["annotations"] = [dict(
        text=f"<b>{top_cat[:8]}</b>", x=0.5, y=0.5,
        font=dict(size=11, color="#00ff88", family="Orbitron"), showarrow=False,
    )]
    fig2.update_layout(**lo2)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ── ROW 2: City bar + Weather bar ─────────────────────────────────
ch3, ch4 = st.columns(2)

with ch3:
    cir = df.groupby("city")["revenue"].sum().sort_values(ascending=True).reset_index()
    fig3 = go.Figure(go.Bar(
        y=cir["city"], x=cir["revenue"], orientation="h",
        marker=dict(
            color=cir["revenue"].tolist(),
            colorscale=[[0, "#002210"], [0.4, "#006640"], [1, "#00ff88"]],
            line=dict(width=0),
        ),
        text=[fi(v) for v in cir["revenue"]], textposition="inside",
        textfont=dict(size=9, color="#003318"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    lo3 = chart_layout("REVENUE BY CITY", 280)
    lo3["yaxis"]["showgrid"] = False
    lo3["showlegend"] = False
    fig3.update_layout(**lo3)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with ch4:
    wr = df.groupby("weather_condition")["revenue"].sum().sort_values(ascending=False).reset_index()
    wcolors = [
        "#00ff88" if WIMPACT.get(w, ("n",))[0] == "boost"
        else "#ff5050" if WIMPACT.get(w, ("n",))[0] == "hurt"
        else "#ffaa00"
        for w in wr["weather_condition"]
    ]
    fig4 = go.Figure(go.Bar(
        x=wr["weather_condition"], y=wr["revenue"],
        marker=dict(color=wcolors, line=dict(width=0)),
        text=[fi(v) for v in wr["revenue"]], textposition="outside",
        textfont=dict(size=8, color="#8ab88a"),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    lo4 = chart_layout("REVENUE BY WEATHER CONDITION", 280)
    lo4["xaxis"]["tickangle"] = -30
    lo4["showlegend"] = False
    fig4.update_layout(**lo4)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# ── ROW 3: Heatmap + Leaderboard ──────────────────────────────────
ch5, ch6 = st.columns([1.6, 1])

with ch5:
    dfh = df.copy()
    dfh["hour"] = dfh["timestamp"].dt.hour
    piv = (dfh.groupby(["city", "hour"])["revenue"]
              .sum().reset_index()
              .pivot(index="city", columns="hour", values="revenue")
              .fillna(0))
    fig5 = go.Figure(go.Heatmap(
        z=piv.values,
        x=[f"{h:02d}:00" for h in piv.columns],
        y=piv.index.tolist(),
        colorscale=[[0, "#020408"], [.15, "#001a0d"], [.4, "#004d20"], [.7, "#00aa55"], [1, "#00ff88"]],
        hovertemplate="<b>%{y}</b> · %{x}<br>₹%{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(size=8, color="rgba(0,200,100,.5)"), thickness=10, len=0.9),
    ))
    lo5 = chart_layout("REVENUE HEATMAP · CITY × HOUR OF DAY", 280)
    lo5["xaxis"]["showgrid"] = False
    lo5["yaxis"]["showgrid"] = False
    lo5["showlegend"] = False
    fig5.update_layout(**lo5)
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

with ch6:
    st.markdown('<div class="sec" style="margin-top:.4rem;">🏆 PRODUCT LEADERBOARD</div>', unsafe_allow_html=True)
    pr  = (df.groupby(["product", "category"])["revenue"]
             .sum().sort_values(ascending=False).head(8).reset_index())
    mx  = pr["revenue"].max()
    for rank, (_, row) in enumerate(pr.iterrows(), 1):
        pct = (row["revenue"] / mx) * 100
        st.markdown(
            f'<div class="prow">'
            f'<div class="prnk">#{rank}</div>'
            f'<div style="flex:1;">'
            f'  <div class="pname">{row["product"]}</div>'
            f'  <div class="pcat">{row["category"].upper()}</div>'
            f'  <div class="pbg" style="margin-top:4px;"><div class="pfill" style="width:{pct:.0f}%;"></div></div>'
            f'</div>'
            f'<div class="prev">{fi(row["revenue"])}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ── ROW 4: Treemap + Hourly pattern ───────────────────────────────
ch7, ch8 = st.columns(2)

with ch7:
    rc3 = df.groupby(["region", "category"])["revenue"].sum().reset_index()
    fig6 = px.treemap(
        rc3, path=["region", "category"], values="revenue", color="revenue",
        color_continuous_scale=[[0, "#001a0d"], [0.5, "#006640"], [1, "#00ff88"]],
    )
    fig6.update_traces(
        textfont=dict(family="Share Tech Mono", size=10, color="#c8e8c8"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>",
        marker=dict(line=dict(color=PAPER_BG, width=2)),
    )
    lo6 = chart_layout("REVENUE TREEMAP · REGION × CATEGORY", 280)
    lo6["showlegend"]           = False
    lo6["margin"]               = dict(l=4, r=4, t=32, b=4)
    lo6["coloraxis_showscale"]  = False
    fig6.update_layout(**lo6)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

with ch8:
    dfhr = df.copy()
    dfhr["hour"] = dfhr["timestamp"].dt.hour
    hr = dfhr.groupby("hour").agg(rev=("revenue", "sum"), ord=("order_id", "count")).reset_index()
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=hr["hour"], y=hr["rev"],
        fill="tozeroy", fillcolor="rgba(0,180,255,.08)",
        line=dict(color="#00ccff", width=2.5),
        mode="lines+markers", marker=dict(size=5, color="#00ccff"),
        name="Revenue",
        hovertemplate="<b>%{x}:00</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig7.add_trace(go.Scatter(
        x=hr["hour"], y=hr["ord"],
        fill="tozeroy", fillcolor="rgba(170,136,255,.06)",
        line=dict(color="#aa88ff", width=2, dash="dot"),
        mode="lines+markers", marker=dict(size=4, color="#aa88ff"),
        name="Orders", yaxis="y2",
        hovertemplate="<b>%{x}:00</b><br>Orders: %{y}<extra></extra>",
    ))
    lo7 = chart_layout("HOURLY REVENUE + ORDERS PATTERN", 280)
    lo7["yaxis2"] = dict(
        overlaying="y", side="right", showgrid=False, zeroline=False,
        tickfont=dict(size=8, color="rgba(170,136,255,.5)"), rangemode="tozero",
    )
    lo7["xaxis"]["dtick"] = 2
    fig7.update_layout(**lo7)
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

# ── LIVE ORDER FEED ───────────────────────────────────────────────────────────
st.markdown('<div class="sec">📡 LIVE ORDER FEED · REAL-TIME TRANSACTIONS</div>', unsafe_allow_html=True)
rows = ""
for _, row in df.head(12).iterrows():
    rc_cls = WIMPACT.get(row["weather_condition"], ("neutral", "", ""))[0]
    wcls   = {"boost": "wb", "hurt": "wh", "neutral": "wn"}.get(rc_cls, "wn")
    rows  += (
        f'<tr>'
        f'<td style="color:rgba(0,255,136,.38);font-size:.56rem;">{row["timestamp"].strftime("%H:%M:%S")}</td>'
        f'<td style="color:rgba(0,200,255,.65);">{row["order_id"]}</td>'
        f'<td>{row["product"]}</td>'
        f'<td style="color:rgba(170,140,255,.65);">{row["category"]}</td>'
        f'<td style="text-align:center;">{row["quantity"]}</td>'
        f'<td>{row["city"]}</td>'
        f'<td class="{wcls}">{row.get("weather_emoji","🌡️")} {row["weather_condition"]}</td>'
        f'<td class="rc">{fi(row["revenue"])}</td>'
        f'</tr>'
    )
st.markdown(
    f'<div style="background:{PLOT_BG};border:1px solid rgba(0,255,136,.1);border-radius:4px;overflow:hidden;">'
    f'<table class="otbl"><thead><tr>'
    f'<th>TIME</th><th>ORDER ID</th><th>PRODUCT</th><th>CATEGORY</th>'
    f'<th>QTY</th><th>CITY</th><th>WEATHER</th><th>REVENUE</th>'
    f'</tr></thead><tbody>{rows}</tbody></table></div>',
    unsafe_allow_html=True
)

# ── MANAGER INTELLIGENCE ──────────────────────────────────────────────────────
st.markdown('<div class="sec">📋 MANAGER INTELLIGENCE PANEL</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

best_w   = df.groupby("weather_condition")["revenue"].mean().idxmax() if tot_ord > 0 else "Clear"
dfhr2    = df.copy()
dfhr2["hour"] = dfhr2["timestamp"].dt.hour
peak_hr  = dfhr2.groupby("hour")["revenue"].sum().idxmax() if tot_ord > 0 else 12
worst_c  = df.groupby("city")["revenue"].sum().idxmin()  if tot_ord > 0 else "N/A"
worst_r  = df.groupby("city")["revenue"].sum().min()     if tot_ord > 0 else 0
target   = 200000.0
pct_tgt  = min((tot_rev / target) * 100, 100)

for col, (tag, val, desc) in zip([m1, m2, m3, m4], [
    ("🌤 BEST WEATHER",     best_w,
     "Highest avg revenue per order. Schedule major campaigns on this condition."),
    ("⏰ PEAK HOUR",         f"{peak_hr:02d}:00–{peak_hr+1:02d}:00",
     "Deploy push campaigns 30 min before this window."),
    ("⚠ UNDERPERFORMING",   f"{worst_c}",
     f"Only {fi(worst_r)} revenue. Investigate local factors."),
    ("🎯 SESSION TARGET",    f"{pct_tgt:.0f}%",
     f"{fi(tot_rev)} of {fi(target)} target. Need {fi(max(target-tot_rev,0))} more."),
]):
    col.markdown(
        f'<div class="icrd">'
        f'<div class="itag">{tag}</div>'
        f'<div class="ival">{val}</div>'
        f'<div class="idesc">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown(
    f'<div class="ftr">REVENUE PULSE WAR ROOM · {st.session_state.tg} ORDERS GENERATED · AUTO-REFRESH 30s · {now_dt.strftime("%d %b %Y %H:%M:%S")}</div>',
    unsafe_allow_html=True
)

st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)
