import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests, random, time
from datetime import datetime, timedelta

st.set_page_config(page_title="Revenue Pulse · War Room", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
html,body,[class*="css"],.stApp{background-color:#030712!important;color:#e2e8f0!important;}
*{font-family:'Rajdhani',sans-serif!important;}
header[data-testid="stHeader"]{background:transparent!important;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding:1.5rem 2rem 2rem!important;max-width:1600px;}
.wr-title{font-size:2.2rem;font-weight:700;color:#10b981;letter-spacing:3px;text-transform:uppercase;line-height:1.1;}
.wr-sub{font-family:'Share Tech Mono',monospace!important;font-size:0.65rem;color:#374151;letter-spacing:2px;text-transform:uppercase;margin-top:4px;}
.live-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:20px;padding:4px 14px;font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#10b981;letter-spacing:1px;}
.dot{width:7px;height:7px;background:#10b981;border-radius:50%;display:inline-block;animation:blink 1.5s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.2}}
.kpi{background:#0d1117;border:1px solid #1f2937;border-radius:12px;padding:1.2rem 1.4rem;position:relative;overflow:hidden;min-height:120px;}
.kpi::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;}
.bg::after{background:linear-gradient(90deg,transparent,#10b981,transparent);}
.ba::after{background:linear-gradient(90deg,transparent,#f59e0b,transparent);}
.bb::after{background:linear-gradient(90deg,transparent,#38bdf8,transparent);}
.br::after{background:linear-gradient(90deg,transparent,#ef4444,transparent);}
.bp::after{background:linear-gradient(90deg,transparent,#a78bfa,transparent);}
.kpi-label{font-family:'Share Tech Mono',monospace!important;font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;color:#4b5563;margin-bottom:6px;}
.kpi-val{font-size:1.9rem;font-weight:700;line-height:1;}
.kpi-sub{font-family:'Share Tech Mono',monospace!important;font-size:0.6rem;color:#6b7280;margin-top:6px;}
.kpi-icon{position:absolute;top:12px;right:14px;font-size:1.4rem;opacity:0.1;}
.cg{color:#10b981;}.ca{color:#f59e0b;}.cb{color:#38bdf8;}.cr{color:#ef4444;}.cp{color:#a78bfa;}
.sec{font-family:'Share Tech Mono',monospace!important;font-size:0.58rem;letter-spacing:3px;text-transform:uppercase;color:#10b981;border-left:2px solid #10b981;padding-left:8px;margin:1.5rem 0 0.8rem;}
.alrt{border-radius:8px;padding:0.55rem 1rem;font-family:'Share Tech Mono',monospace!important;font-size:0.7rem;margin-bottom:5px;}
.ag{background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);color:#6ee7b7;}
.aa{background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);color:#fcd34d;}
.ar{background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);color:#fca5a5;}
.cc{background:#0d1117;border:1px solid #1f2937;border-radius:10px;padding:0.9rem;text-align:center;}
.pb{background:#0d1117;border:1px solid #1f2937;border-radius:8px;padding:0.55rem 0.8rem;margin-bottom:5px;}
.mgr{background:#0d1117;border:1px solid #1f2937;border-radius:10px;padding:1rem 1.2rem;}
hr{border-color:#1f2937!important;}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:#030712}::-webkit-scrollbar-thumb{background:#1f2937;border-radius:2px}
</style>""", unsafe_allow_html=True)

PRODUCTS=[("UltraBook Pro","Electronics",45000,85000),("Wireless Earbuds","Electronics",2500,8000),
("Smart Watch","Electronics",12000,35000),("Office Chair","Furniture",8000,25000),
("Standing Desk","Furniture",15000,40000),("Running Shoes","Apparel",3000,9000),
("Winter Jacket","Apparel",2500,7500),("Protein Powder","Health",1500,4500),
("Yoga Mat","Health",800,2500),("Coffee Maker","Appliances",3500,12000),
("Air Purifier","Appliances",8000,20000),("Mechanical Keyboard","Electronics",4000,15000),
("Monitor 4K","Electronics",18000,45000),("Water Bottle","Health",500,1800),("Backpack","Apparel",1500,5000)]
CITIES=[("Hyderabad","South"),("Mumbai","West"),("Delhi","North"),("Bangalore","South"),
("Chennai","South"),("Kolkata","East"),("Pune","West"),("Ahmedabad","West")]
WEATHER=[("Clear",1.25),("Partly Cloudy",1.10),("Cloudy",0.95),("Drizzle",0.80),
("Rain",0.65),("Heavy Rain",0.50),("Thunderstorm",0.40),("Extreme Heat",0.70),("Foggy",0.85),("Windy",0.90)]
WI={"Clear":("#10b981","+18%","🟢"),"Partly Cloudy":("#10b981","+8%","🟢"),"Cloudy":("#f59e0b","±0%","🟡"),
"Drizzle":("#ef4444","-18%","🔴"),"Rain":("#ef4444","-32%","🔴"),"Heavy Rain":("#ef4444","-48%","🔴"),
"Thunderstorm":("#ef4444","-58%","🔴"),"Extreme Heat":("#ef4444","-28%","🔴"),
"Foggy":("#f59e0b","-8%","🟡"),"Windy":("#f59e0b","-6%","🟡")}

if "sales" not in st.session_state:
    st.session_state.sales=[];st.session_state.oid=1001;st.session_state.last_add=0.0

def new_sale(ts=None):
    p,cat,lo,hi=random.choice(PRODUCTS);city,reg=random.choice(CITIES);wx,mult=random.choice(WEATHER)
    qty=random.choices([1,2,3,4,5],weights=[50,25,15,7,3])[0];price=random.randint(lo,hi)
    rev=round(price*qty*(0.85+mult*0.15))
    r={"ts":ts or datetime.now(),"oid":f"ORD-{st.session_state.oid}","product":p,"category":cat,
       "price":price,"qty":qty,"city":city,"region":reg,"weather":wx,"revenue":rev}
    st.session_state.oid+=1;return r

if not st.session_state.sales:
    now=datetime.now()
    for i in range(60):
        st.session_state.sales.append(new_sale(now-timedelta(minutes=random.randint(1,180))))
    st.session_state.sales.sort(key=lambda x:x["ts"])
    st.session_state.last_add=time.time()

now_ts=time.time()
if now_ts-st.session_state.last_add>=30:
    st.session_state.sales.append(new_sale());st.session_state.last_add=now_ts

df=pd.DataFrame(st.session_state.sales).sort_values("ts",ascending=False).reset_index(drop=True)

total_rev=df["revenue"].sum();total_ord=len(df);aov=df["revenue"].mean()
now_dt=datetime.now()
hr1=df[df["ts"]>=now_dt-timedelta(hours=1)]["revenue"].sum()
hr2=df[(df["ts"]>=now_dt-timedelta(hours=2))&(df["ts"]<now_dt-timedelta(hours=1))]["revenue"].sum()
trend=((hr1-hr2)/max(hr2,1))*100
ord30=len(df[df["ts"]>=now_dt-timedelta(minutes=30)])
today_rev=df[df["ts"].dt.date==now_dt.date()]["revenue"].sum()
top_cat=df.groupby("category")["revenue"].sum().idxmax()
top_prod=df.groupby("product")["revenue"].sum().idxmax()
top_city=df.groupby("city")["revenue"].sum().idxmax()

def inr(v):
    if v>=1_00_00_000:return f"₹{v/1_00_00_000:.2f}Cr"
    if v>=1_00_000:return f"₹{v/1_00_000:.2f}L"
    return f"₹{v:,.0f}"

def pb(title="",h=280):
    return dict(title=dict(text=title,font=dict(size=10,color="#10b981",family="Share Tech Mono"),x=0.01),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#6b7280",family="Rajdhani",size=11),
        xaxis=dict(gridcolor="#111827",showgrid=True,zeroline=False,tickfont=dict(size=9,color="#374151")),
        yaxis=dict(gridcolor="#111827",showgrid=True,zeroline=False,tickfont=dict(size=9,color="#374151")),
        margin=dict(l=8,r=8,t=32,b=8),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9),orientation="h",y=1.12),height=h)

# Header
c1,c2,c3=st.columns([4,3,1])
with c1:st.markdown('<div class="wr-title">⚡ Revenue Pulse</div><div class="wr-sub">Live Sales War Room · Data auto-generates every session · Weather Integrated</div>',unsafe_allow_html=True)
with c2:
    next_s=max(0,30-int(now_ts-st.session_state.last_add))
    st.markdown(f'<div style="text-align:right;padding-top:10px;"><div class="live-badge"><span class="dot"></span>&nbsp;LIVE · {total_ord} ORDERS</div><div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:#374151;margin-top:5px;">SYNCED {datetime.now().strftime("%d %b %Y · %H:%M:%S")} · NEXT IN {next_s}s</div></div>',unsafe_allow_html=True)
with c3:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("⟳ Refresh"):st.rerun()
st.markdown("---")

# KPIs
st.markdown('<div class="sec">LIVE METRICS</div>',unsafe_allow_html=True)
k1,k2,k3,k4,k5=st.columns(5)
tr_arrow="▲" if trend>=0 else "▼";tr_cls="cg" if trend>=0 else "cr";tr_bar="bg" if trend>=0 else "br"
for col,icon,label,val,sub,vc,bc in [
    (k1,"💰","Total Revenue",inr(total_rev),f"All time · {total_ord} orders","cg","bg"),
    (k2,"📦","Orders Last 30m",str(ord30),"Live order volume","ca","ba"),
    (k3,"🧾","Avg Order Value",inr(aov),"Per transaction","cb","bb"),
    (k4,"📈","Revenue Trend",f"{tr_arrow} {abs(trend):.1f}%","vs previous hour",tr_cls,tr_bar),
    (k5,"🏆","Today Revenue",inr(today_rev),f"Top: {top_city}","cp","bp")]:
    with col:st.markdown(f'<div class="kpi {bc}"><div class="kpi-icon">{icon}</div><div class="kpi-label">{label}</div><div class="kpi-val {vc}">{val}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)

# Weather
st.markdown('<div class="sec">🌦 WEATHER × SALES IMPACT</div>',unsafe_allow_html=True)
API_KEY=st.secrets.get("OPENWEATHER_API_KEY","")
wc=st.session_state.get("weather_cache",{})
if API_KEY and (now_ts-st.session_state.get("weather_ts",0))>600:
    for city,_ in CITIES[:5]:
        try:
            r=requests.get("https://api.openweathermap.org/data/2.5/weather",params={"q":city+",IN","appid":API_KEY,"units":"metric"},timeout=5)
            if r.status_code==200:
                d=r.json();wc[city]={"desc":d["weather"][0]["description"].title(),"temp":round(d["main"]["temp"],1),"icon":d["weather"][0]["icon"]}
        except:pass
    st.session_state.weather_cache=wc;st.session_state.weather_ts=now_ts
wcols=st.columns(5)
for i,(city,_) in enumerate(CITIES[:5]):
    city_rev=df[df["city"]==city]["revenue"].sum();wd=wc.get(city)
    if wd:
        wk=next((k for k in WI if k.lower() in wd["desc"].lower()),"Cloudy");clr,pct,dot=WI[wk]
        ih=f'<img src="https://openweathermap.org/img/wn/{wd["icon"]}@2x.png" style="width:34px;height:34px;">';det=f'{wd["desc"]} · {wd["temp"]}°C'
    else:
        cdf=df[df["city"]==city];tw=cdf["weather"].mode()[0] if not cdf.empty else "Cloudy"
        clr,pct,dot=WI.get(tw,("#f59e0b","±0%","🟡"));ih="<div style='font-size:1.6rem'>🌡️</div>";det=tw
    with wcols[i]:st.markdown(f'<div class="cc" style="border-top:2px solid {clr};">{ih}<div style="font-size:0.95rem;font-weight:700;color:#e2e8f0;margin-top:4px;">{city}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:#6b7280;">{det}</div><div style="font-size:1rem;font-weight:700;color:{clr};margin-top:4px;">{dot} {pct}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:#4b5563;margin-top:2px;">{inr(city_rev)}</div></div>',unsafe_allow_html=True)

# Alerts
st.markdown('<div class="sec">⚠ SMART ALERTS</div>',unsafe_allow_html=True)
alerts=[]
if trend>20:alerts.append(("ag",f"🚀 SURGE — Revenue up {trend:.1f}% vs last hour."))
elif trend<-20:alerts.append(("ar",f"📉 DROP — Revenue down {abs(trend):.1f}% vs last hour."))
rc=df[df["weather"].isin(["Rain","Heavy Rain","Thunderstorm"])]["city"].unique()
if len(rc):alerts.append(("aa",f"🌧️ RAIN IMPACT — {', '.join(rc)}. Push digital promos."))
hc=df[df["weather"]=="Extreme Heat"]["city"].unique()
if len(hc):alerts.append(("aa",f"🔥 HEAT ALERT — {', '.join(hc)}. Boost online-only offers."))
if ord30==0:alerts.append(("ar","⚡ NO ORDERS in last 30 min. Check pipeline."))
elif ord30<3:alerts.append(("aa",f"📊 LOW VOLUME — {ord30} orders in last 30 min."))
alerts.append(("ag",f"🏆 LEADER — {top_cat} top category · {top_prod} best product."))
for cls,msg in alerts:st.markdown(f'<div class="alrt {cls}">{msg}</div>',unsafe_allow_html=True)

# Charts
st.markdown('<div class="sec">📊 REVENUE ANALYTICS</div>',unsafe_allow_html=True)
r1,r2=st.columns([2,1])
with r1:
    dft=df.copy();dft["bucket"]=dft["ts"].dt.floor("15min")
    rt=dft.groupby("bucket")["revenue"].sum().reset_index().sort_values("bucket")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=rt["bucket"],y=rt["revenue"],fill="tozeroy",line=dict(color="#10b981",width=2),fillcolor="rgba(16,185,129,0.06)",name="Revenue",hovertemplate="<b>%{x|%H:%M}</b><br>%{y:,.0f}<extra></extra>"))
    if len(rt)>3:
        rt["ma"]=rt["revenue"].rolling(3,min_periods=1).mean()
        fig.add_trace(go.Scatter(x=rt["bucket"],y=rt["ma"],line=dict(color="#f59e0b",width=1.5,dash="dot"),name="Trend"))
    fig.update_layout(**pb("REVENUE — 15 MIN BUCKETS",270));st.plotly_chart(fig,use_container_width=True)
with r2:
    cr=df.groupby("category")["revenue"].sum().reset_index()
    colors=["#10b981","#f59e0b","#38bdf8","#a78bfa","#ef4444","#34d399"]
    fig2=go.Figure(go.Pie(labels=cr["category"],values=cr["revenue"],hole=0.6,marker=dict(colors=colors[:len(cr)],line=dict(color="#030712",width=2)),textfont=dict(size=10),hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>"))
    lo2=pb("REVENUE BY CATEGORY",270);lo2["showlegend"]=True;lo2["annotations"]=[dict(text=f"<b>{top_cat}</b>",x=0.5,y=0.5,font=dict(size=10,color="#10b981"),showarrow=False)]
    fig2.update_layout(**lo2);st.plotly_chart(fig2,use_container_width=True)

r3,r4=st.columns(2)
with r3:
    cir=df.groupby("city")["revenue"].sum().sort_values().reset_index()
    fig3=go.Figure(go.Bar(y=cir["city"],x=cir["revenue"],orientation="h",marker=dict(color=cir["revenue"],colorscale=[[0,"#064e3b"],[0.5,"#10b981"],[1,"#34d399"]],line=dict(width=0)),hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>"))
    lo3=pb("REVENUE BY CITY",250);lo3["yaxis"]["showgrid"]=False;fig3.update_layout(**lo3);st.plotly_chart(fig3,use_container_width=True)
with r4:
    wr=df.groupby("weather")["revenue"].sum().sort_values(ascending=False).reset_index()
    wclr=[WI.get(w,("#f59e0b","",""))[0] for w in wr["weather"]]
    fig4=go.Figure(go.Bar(x=wr["weather"],y=wr["revenue"],marker=dict(color=wclr,line=dict(width=0)),hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>"))
    lo4=pb("REVENUE BY WEATHER",250);lo4["xaxis"]["tickangle"]=-30;fig4.update_layout(**lo4);st.plotly_chart(fig4,use_container_width=True)

r5,r6=st.columns([1,2])
with r5:
    st.markdown('<div class="sec">🏆 TOP 5 PRODUCTS</div>',unsafe_allow_html=True)
    pr=df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(5).reset_index()
    for _,row in pr.iterrows():
        pct=(row["revenue"]/total_rev)*100;bw=min(int(pct*3.5),100)
        st.markdown(f'<div class="pb"><div style="display:flex;justify-content:space-between;"><span style="font-size:0.85rem;font-weight:600;color:#e2e8f0">{row["product"]}</span><span style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#10b981">{inr(row["revenue"])}</span></div><div style="background:#1f2937;border-radius:3px;height:3px;margin-top:5px;"><div style="background:linear-gradient(90deg,#10b981,#34d399);width:{bw}%;height:3px;border-radius:3px;"></div></div><div style="font-family:Share Tech Mono,monospace;font-size:0.55rem;color:#4b5563;margin-top:2px;">{pct:.1f}% of total</div></div>',unsafe_allow_html=True)
with r6:
    dfh=df.copy();dfh["hour"]=dfh["ts"].dt.hour
    pivot=dfh.groupby(["city","hour"])["revenue"].sum().reset_index().pivot(index="city",columns="hour",values="revenue").fillna(0)
    fig5=go.Figure(go.Heatmap(z=pivot.values,x=[f"{h:02d}:00" for h in pivot.columns],y=pivot.index.tolist(),colorscale=[[0,"#030712"],[0.3,"#064e3b"],[0.7,"#10b981"],[1,"#34d399"]],hovertemplate="<b>%{y}</b> @ %{x}<br>%{z:,.0f}<extra></extra>"))
    lo5=pb("HEATMAP · CITY × HOUR",290);lo5["xaxis"]["showgrid"]=False;lo5["yaxis"]["showgrid"]=False;fig5.update_layout(**lo5);st.plotly_chart(fig5,use_container_width=True)

# Order feed
st.markdown('<div class="sec">📡 LIVE ORDER FEED · LAST 15 TRANSACTIONS</div>',unsafe_allow_html=True)
feed=df.head(15)[["ts","oid","product","category","qty","price","city","weather","revenue"]].copy()
feed["ts"]=feed["ts"].dt.strftime("%H:%M:%S")
feed["revenue"]=feed["revenue"].apply(lambda x:f"₹{x:,.0f}")
feed["price"]=feed["price"].apply(lambda x:f"₹{x:,.0f}")
feed.columns=["Time","Order ID","Product","Category","Qty","Price","City","Weather","Revenue"]
st.dataframe(feed.reset_index(drop=True),use_container_width=True,hide_index=True)

# Manager board
st.markdown('<div class="sec">📋 MANAGER DECISION BOARD</div>',unsafe_allow_html=True)
m1,m2,m3=st.columns(3)
worst_w=df.groupby("weather")["revenue"].mean().idxmin() if not df.empty else "Rain"
best_hr=dfh.groupby("hour")["revenue"].sum().idxmax() if not df.empty else 12
for col,clr,label,val,sub in [
    (m1,"#10b981","TOP OPPORTUNITY",f"Push more {top_cat}",f"Best category · {top_prod} top product"),
    (m2,"#f59e0b","WEATHER RISK",f"Monitor {worst_w} cities",f"Lowest avg revenue during {worst_w}"),
    (m3,"#38bdf8","PEAK HOUR",f"{best_hr:02d}:00 — {best_hr+1:02d}:00","Highest revenue window today")]:
    with col:st.markdown(f'<div class="mgr" style="border-left:3px solid {clr};"><div style="font-family:Share Tech Mono,monospace;font-size:0.55rem;letter-spacing:2px;color:#4b5563;margin-bottom:5px;">{label}</div><div style="font-size:1rem;font-weight:700;color:{clr};">{val}</div><div style="font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#6b7280;margin-top:4px;">{sub}</div></div>',unsafe_allow_html=True)

st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.55rem;color:#1f2937;text-align:center;margin-top:2rem;padding-top:1rem;border-top:1px solid #111827;letter-spacing:2px;">REVENUE PULSE WAR ROOM · DATA AUTO-GENERATES PER SESSION · OPENWEATHERMAP OPTIONAL</div>',unsafe_allow_html=True)
st.markdown('<meta http-equiv="refresh" content="30">',unsafe_allow_html=True)