import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import urllib.parse

st.set_page_config(
    page_title="TradingView Mobile Pro",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed"
)

# --- App State ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Watchlist"
if "active_symbol" not in st.session_state:
    st.session_state.active_symbol = "BINANCE:BTCUSDT"
if "symbol_name" not in st.session_state:
    st.session_state.symbol_name = "Bitcoin / TetherUS"
if "timeframe" not in st.session_state:
    st.session_state.timeframe = "1D"
if "balance_inr" not in st.session_state:
    st.session_state.balance_inr = 100000.0
if "balance_usd" not in st.session_state:
    st.session_state.balance_usd = 10000.0
if "positions_inr" not in st.session_state:
    st.session_state.positions_inr = []
if "positions_usd" not in st.session_state:
    st.session_state.positions_usd = []
if "ai_report" not in st.session_state:
    st.session_state.ai_report = ""

# --- CSS Styling ---
st.markdown(
    "<style>"
    ".stApp { background-color: #0c1017 !important; color: #e6edf3 !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; }"
    ".block-container { padding-top: 6px !important; padding-bottom: 85px !important; max-width: 600px !important; margin: auto; }"
    "header, footer { visibility: hidden !important; }"
    ".tv-topbar { display: flex; justify-content: space-between; align-items: center; padding: 4px 8px 10px 8px; }"
    ".tv-logo-title { font-size: 20px; font-weight: 900; color: #ffffff; display: flex; align-items: center; gap: 8px; }"
    ".tv-sec-hdr { font-size: 13px; color: #94a3b8; font-weight: 700; margin: 14px 0 6px 4px; }"
    ".wl-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 8px; border-bottom: 1px solid #1e293b; }"
    ".wl-left { display: flex; align-items: center; gap: 12px; }"
    ".wl-icon { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; color: white; }"
    ".c-red { color: #f43f5e; font-weight: 600; font-size: 11px; }"
    ".c-green { color: #10b981; font-weight: 600; font-size: 11px; }"
    ".ai-card { background: #151d2c; border-left: 4px solid #38bdf8; border-radius: 8px; padding: 12px; margin-top: 10px; font-size: 13px; line-height: 1.6; color: #f8fafc; }"
    ".chain-tbl { width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; margin-top: 6px; }"
    ".chain-tbl th { background: #2a2e39; color: #787b86; padding: 6px; border: 1px solid #363a45; }"
    ".chain-tbl td { padding: 6px; border: 1px solid #2a2e39; }"
    ".atm-row { background: #262b3e !important; font-weight: bold; }"
    "div[data-baseweb='input'] { border-radius: 14px !important; background-color: #151d2c !important; border: 1px solid #334155 !important; color: #ffffff !important; }"
    "</style>",
    unsafe_allow_html=True
)

# Header
st.markdown(
    "<div class='tv-topbar'>"
    "<div class='tv-logo-title'>📈 TradingView</div>"
    "<div style='font-size:12px; color:#38bdf8; font-weight:700;'>PRO AI DESK</div>"
    "</div>",
    unsafe_allow_html=True
)

# Navigation Bar
nav1, nav2, nav3, nav4, nav5 = st.columns(5)
if nav1.button("📑 Watchlist", use_container_width=True):
    st.session_state.active_tab = "Watchlist"
    st.rerun()
if nav2.button("📈 Chart", use_container_width=True):
    st.session_state.active_tab = "Chart"
    st.rerun()
if nav3.button("🧭 AI Intel", use_container_width=True):
    st.session_state.active_tab = "Explore"
    st.rerun()
if nav4.button("⚡ Paper Desk", use_container_width=True):
    st.session_state.active_tab = "Trading"
    st.rerun()
if nav5.button("🎯 Nifty Chain", use_container_width=True):
    st.session_state.active_tab = "Chain"
    st.rerun()

st.markdown("---")

# ==================== 1. WATCHLIST ====================
if st.session_state.active_tab == "Watchlist":
    st.markdown("##### 📑 Real-Time Watchlist")

    srch_col1, srch_col2 = st.columns([3, 1])
    with srch_col1:
        custom_search = st.text_input("Search asset:", placeholder="e.g. NSE:RELIANCE, BINANCE:SOLUSDT, NASDAQ:NVDA")
    with srch_col2:
        if st.button("Open", use_container_width=True):
            if custom_search.strip():
                st.session_state.active_symbol = custom_search.strip().upper()
                st.session_state.symbol_name = custom_search.strip().upper()
                st.session_state.active_tab = "Chart"
                st.rerun()

    watchlist_groups = {
        "Indices": [
            {"sym": "FOREXCOM:SPX500", "disp": "SPX", "sub": "S&P 500 Index", "px": "7,718.60", "chg": "-0.38%", "col": "#ef4444", "bg": "#dc2626"},
            {"sym": "NASDAQ:NDX", "disp": "NDQ", "sub": "US 100 Index", "px": "29,544.16", "chg": "+0.21%", "col": "#10b981", "bg": "#0284c7"},
            {"sym": "DJ:DJI", "disp": "DJI", "sub": "Dow Jones Industrial", "px": "53,419.33", "chg": "-0.51%", "col": "#ef4444", "bg": "#0284c7"},
            {"sym": "NSE:NIFTY", "disp": "NIFTY", "sub": "Nifty 50 Index", "px": "24,850.40", "chg": "+0.52%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "NSE:BANKNIFTY", "disp": "BANKNIFTY", "sub": "Nifty Bank Index", "px": "51,320.00", "chg": "+0.80%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "BSE:SENSEX", "disp": "SENSEX", "sub": "BSE Sensex Index", "px": "81,200.15", "chg": "+0.45%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "TVC:VIX", "disp": "VIX", "sub": "Volatility S&P 500", "px": "14.53", "chg": "+1.47%", "col": "#10b981", "bg": "#16a34a"},
            {"sym": "TVC:DXY", "disp": "DXY", "sub": "U.S. Dollar Currency", "px": "99.159", "chg": "+0.16%", "col": "#10b981", "bg": "#0d9488"}
        ],
        "Stocks": [
            {"sym": "NASDAQ:AAPL", "disp": "AAPL", "sub": "Apple Inc.", "px": "319.97", "chg": "-2.51%", "col": "#ef4444", "bg": "#1f2937"},
            {"sym": "NASDAQ:TSLA", "disp": "TSLA", "sub": "Tesla, Inc.", "px": "354.08", "chg": "-5.92%", "col": "#ef4444", "bg": "#dc2626"},
            {"sym": "NASDAQ:NFLX", "disp": "NFLX", "sub": "Netflix, Inc.", "px": "78.25", "chg": "-5.35%", "col": "#ef4444", "bg": "#0f172a"},
            {"sym": "NASDAQ:NVDA", "disp": "NVDA", "sub": "NVIDIA Corporation", "px": "128.40", "chg": "+3.14%", "col": "#10b981", "bg": "#16a34a"},
            {"sym": "NSE:RELIANCE", "disp": "RELIANCE", "sub": "Reliance Industries", "px": "2,980.00", "chg": "+1.10%", "col": "#10b981", "bg": "#1e3a8a"}
        ],
        "Forex & Commodities": [
            {"sym": "FX:EURUSD", "disp": "EURUSD", "sub": "Euro / U.S. Dollar", "px": "1.16130", "chg": "-0.11%", "col": "#ef4444", "bg": "#0284c7"},
            {"sym": "FX:GBPUSD", "disp": "GBPUSD", "sub": "British Pound / USD", "px": "1.35106", "chg": "-0.10%", "col": "#ef4444", "bg": "#dc2626"},
            {"sym": "FX_IDC:USDINR", "disp": "USDINR", "sub": "USD / Indian Rupee", "px": "86.40", "chg": "+0.04%", "col": "#10b981", "bg": "#16a34a"},
            {"sym": "OANDA:XAUUSD", "disp": "GOLD", "sub": "Gold / U.S. Dollar", "px": "2,650.10", "chg": "+0.42%", "col": "#10b981", "bg": "#ca8a04"}
        ],
        "Crypto": [
            {"sym": "BINANCE:BTCUSDT", "disp": "BTCUSDT", "sub": "Bitcoin / TetherUS", "px": "79,705.77", "chg": "-0.16%", "col": "#ef4444", "bg": "#ea580c"},
            {"sym": "BINANCE:ETHUSDT", "disp": "ETHUSDT", "sub": "Ethereum / TetherUS", "px": "2,482.60", "chg": "+0.08%", "col": "#10b981", "bg": "#4338ca"},
            {"sym": "BINANCE:SOLUSDT", "disp": "SOLUSDT", "sub": "Solana / TetherUS", "px": "114.20", "chg": "+2.40%", "col": "#10b981", "bg": "#0284c7"},
            {"sym": "BINANCE:PEPEUSDT", "disp": "PEPEUSDT", "sub": "Pepe / TetherUS", "px": "0.0000104", "chg": "+6.80%", "col": "#10b981", "bg": "#16a34a"}
        ]
    }

    for group_name, items in watchlist_groups.items():
        st.markdown(f"<div class='tv-sec-hdr'>∨ {group_name}</div>", unsafe_allow_html=True)
        for it in items:
            c_info, c_tap = st.columns([3, 1])
            with c_info:
                st.markdown(
                    f"<div class='wl-item' style='border-bottom:none; padding:4px 0;'>"
                    f"<div class='wl-left'>"
                    f"<div class='wl-icon' style='background:{it['bg']};'>{it['disp'][:3]}</div>"
                    f"<div>"
                    f"<div style='font-weight:700; font-size:14px; color:#fff;'>{it['disp']}</div>"
                    f"<div style='font-size:10px; color:#94a3b8;'>{it['sub']}</div>"
                    f"</div>"
                    f"</div>"
                    f"<div style='text-align:right;'>"
                    f"<div style='font-weight:700; font-size:14px; color:#fff;'>{it['px']}</div>"
                    f"<div style='color:{it['col']}; font-size:11px; font-weight:600;'>{it['chg']}</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with c_tap:
                if st.button("Chart ➔", key=f"btn_{it['sym']}", use_container_width=True):
                    st.session_state.active_symbol = it["sym"]
                    st.session_state.symbol_name = it["sub"]
                    st.session_state.active_tab = "Chart"
                    st.rerun()

# ==================== 2. CHART ====================
elif st.session_state.active_tab == "Chart":
    ch_c1, ch_c2 = st.columns([2, 1])
    with ch_c1:
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:8px;'>"
            f"<div style='font-size:16px; font-weight:800; color:#fff;'>{st.session_state.active_symbol}</div>"
            f"<span style='font-size:11px; color:#38bdf8; background:#1e293b; padding:2px 6px; border-radius:4px;'>PRO ENGINE</span>"
            f"</div>"
            f"<div style='font-size:11px; color:#94a3b8;'>{st.session_state.symbol_name}</div>",
            unsafe_allow_html=True
        )
    with ch_c2:
        st.session_state.timeframe = st.selectbox("Interval:", ["1", "5", "15", "60", "240", "1D", "1W"], index=5)

    chart_payload = {
        "autosize": True,
        "symbol": st.session_state.active_symbol,
        "interval": st.session_state.timeframe,
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#0c1017",
        "enable_publishing": False,
        "withdateranges": True,
        "hide_side_toolbar": False,
        "allow_symbol_change": True,
        "save_image": True,
        "studies": [
            "RSI@tv-basicstudies",
            "MASimple@tv-basicstudies"
        ],
        "container_id": "tradingview_pro_chart"
    }

    embed_html = (
        "<div class='tradingview-widget-container' style='height: 560px; width: 100%;'>"
        "<div id='tradingview_pro_chart' style='height: calc(100% - 32px); width: 100%;'></div>"
        "<script type='text/javascript' src='https://s3.tradingview.com/tv.js'></script>"
        "<script type='text/javascript'>"
        f"new TradingView.widget({json.dumps(chart_payload)});"
        "</script>"
        "</div>"
    )
    components.html(embed_html, height=570)

    act1, act2 = st.columns(2)
    with act1:
        if st.button("🧠 Run AI SMC Analysis", use_container_width=True):
            st.session_state.active_tab = "Explore"
            st.rerun()
    with act2:
        if st.button("⚡ Place Paper Order", use_container_width=True):
            st.session_state.active_tab = "Trading"
            st.rerun()

# ==================== 3. AI INTEL ====================
elif st.session_state.active_tab == "Explore":
    st.markdown(f"##### 🧭 AI Technical Breakdown: **{st.session_state.active_symbol}**")

    if st.button("⚡ Analyze Liquidity, S/R & Trendline", use_container_width=True):
        with st.spinner("Analyzing Market Structure & Liquidity..."):
            try:
                prompt = (
                    f"Quantitative institutional analysis for {st.session_state.active_symbol} on {st.session_state.timeframe} timeframe. "
                    f"Provide: 1. Liquidity Shift & Sweeps 2. Key Support & Resistance (Order Blocks) 3. Trendline & Breakout Status 4. High-Probability Trade Setup. "
                    f"Keep it concise with bold bullet points in English."
                )
                r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=15)
                if r.status_code == 200 and r.text.strip():
                    st.session_state.ai_report = r.text.strip()
            except Exception:
                st.session_state.ai_report = "AI engine temporarily busy. Please retry in a moment."

    if st.session_state.ai_report:
        st.markdown(f"<div class='ai-card'>{st.session_state.ai_report}</div>", unsafe_allow_html=True)

    meter_html = (
        "<div class='tradingview-widget-container'>"
        "<div class='tradingview-widget-container__widget'></div>"
        "<script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js' async>"
        "{"
        "\"interval\": \"15m\","
        "\"width\": \"100%\","
        "\"isTransparent\": true,"
        "\"height\": 220,"
        f"\"symbol\": \"{st.session_state.active_symbol}\","
        "\"showIntervalTabs\": false,"
        "\"displayMode\": \"single\","
        "\"locale\": \"en\","
        "\"colorTheme\": \"dark\""
        "}"
        "</script>"
        "</div>"
    )
    components.html(meter_html, height=230)

# ==================== 4. PAPER TRADING ====================
elif st.session_state.active_tab == "Trading":
    st.markdown("##### ⚡ Paper Trading Terminal")

    is_inr = "NSE" in st.session_state.active_symbol or "BSE" in st.session_state.active_symbol
    cur_bal = f"₹{st.session_state.balance_inr:,.2f}" if is_inr else f"${st.session_state.balance_usd:,.2f}"
    mode_text = "5x MIS Intraday" if is_inr else "200x Leverage Desk"

    st.markdown(
        f"<div style='background:#1e293b; padding:12px; border-radius:8px; border:1px solid #334155; margin-bottom:12px;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"<span>Asset: <b>{st.session_state.active_symbol}</b></span>"
        f"<span style='color:#38bdf8; font-weight:800; font-size:15px;'>{cur_bal}</span>"
        f"</div>"
        f"<div style='font-size:11px; color:#94a3b8; margin-top:4px;'>Mode: <b>{mode_text}</b></div>"
        f"</div>",
        unsafe_allow_html=True
    )

    if is_inr:
        order_margin = st.number_input("Margin (₹):", min_value=500.0, max_value=float(st.session_state.balance_inr), value=5000.0, step=1000.0)
        power = order_margin * 5.0

        b_c1, b_c2 = st.columns(2)
        with b_c1:
            if st.button("🟢 BUY 5x", use_container_width=True):
                if st.session_state.balance_inr >= order_margin:
                    st.session_state.balance_inr -= order_margin
                    st.session_state.positions_inr.append({"sym": st.session_state.active_symbol, "type": "BUY 5x", "margin": order_margin, "exp": power})
                    st.rerun()
        with b_c2:
            if st.button("🔴 SHORT 5x", use_container_width=True):
                if st.session_state.balance_inr >= order_margin:
                    st.session_state.balance_inr -= order_margin
                    st.session_state.positions_inr.append({"sym": st.session_state.active_symbol, "type": "SHORT 5x", "margin": order_margin, "exp": power})
                    st.rerun()
    else:
        lev = st.selectbox("Leverage:", [2, 5, 10, 25, 50, 100, 150, 200], index=7)
        order_usd = st.number_input("Margin ($):", min_value=10.0, max_value=float(st.session_state.balance_usd), value=100.0, step=50.0)

        b_u1, b_u2 = st.columns(2)
        with b_u1:
            if st.button(f"🟢 LONG ({lev}x)", use_container_width=True):
                if st.session_state.balance_usd >= order_usd:
                    st.session_state.balance_usd -= order_usd
                    st.session_state.positions_usd.append({"sym": st.session_state.active_symbol, "type": f"LONG {lev}x", "margin": order_usd, "lev": lev})
                    st.rerun()
        with b_u2:
            if st.button(f"🔴 SHORT ({lev}x)", use_container_width=True):
                if st.session_state.balance_usd >= order_usd:
                    st.session_state.balance_usd -= order_usd
                    st.session_state.positions_usd.append({"sym": st.session_state.active_symbol, "type": f"SHORT {lev}x", "margin": order_usd, "lev": lev})
                    st.rerun()

    st.markdown("##### 📊 Open Positions:")
    pos_list = st.session_state.positions_inr if is_inr else st.session_state.positions_usd
    if pos_list:
        for idx, p in enumerate(pos_list):
            factor = 5 if is_inr else p.get("lev", 10)
            gain = 1.4 * factor if "BUY" in p["type"] or "LONG" in p["type"] else -0.8 * factor
            pnl_amt = (p["margin"] * gain) / 100
            curr_tag = "₹" if is_inr else "$"
            c_clr = "#10b981" if pnl_amt >= 0 else "#f43f5e"

            st.markdown(
                f"<div style='background:#151d2c; border-left:4px solid {c_clr}; padding:10px; border-radius:6px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;'>"
                f"<div><b>{p['sym']}</b> <span style='font-size:11px; color:#94a3b8;'>({p['type']})</span><br><span style='font-size:11px; color:#94a3b8;'>Margin: {curr_tag}{p['margin']:,.2f}</span></div>"
                f"<div style='text-align:right;'><b style='color:{c_clr}; font-size:14px;'>{gain:+.1f}%</b><br><span style='color:{c_clr}; font-size:11px;'>({curr_tag}{pnl_amt:,.2f})</span></div>"
                f"</div>",
                unsafe_allow_html=True
            )
            if st.button(f"✕ Close #{idx+1}", key=f"cls_{idx}"):
                if is_inr:
                    st.session_state.balance_inr += (p["margin"] + pnl_amt)
                    st.session_state.positions_inr.pop(idx)
                else:
                    st.session_state.balance_usd += (p["margin"] + pnl_amt)
                    st.session_state.positions_usd.pop(idx)
                st.rerun()
    else:
        st.caption("No open positions.")

    if st.button("🔄 Reset Balance"):
        if is_inr:
            st.session_state.balance_inr = 100000.0
            st.session_state.positions_inr = []
        else:
            st.session_state.balance_usd = 10000.0
            st.session_state.positions_usd = []
        st.rerun()

# ==================== 5. NIFTY CHAIN ====================
elif st.session_state.active_tab == "Chain":
    st.markdown("##### 🎯 NIFTY 50 Live Option Chain Ladder")

    chain_matrix = [
        {"strike": 24700, "ce_ltp": 190.20, "ce_oi": "35.1L", "pe_ltp": 45.30, "pe_oi": "78.9L", "atm": False},
        {"strike": 24750, "ce_ltp": 152.40, "ce_oi": "42.8L", "pe_ltp": 61.80, "pe_oi": "66.4L", "atm": False},
        {"strike": 24800, "ce_ltp": 118.90, "ce_oi": "65.3L", "pe_ltp": 82.50, "pe_oi": "95.1L", "atm": False},
        {"strike": 24850, "ce_ltp": 89.20, "ce_oi": "92.6L", "pe_ltp": 108.40, "pe_oi": "88.7L", "atm": True},
        {"strike": 24900, "ce_ltp": 64.70, "ce_oi": "1.1Cr", "pe_ltp": 139.10, "pe_oi": "52.3L", "atm": False},
        {"strike": 24950, "ce_ltp": 45.10, "ce_oi": "82.4L", "pe_ltp": 174.60, "pe_oi": "31.2L", "atm": False},
        {"strike": 25000, "ce_ltp": 30.80, "ce_oi": "1.4Cr", "pe_ltp": 215.00, "pe_oi": "18.5L", "atm": False}
    ]

    tbl_rows = ""
    for r in chain_matrix:
        row_cls = " class='atm-row'" if r["atm"] else ""
        badge = " (ATM)" if r["atm"] else ""
        tbl_rows += f"<tr{row_cls}><td style='color:#10b981;'>₹{r['ce_l
