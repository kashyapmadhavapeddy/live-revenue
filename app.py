"""
Revenue Pulse War Room — app.py
Self-contained: No external script needed.
Data generates automatically inside the app every 30 seconds.
Manager opens link → live data immediately. Works on Streamlit Cloud.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests, random, time
from datetime import datetime, timedelta

st.set_page_config(page_title="Revenue Pulse · War Room", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');
*, html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif !important; background-color: #030712; color: #e2e8f0; }
.stApp { background: #030712; background-image: radial-gradient(ellipse 60% 40% at 10% 0%, rgba(16,185,129,0.06) 0%, transparent 60%), radial-gradient(ellipse 50% 40% at 90% 100%, rgba(245,158,11,0.05) 0%, transparent 60%); }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1600px; }
.wr-title { font-family:'Rajdhani',sans-serif; font-size:2.2rem; font-weight:700; color:#10b981; letter-spacing:3px; text-transform:uppercase; text-shadow:0 0 30px rgba(16,185,129,0.4); }
.wr-subtitle { font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#374151; letter-spacing:2px; text-transform:uppercase; margin-top:2px; }
.live-badge { display:inline-flex; align-items:center; gap:6px; background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:20px; padding:4px 14px; font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#10b981; letter-spacing:2px; }
.live-dot { width:7px; height:7px; background:#10b981; border-radius:50%; animation:pulse 1.5s infinite; display:inline-block; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1);}50%{opacity:0.4;transform:scale(0.8);} }
.kpi-card { background:linear-gradient(145deg,#0d1117,#111827); border:1px solid #1f2937; border-radius:12px; padding:1.3rem 1.5rem; position:relative; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.5); height:135px; }
.kpi-card::after { content:''; position:absolute; bottom:0; left:0; right:0; height:1px; }
.kpi-card.green::after  { background:linear-gradient(90deg,transparent,#10b981,transparent); }
.kpi-card.amber::after  { background:linear-gradient(90deg,transparent,#f59e0b,transparent); }
.kpi-card.blue::after   { background:linear-gradient(90deg,transparent,#38bdf8,transparent); }
.kpi-card.red::after    { background:linear-gradient(90deg,transparent,#ef4444,transparent); }
.kpi-card.purple::after { background:linear-gradient(90deg,transparent,#a78bfa,transparent); }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:2px; text-transform:uppercase; color:#4b5563; margin-bottom:0.4rem; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:2rem; font-weight:700; line-height:1.1; }
.kpi-value.green  { color:#10b981; text-shadow:0 0 20px rgba(16,185,129,0.3); }
.kpi-value.amber  { color:#f59e0b; text-shadow:0 0 20px rgba(245,158,11,0.3); }
.kpi-value.blue   { color:#38bdf8; text-shadow:0 0 20px rgba(56,189,248,0.3); }
.kpi-value.red    { color:#ef4444; text-shadow:0 0 20px rgba(239,68,68,0.3); }
.kpi-value.purple { color:#a78bfa; text-shadow:0 0 20px rgba(167,139,250,0.3); }
.kpi-sub { font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:#6b7280; margin-top:0.3rem; }
.kpi-icon { position:absolute; top:1rem; right:1rem; font-size:1.6rem; opacity:0.12; }
.sec-header { font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:3px; text-transform:uppercase; color:#10b981; border-left:2px solid #10b981; padding-left:0.7rem; margin:1.5rem 0 0.8rem 0; }
.alert-ticker { background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2); border-radius:8px; padding:0.6rem 1rem; font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#fcd34d; margin-bottom:0.4rem; }
.alert-ticker.green { background:rgba(16,185,129,0.08); border-color:rgba(16,185,129,0.2); color:#6ee7b7; }
.alert-ticker.red   { background:rgba(239,68,68,0.08);  border-color:rgba(239,68,68,0.2);  color:#fca5a5; }
.stButton button { background:linear-gradient(135deg,#059669,#047857)!important; border:none!important; border-radius:8px!important; color:white!important; font-family:'Share Tech Mono',monospace!important; font-size:0.72rem!important; letter-spacing:1px!important; padding:0.4rem 1.2rem!important; }
hr { border-color:#1f2937!important; }
::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#030712;} ::-webkit-scrollbar-thumb{background:#1f2937;border-radius:4px;}
.timestamp { font-family:'Share Tech Mono',monospace; font-size:0.62rem; color:#1f2937; letter-spacing:1px; }
</style>
""", unsafe_allow_html=True)

PRODUCTS = [
    ("UltraBook Pro","Electronics",45000,85000),("Wireless Earbuds","Electronics",2500,8000),
    ("Smart Watch","Electronics",12000,35000),("Office Chair","Furniture",8000,25000),
    ("Standing Desk","Furniture",15000,40000),("Running Shoes","Apparel",3000,9000),
    ("Winter Jacket","Apparel",2500,7500),("Protein Powder","Health",1500,4500),
    ("Yoga Mat","Health",800,2500),("Coffee Maker","Appliances",3500,12000),
    ("Air Purifier","Appliances",8000,20000),("Mechanical Keyboard","Electronics",4000,15000),
    ("Monitor 4K","Electronics",18000,45000),("Water Bottle","Health",500,1800),
    ("Backpack","Apparel",1500,5000),
]
CITIES = [("Hyderabad","South"),("Mumbai","West"),("Delhi","North"),
          ("Bangalore","South"),("Chennai","South"),("Kolkata","East"),
          ("Pune","West"),("Ahmedabad","West")]
WEATHER_PROFILES = [
    ("Clear",1.25),("Partly Cloudy",1.10),("Cloudy",0.95),("Drizzle",0.80),
    ("Rain",0.65),("Heavy Rain",0.50),("Thunderstorm",0.40),
    ("Extreme Heat",0.70),("Foggy",0.85),("Windy",0.90),
]
WEATHER_IMPACT = {
    "Clear":("boost","+18% vs avg","🟢"),"Partly Cloudy":("boost","+8% vs avg","🟢"),
    "Cloudy":("neutral","±0% vs avg","🟡"),"Drizzle":("hurt","-18% vs avg","🔴"),
    "Rain":("hurt","-32% vs avg","🔴"),"Heavy Rain":("hurt","-48% vs avg","🔴"),
    "Thunderstorm":("hurt","-58% vs avg","🔴"),"Extreme Heat":("hurt","-28% vs avg","🔴"),
    "Foggy":("neutral","-8% vs avg","🟡"),"Windy":("neutral","-6% vs avg","🟡"),
}

if "sales" not in st.session_state:
    st.session_state.sales=[];st.session_state.order_counter=1001
    st.session_state.last_sale_ts=0;st.session_state.weather_cache={}
    st.session_state.weather_ts=0

def generate_sale(ts=None):
    product,category,pmin,pmax=random.choice(PRODUCTS)
    city,region=random.choice(CITIES)
    weather,mult=random.choice(WEATHER_PROFILES)
    quantity=random.choices([1,2,3,4,5],weights=[50,25,15,7,3])[0]
    price=random.randint(pmin,pmax)
    revenue=round(price*quantity*(0.85+mult*0.15))
    oid=f"ORD-{st.session_state.order_counter}"
    st.session_state.order_counter+=1
    return {"timestamp":ts or datetime.now(),"order_id":oid,"product":product,
            "category":category,"price":price,"quantity":quantity,"city":city,
            "region":region,"weather_condition":weather,"revenue":revenue}

if len(st.session_state.sales)==0:
    now=datetime.now()
    for i in range(50):
        ts=now-timedelta(minutes=random.randint(1,120))
        st.session_state.sales.append(generate_sale(ts))
    st.session_state.sales.sort(key=lambda x:x["timestamp"])

now_ts=time.time()
if (now_ts-st.session_state.last_sale_ts)>=30:
    st.session_state.sales.append(generate_sale())
    st.session_state.last_sale_ts=now_ts

df=pd.DataFrame(st.session_state.sales).sort_values("timestamp",ascending=False).reset_index(drop=True)

API_KEY=st.secrets.get("OPENWEATHER_API_KEY","")
def get_weather(city):
    if not API_KEY: return None
    try:
        r=requests.get("https://api.openweathermap.org/data/2.5/weather",
                       params={"q":city+",IN","appid":API_KEY,"units":"metric"},timeout=5)
        if r.status_code==200:
            d=r.json()
            return {"city":city,"desc":d["weather"][0]["description"].title(),
                    "temp":round(d["main"]["temp"],1),"icon":d["weather"][0]["icon"]}
    except: pass
    return None

if API_KEY and (now_ts-st.session_state.weather_ts)>600:
    for city,_ in CITIES[:5]:
        w=get_weather(city)
        if w: st.session_state.weather_cache[city]=w
    st.session_state.weather_ts=now_ts

def fmt_inr(val):
    if val>=1_00_00_000: return f"₹{val/1_00_00_000:.2f}Cr"
    elif val>=1_00_000:  return f"₹{val/1_00_000:.2f}L"
    else:                return f"₹{val:,.0f}"

def base_layout(title="",height=300):
    return dict(
        title=dict(text=title,font=dict(size=11,color="#10b981",family="Share Tech Mono, monospace"),x=0.01),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#6b7280",family="Rajdhani, sans-serif",size=11),
        xaxis=dict(showgrid=True,gridcolor="#111827",zeroline=False,tickfont=dict(size=9,color="#4b5563")),
        yaxis=dict(showgrid=True,gridcolor="#111827",zeroline=False,tickfont=dict(size=9,color="#4b5563")),
        margin=dict(l=10,r=10,t=35,b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9),orientation="h",y=1.12),
        height=height)

total_revenue=df["revenue"].sum();total_orders=len(df);avg_order_value=df["revenue"].mean()
top_city=df.groupby("city")["revenue"].sum().idxmax()
top_product=df.groupby("product")["revenue"].sum().idxmax()
top_category=df.groupby("category")["revenue"].sum().idxmax()
now_dt=datetime.now()
one_hr=df[df["timestamp"]>=now_dt-timedelta(hours=1)]
prev_hr=df[(df["timestamp"]>=now_dt-timedelta(hours=2))&(df["timestamp"]<now_dt-timedelta(hours=1))]
rev_trend=((one_hr["revenue"].sum()-prev_hr["revenue"].sum())/max(prev_hr["revenue"].sum(),1))*100
last_30=df[df["timestamp"]>=now_dt-timedelta(minutes=30)];orders_30=len(last_30)
today_rev=df[df["timestamp"].dt.date==now_dt.date()]["revenue"].sum()

h1,h2,h3=st.columns([3,2,1])
with h1:
    st.markdown('<div class="wr-title">⚡ Revenue Pulse</div><div class="wr-subtitle">Live Sales Command Center · New sale every 30s · Weather integrated</div>',unsafe_allow_html=True)
with h2:
    now_str=datetime.now().strftime("%d %b %Y · %H:%M:%S")
    st.markdown(f'<div style="text-align:right;padding-top:0.8rem;"><div class="live-badge"><span class="live-dot"></span> LIVE · {total_orders} ORDERS</div><div class="timestamp" style="margin-top:6px;">SYNCED · {now_str}</div></div>',unsafe_allow_html=True)
with h3:
    st.markdown("<br>",unsafe_allow_html=True);st.button("⟳ Sync Now")
st.markdown("---")

st.markdown('<div class="sec-header">LIVE METRICS · COMMAND OVERVIEW</div>',unsafe_allow_html=True)
k1,k2,k3,k4,k5=st.columns(5)
with k1: st.markdown(f'<div class="kpi-card green"><div class="kpi-icon">💰</div><div class="kpi-label">Total Revenue</div><div class="kpi-value green">{fmt_inr(total_revenue)}</div><div class="kpi-sub">All time · {total_orders} orders</div></div>',unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card amber"><div class="kpi-icon">📦</div><div class="kpi-label">Orders · Last 30 Min</div><div class="kpi-value amber">{orders_30}</div><div class="kpi-sub">Live order volume</div></div>',unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card blue"><div class="kpi-icon">🧾</div><div class="kpi-label">Avg Order Value</div><div class="kpi-value blue">{fmt_inr(avg_order_value)}</div><div class="kpi-sub">Per transaction</div></div>',unsafe_allow_html=True)
with k4:
    arrow="▲" if rev_trend>=0 else "▼";cls="green" if rev_trend>=0 else "red"
    st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-icon">📈</div><div class="kpi-label">Revenue Trend</div><div class="kpi-value {cls}">{arrow} {abs(rev_trend):.1f}%</div><div class="kpi-sub">vs previous hour</div></div>',unsafe_allow_html=True)
with k5: st.markdown(f'<div class="kpi-card purple"><div class="kpi-icon">🏆</div><div class="kpi-label">Today\'s Revenue</div><div class="kpi-value purple">{fmt_inr(today_rev)}</div><div class="kpi-sub">Top city: {top_city}</div></div>',unsafe_allow_html=True)

st.markdown('<div class="sec-header">🌦 WEATHER × SALES IMPACT · LIVE CITY FEED</div>',unsafe_allow_html=True)
city_list=[c[0] for c in CITIES[:5]];wdata=st.session_state.weather_cache;wcc=st.columns(5)
for i,city in enumerate(city_list):
    wd=wdata.get(city);city_rev=df[df["city"]==city]["revenue"].sum()
    if wd:
        ik=next((k for k in WEATHER_IMPACT if k.lower() in wd["desc"].lower()),"Cloudy")
        ic,ip,dot=WEATHER_IMPACT[ik];border="#10b981" if ic=="boost" else "#ef4444" if ic=="hurt" else "#f59e0b"
        icon_h=f'<img src="https://openweathermap.org/img/wn/{wd["icon"]}@2x.png" style="width:36px;height:36px;filter:drop-shadow(0 0 8px {border}60);">'
        detail=f'{wd["desc"]} · {wd["temp"]}°C'
    else:
        cdf=df[df["city"]==city];tw=cdf["weather_condition"].mode()[0] if not cdf.empty else "Cloudy"
        ic,ip,dot=WEATHER_IMPACT.get(tw,("neutral","±0%","🟡"))
        border="#10b981" if ic=="boost" else "#ef4444" if ic=="hurt" else "#f59e0b"
        icon_h="<div style='font-size:2rem;'>🌡️</div>";detail=tw
    with wcc[i]:
        st.markdown(f'<div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-top:2px solid {border};border-radius:12px;padding:1rem;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.4);">{icon_h}<div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#e2e8f0;">{city}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#6b7280;">{detail}</div><div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;color:{border};margin-top:0.3rem;">{dot} {ip}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4b5563;margin-top:2px;">Rev: {fmt_inr(city_rev)}</div></div>',unsafe_allow_html=True)

st.markdown('<div class="sec-header">⚠ SMART ALERTS · MANAGER ACTION REQUIRED</div>',unsafe_allow_html=True)
alerts=[]
if rev_trend>20:    alerts.append(("green",f"🚀 SURGE DETECTED — Revenue up {rev_trend:.1f}% vs last hour. Consider increasing ad spend now."))
elif rev_trend<-20: alerts.append(("red",  f"📉 REVENUE DROP — Down {abs(rev_trend):.1f}% vs last hour. Investigate top city performance immediately."))
rc=df[df["weather_condition"].isin(["Rain","Heavy Rain","Thunderstorm"])]["city"].unique()
if len(rc)>0: alerts.append(("amber",f"🌧️ WEATHER IMPACT — Rain in: {', '.join(rc)}. Push digital promotions to offset 30-50% drop."))
hc=df[df["weather_condition"]=="Extreme Heat"]["city"].unique()
if len(hc)>0: alerts.append(("amber",f"🔥 HEAT ALERT — Extreme heat in: {', '.join(hc)}. Boost online-only offers."))
if orders_30==0:   alerts.append(("red",  "⚡ NO ORDERS in last 30 minutes. Check data pipeline immediately."))
elif orders_30<3:  alerts.append(("amber",f"📊 LOW VOLUME — Only {orders_30} orders in last 30 min. Monitor closely."))
alerts.append(("green",f"🏆 TOP PERFORMER — {top_category} leading all categories. {top_product} is best-selling product."))
for cls,msg in alerts: st.markdown(f'<div class="alert-ticker {cls}">{msg}</div>',unsafe_allow_html=True)

st.markdown('<div class="sec-header">📊 REVENUE ANALYTICS</div>',unsafe_allow_html=True)
ch1,ch2=st.columns([2,1])
with ch1:
    dft=df.copy();dft["bucket"]=dft["timestamp"].dt.floor("15min")
    rt=dft.groupby("bucket")["revenue"].sum().reset_index().sort_values("bucket")
    fig_r=go.Figure()
    fig_r.add_trace(go.Scatter(x=rt["bucket"],y=rt["revenue"],fill="tozeroy",line=dict(color="#10b981",width=2.5),fillcolor="rgba(16,185,129,0.07)",name="Revenue",hovertemplate="<b>%{x|%H:%M}</b><br>₹%{y:,.0f}<extra></extra>"))
    if len(rt)>3:
        rt["ma"]=rt["revenue"].rolling(3,min_periods=1).mean()
        fig_r.add_trace(go.Scatter(x=rt["bucket"],y=rt["ma"],line=dict(color="#f59e0b",width=1.5,dash="dot"),name="Trend Line",hovertemplate="Trend: ₹%{y:,.0f}<extra></extra>"))
    fig_r.update_layout(**base_layout("REVENUE OVER TIME (15-MIN BUCKETS)",280));st.plotly_chart(fig_r,use_container_width=True)
with ch2:
    cr=df.groupby("category")["revenue"].sum().reset_index()
    colors=["#10b981","#f59e0b","#38bdf8","#a78bfa","#ef4444","#34d399"]
    fig_c=go.Figure(go.Pie(labels=cr["category"],values=cr["revenue"],hole=0.65,marker=dict(colors=colors[:len(cr)],line=dict(color="#030712",width=2)),textfont=dict(size=10,family="Rajdhani"),hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"))
    lo=base_layout("REVENUE BY CATEGORY",280);lo["showlegend"]=True
    lo["annotations"]=[dict(text=f"<b>{top_category}</b>",x=0.5,y=0.5,font=dict(size=11,color="#10b981",family="Rajdhani"),showarrow=False)]
    fig_c.update_layout(**lo);st.plotly_chart(fig_c,use_container_width=True)

ch3,ch4=st.columns(2)
with ch3:
    cir=df.groupby("city")["revenue"].sum().sort_values(ascending=True).reset_index()
    fig_ci=go.Figure(go.Bar(y=cir["city"],x=cir["revenue"],orientation="h",marker=dict(color=cir["revenue"],colorscale=[[0,"#064e3b"],[0.5,"#10b981"],[1,"#34d399"]],line=dict(width=0)),hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"))
    lo_ci=base_layout("REVENUE BY CITY",260);lo_ci["yaxis"]["showgrid"]=False;fig_ci.update_layout(**lo_ci);st.plotly_chart(fig_ci,use_container_width=True)
with ch4:
    wr=df.groupby("weather_condition")["revenue"].sum().sort_values(ascending=False).reset_index()
    wc2=["#10b981" if WEATHER_IMPACT.get(w,("neutral","",""))[0]=="boost" else "#ef4444" if WEATHER_IMPACT.get(w,("neutral","",""))[0]=="hurt" else "#f59e0b" for w in wr["weather_condition"]]
    fig_w=go.Figure(go.Bar(x=wr["weather_condition"],y=wr["revenue"],marker=dict(color=wc2,line=dict(width=0)),hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"))
    lo_w=base_layout("REVENUE BY WEATHER CONDITION",260);lo_w["xaxis"]["tickangle"]=-30;fig_w.update_layout(**lo_w);st.plotly_chart(fig_w,use_container_width=True)

ch5,ch6=st.columns([1,2])
with ch5:
    st.markdown('<div class="sec-header">🏆 TOP 5 PRODUCTS</div>',unsafe_allow_html=True)
    pr=df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(5).reset_index()
    for _,row in pr.iterrows():
        pct=(row["revenue"]/total_revenue)*100;bw=min(int(pct*3.5),100)
        st.markdown(f'<div style="background:#0d1117;border:1px solid #1f2937;border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.4rem;"><div style="display:flex;justify-content:space-between;align-items:center;"><div style="font-family:Rajdhani,sans-serif;font-size:0.88rem;font-weight:600;color:#e2e8f0;">{row["product"]}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#10b981;">{fmt_inr(row["revenue"])}</div></div><div style="background:#1f2937;border-radius:4px;height:4px;margin-top:0.3rem;"><div style="background:linear-gradient(90deg,#10b981,#34d399);width:{bw}%;height:4px;border-radius:4px;"></div></div><div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:#4b5563;margin-top:2px;">{pct:.1f}% of total</div></div>',unsafe_allow_html=True)
with ch6:
    if len(df)>5:
        dfh=df.copy();dfh["hour"]=dfh["timestamp"].dt.hour
        pivot=dfh.groupby(["city","hour"])["revenue"].sum().reset_index().pivot(index="city",columns="hour",values="revenue").fillna(0)
        fig_h=go.Figure(go.Heatmap(z=pivot.values,x=[f"{h:02d}:00" for h in pivot.columns],y=pivot.index.tolist(),colorscale=[[0,"#030712"],[0.3,"#064e3b"],[0.6,"#10b981"],[1,"#34d399"]],hovertemplate="<b>%{y}</b> at %{x}<br>₹%{z:,.0f}<extra></extra>"))
        lo_h=base_layout("REVENUE HEATMAP · CITY × HOUR OF DAY",300);lo_h["xaxis"]["showgrid"]=False;lo_h["yaxis"]["showgrid"]=False;fig_h.update_layout(**lo_h);st.plotly_chart(fig_h,use_container_width=True)

st.markdown('<div class="sec-header">📡 LIVE ORDER FEED · LAST 10 TRANSACTIONS</div>',unsafe_allow_html=True)
recent=df.head(10)[["timestamp","order_id","product","category","quantity","price","city","weather_condition","revenue"]].copy()
recent["revenue"]=recent["revenue"].apply(lambda x:f"₹{x:,.0f}");recent["price"]=recent["price"].apply(lambda x:f"₹{x:,.0f}")
recent["timestamp"]=recent["timestamp"].dt.strftime("%H:%M:%S");recent.columns=["Time","Order ID","Product","Category","Qty","Price","City","Weather","Revenue"]
st.dataframe(recent,use_container_width=True,hide_index=True)

st.markdown('<div class="sec-header">📋 MANAGER DECISION SUMMARY</div>',unsafe_allow_html=True)
ms1,ms2,ms3=st.columns(3)
with ms1:
    st.markdown(f'<div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-left:3px solid #10b981;border-radius:12px;padding:1rem 1.2rem;"><div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;letter-spacing:2px;color:#4b5563;margin-bottom:0.5rem;">TOP OPPORTUNITY</div><div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#10b981;">Push more {top_category}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#6b7280;margin-top:0.3rem;">Highest revenue category this session</div></div>',unsafe_allow_html=True)
with ms2:
    worst_w=df.groupby("weather_condition")["revenue"].mean().idxmin() if not df.empty else "Rain"
    st.markdown(f'<div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-left:3px solid #f59e0b;border-radius:12px;padding:1rem 1.2rem;"><div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;letter-spacing:2px;color:#4b5563;margin-bottom:0.5rem;">WEATHER RISK</div><div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#f59e0b;">Watch {worst_w} cities</div><div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#6b7280;margin-top:0.3rem;">Lowest avg revenue during {worst_w}</div></div>',unsafe_allow_html=True)
with ms3:
    dfhr=df.copy();dfhr["hour"]=dfhr["timestamp"].dt.hour
    bh=dfhr.groupby("hour")["revenue"].sum().idxmax() if not df.empty else 12
    st.markdown(f'<div style="background:linear-gradient(145deg,#0d1117,#111827);border:1px solid #1f2937;border-left:3px solid #38bdf8;border-radius:12px;padding:1rem 1.2rem;"><div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;letter-spacing:2px;color:#4b5563;margin-bottom:0.5rem;">PEAK HOUR</div><div style="font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#38bdf8;">{bh:02d}:00 — {bh+1:02d}:00</div><div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#6b7280;margin-top:0.3rem;">Highest revenue hour today</div></div>',unsafe_allow_html=True)

st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:#1f2937;text-align:center;margin-top:2rem;padding-top:1rem;border-top:1px solid #111827;letter-spacing:2px;">REVENUE PULSE WAR ROOM · SELF-GENERATING DATA PIPELINE · OPENWEATHERMAP INTEGRATED · AUTO-REFRESH 30s</div>',unsafe_allow_html=True)

time.sleep(30)
st.rerun()