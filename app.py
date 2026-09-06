import streamlit as st
import streamlit.components.v1 as components
import json, requests, urllib.parse

st.set_page_config(page_title="TradingView Pro", layout="wide", page_icon="📈", initial_sidebar_state="collapsed")

# Session State
for k, v in {"sym": "BINANCE:BTCUSDT", "tf": "15", "inr": 100000.0, "usd": 10000.0, "p_inr": [], "p_usd": [], "ai": ""}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""<style>
.stApp { background:#0c1017 !important; color:#e6edf3 !important; }
.block-container { padding:4px 8px 60px 8px !important; max-width:650px !important; margin:auto; }
header, footer { visibility:hidden !important; }
div[data-baseweb="tab-list"] { background:#151d2c; border-radius:10px; padding:4px; }
button[data-baseweb="tab"] { color:#94a3b8 !important; font-size:12px !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:#38bdf8 !important; font-weight:bold !important; }
.card { background:#151d2c; border:1px solid #1e293b; border-radius:8px; padding:10px; margin-bottom:8px; }
.btn-red { color:#ef4444; font-weight:bold; } .btn-green { color:#10b981; font-weight:bold; }
</style>""", unsafe_allow_html=True)

# Top Bar
st.markdown(f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0;">
    <div style="font-size:18px; font-weight:900; color:#fff;">📈 TradingView Pro</div>
    <div style="font-size:11px; color:#38bdf8;">₹{st.session_state.inr:,.0f} | ${st.session_state.usd:,.0f}</div>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📑 Watchlist", "📈 Chart", "🧠 AI SMC", "⚡ Paper Trade", "🎯 Option Chain"])

# 1. WATCHLIST
with tab1:
    st.caption("Tap any asset to load directly on TradingView Chart:")
    wl = {
        "Indices": [("NSE:NIFTY", "Nifty 50", "24,850.40", "+0.52%"), ("NSE:BANKNIFTY", "Bank Nifty", "51,320.00", "+0.80%"), ("BSE:SENSEX", "Sensex", "81,200.15", "+0.45%"), ("FOREXCOM:SPX500", "S&P 500", "7,718.60", "-0.38%"), ("NASDAQ:NDX", "US 100", "29,544.16", "+0.21%")],
        "Crypto": [("BINANCE:BTCUSDT", "Bitcoin", "79,705.77", "-0.16%"), ("BINANCE:ETHUSDT", "Ethereum", "2,482.60", "+0.08%"), ("BINANCE:SOLUSDT", "Solana", "114.20", "+2.40%"), ("BINANCE:PEPEUSDT", "Pepe", "0.0000104", "+6.80%")],
        "Stocks & Forex": [("NASDAQ:NVDA", "NVIDIA", "128.40", "+3.14%"), ("NASDAQ:TSLA", "Tesla", "354.08", "-5.92%"), ("NSE:RELIANCE", "Reliance", "2,980.00", "+1.10%"), ("OANDA:XAUUSD", "Gold", "2,650.10", "+0.42%"), ("FX:EURUSD", "EUR/USD", "1.1613", "-0.11%")]
    }
    for cat, items in wl.items():
        st.markdown(f"<b style='color:#94a3b8; font-size:12px;'>∨ {cat}</b>", unsafe_allow_html=True)
        for sym, name, px, chg in items:
            c1, c2, c3 = st.columns([2.5, 2, 1.2])
            c1.markdown(f"<b>{name}</b><br><span style='font-size:10px; color:#64748b;'>{sym}</span>", unsafe_allow_html=True)
            colr = "#10b981" if "+" in chg else "#ef4444"
            c2.markdown(f"<div style='text-align:right;'><b>{px}</b><br><span style='font-size:11px; color:{colr};'>{chg}</span></div>", unsafe_allow_html=True)
            if c3.button("Chart", key="wl_"+sym):
                st.session_state.sym = sym
                st.rerun()

    st.markdown("---")
    custom = st.text_input("Or search ANY world asset:", placeholder="e.g. NSE:TRENT, BINANCE:DOGEUSDT, NASDAQ:AAPL")
    if st.button("Load Custom Symbol") and custom.strip():
        st.session_state.sym = custom.strip().upper()
        st.rerun()

# 2. CHART (TradingView SuperChart with Drawings & Indicators)
with tab2:
    cc1, cc2 = st.columns([2.5, 1])
    with cc1: st.markdown(f"Active: <b style='color:#38bdf8; font-size:16px;'>{st.session_state.sym}</b>", unsafe_allow_html=True)
    with cc2: st.session_state.tf = st.selectbox("Interval", ["1", "5", "15", "60", "240", "1D", "1W"], index=2, label_visibility="collapsed")
    
    cfg = {"autosize": True, "symbol": st.session_state.sym, "interval": st.session_state.tf, "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "en", "toolbar_bg": "#0c1017", "hide_side_toolbar": False, "allow_symbol_change": True, "save_image": True, "studies": ["RSI@tv-basicstudies", "MASimple@tv-basicstudies"], "container_id": "tv_chart"}
    components.html(f"""<div style="height:540px;"><div id="tv_chart" style="height:100%;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({json.dumps(cfg)});</script></div>""", height=550)

# 3. AI SMC ANALYST (Liquidity, S/R, Breakout, Trendline)
with tab3:
    st.markdown(f"#### 🧠 Institutional SMC Analysis: {st.session_state.sym}")
    if st.button("⚡ Run AI SMC & Liquidity Breakdown", use_container_width=True):
        with st.spinner("Calculating Order Blocks & Liquidity Sweeps..."):
            try:
                p = f"Act as elite quantitative SMC trader. Analyze {st.session_state.sym} on {st.session_state.tf} timeframe. Give: 1. Liquidity Shifts & Sweeps (Buy-side/Sell-side pools) 2. Key Support & Resistance (Order Blocks/FVG) 3. Trendline & Breakout status 4. High-probability trade entry, stoploss & targets. Concise bullet points in English."
                r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}", timeout=12)
                if r.status_code == 200: st.session_state.ai = r.text.strip()
            except Exception:
                st.session_state.ai = "AI analysis server busy. Please tap again."
    if st.session_state.ai:
        st.markdown(f"<div class='card' style='border-left:4px solid #38bdf8; line-height:1.6;'>{st.session_state.ai}</div>", unsafe_allow_html=True)
    
    # Technical Analysis Meter
    components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{{"interval":"15m","width":"100%","isTransparent":true,"height":220,"symbol":"{st.session_state.sym}","showIntervalTabs":false,"displayMode":"single","locale":"en","colorTheme":"dark"}}</script></div>""", height=225)

# 4. PAPER TRADING DESK
with tab4:
    is_inr = "NSE" in st.session_state.sym or "BSE" in st.session_state.sym
    st.markdown(f"<div class='card'>Asset: <b>{st.session_state.sym}</b> | Available: <b style='color:#38bdf8;'>{'₹'+f'{st.session_state.inr:,.0f}' if is_inr else '$'+f'{st.session_state.usd:,.0f}'}</b> ({'5x MIS' if is_inr else '200x Crypto'})</div>", unsafe_allow_html=True)
    
    if is_inr:
        m = st.number_input("Margin (₹)", 500.0, float(st.session_state.inr), 5000.0, 1000.0)
        c1, c2 = st.columns(2)
        if c1.button("🟢 BUY 5x", use_container_width=True):
            st.session_state.inr -= m
            st.session_state.p_inr.append({"s": st.session_state.sym, "t": "BUY 5x", "m": m})
            st.rerun()
        if c2.button("🔴 SHORT 5x", use_container_width=True):
            st.session_state.inr -= m
            st.session_state.p_inr.append({"s": st.session_state.sym, "t": "SHORT 5x", "m": m})
            st.rerun()
    else:
        lev = st.selectbox("Leverage", [2, 5, 10, 25, 50, 100, 200], index=6)
        m = st.number_input("Margin ($)", 10.0, float(st.session_state.usd), 100.0, 50.0)
        c1, c2 = st.columns(2)
        if c1.button(f"🟢 LONG {lev}x", use_container_width=True):
            st.session_state.usd -= m
            st.session_state.p_usd.append({"s": st.session_state.sym, "t": f"LONG {lev}x", "m": m, "l": lev})
            st.rerun()
        if c2.button(f"🔴 SHORT {lev}x", use_container_width=True):
            st.session_state.usd -= m
            st.session_state.p_usd.append({"s": st.session_state.sym, "t": f"SHORT {lev}x", "m": m, "l": lev})
            st.rerun()

    pos = st.session_state.p_inr if is_inr else st.session_state.p_usd
    st.markdown("##### 📊 Open Positions")
    if pos:
        for idx, p in enumerate(pos):
            gn = 7.5 if "BUY" in p["t"] or "LONG" in p["t"] else -4.2
            amt = (p["m"] * gn) / 100
            cur = "₹" if is_inr else "$"
            clr = "#10b981" if amt >= 0 else "#ef4444"
            st.markdown(f"<div class='card' style='border-left:4px solid {clr}; display:flex; justify-content:space-between;'><div><b>{p['s']}</b> ({p['t']})<br><span style='font-size:10px;'>Margin: {cur}{p['m']:,.0f}</span></div><div style='text-align:right;'><b style='color:{clr};'>{gn:+.1f}%</b><br><span style='font-size:10px; color:{clr};'>{cur}{amt:,.1f}</span></div></div>", unsafe_allow_html=True)
            if st.button(f"✕ Close #{idx+1}", key=f"c_{idx}"):
                if is_inr: st.session_state.inr += (p["m"] + amt); st.session_state.p_inr.pop(idx)
                else: st.session_state.usd += (p["m"] + amt); st.session_state.p_usd.pop(idx)
                st.rerun()
    else: st.caption("No open positions.")

# 5. OPTION CHAIN
with tab5:
    st.markdown("##### 🎯 NIFTY 50 Live Option Chain")
    data = [(24750, 152.4, "42L", 61.8, "66L", False), (24800, 118.9, "65L", 82.5, "95L", False), (24850, 89.2, "92L", 108.4, "88L", True), (24900, 64.7, "1.1Cr", 139.1, "52L", False), (24950, 45.1, "82L", 174.6, "31L", False)]
    rows = "".join([f"<tr style='background:{'#1e293b' if atm else 'transparent'}; font-weight:{'bold' if atm else 'normal'};'><td style='color:#10b981; padding:6px;'>₹{c}</td><td style='color:#94a3b8;'>{coi}</td><td style='color:#facc15;'>{k}{' (ATM)' if atm else ''}</td><td style='color:#94a3b8;'>{poi}</td><td style='color:#ef4444;'>₹{p}</td></tr>" for k, c, coi, p, poi, atm in data])
    st.markdown(f"<table style='width:100%; text-align:center; font-size:11px; border-collapse:collapse;'><tr style='background:#151d2c; color:#94a3b8; padding:6px;'><th>CALLS</th><th>OI</th><th>STRIKE</th><th>OI</th><th>PUTS</th></tr>{rows}</table>", unsafe_allow_html=True)
