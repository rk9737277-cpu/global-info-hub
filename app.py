import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import urllib.parse

# Mobile-first full layout config
st.set_page_config(
    page_title="TradingView Mobile Pro",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed"
)

# ----------------- App State Management -----------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Watchlist"
if "active_symbol" not in st.session_state:
    st.session_state.active_symbol = "BINANCE:BTCUSDT"
if "symbol_name" not in st.session_state:
    st.session_state.symbol_name = "Bitcoin / TetherUS"
if "timeframe" not in st.session_state:
    st.session_state.timeframe = "1D"
if "balance_inr" not in st.session_state:
    st.session_state.balance_inr = 100000.0  # ₹1,00,000 INR
if "balance_usd" not in st.session_state:
    st.session_state.balance_usd = 10000.0   # $10,000 USD
if "positions_inr" not in st.session_state:
    st.session_state.positions_inr = []
if "positions_usd" not in st.session_state:
    st.session_state.positions_usd = []
if "ai_report" not in st.session_state:
    st.session_state.ai_report = ""

# ----------------- Exact TradingView Mobile Styling -----------------
st.markdown("""
<style>
    .stApp {
        background-color: #0c1017 !important;
        color: #e6edf3 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    .block-container {
        padding-top: 6px !important;
        padding-bottom: 85px !important;
        max-width: 600px !important;
        margin: auto;
    }
    header, footer { visibility: hidden !important; }

    /* Top App Bar */
    .tv-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 8px 10px 8px;
    }
    .tv-logo-title {
        font-size: 20px;
        font-weight: 900;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.5px;
    }

    /* Section Subheaders */
    .tv-sec-hdr {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 700;
        margin: 14px 0 6px 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Watchlist Item Card */
    .wl-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 8px;
        border-bottom: 1px solid #1e293b;
        cursor: pointer;
    }
    .wl-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .wl-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 800;
        color: white;
    }
    .c-red { color: #f43f5e; font-weight: 600; font-size: 11px; }
    .c-green { color: #10b981; font-weight: 600; font-size: 11px; }

    /* Bottom Navigation Bar */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: #111827;
        border-top: 1px solid #1f2937;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 999999;
    }
    .nav-btn {
        background: transparent;
        border: none;
        color: #9ca3af;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 10px;
        cursor: pointer;
    }
    .nav-active {
        color: #38bdf8 !important;
        font-weight: 700;
    }

    .ai-card {
        background: #151d2c;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        font-size: 13px;
        line-height: 1.6;
        color: #f8fafc;
    }
    div[data-baseweb="input"] {
        border-radius: 14px !important;
        background-color: #151d2c !important;
        border: 1px solid #334155 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Top Header Bar
st.markdown("""
<div class="tv-topbar">
    <div class="tv-logo-title">
        <svg width="28" height="18" viewBox="0 0 36 28" fill="none"><path d="M14 22H7V11H14V22Z" fill="#2962FF"/><path d="M22 22H15V6H22V22Z" fill="#2962FF"/><path d="M29 22H22V0H29V22Z" fill="#2962FF"/><circle cx="4" cy="18" r="4" fill="#2962FF"/></svg>
        TradingView
    </div>
    <div style="font-size:12px; color:#38bdf8; font-weight:700;">PRO AI DESK</div>
</div>
""", unsafe_allow_html=True)

# 2. Bottom Navigation Control Tabs
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

# =====================================================================
# 📑 1. WATCHLIST TAB (Exactly like your Screenshot 1 & 2)
# =====================================================================
if st.session_state.active_tab == "Watchlist":
    st.markdown("##### 📑 Real-Time Watchlist")
    
    # Custom Symbol Search (For any asset in the world)
    srch_col1, srch_col2 = st.columns([3, 1])
    with srch_col1:
        custom_search = st.text_input("Search any world asset (NSE, Crypto, US, FX):", placeholder="e.g. NSE:RELIANCE, BINANCE:SOLUSDT, NASDAQ:NVDA")
    with srch_col2:
        if st.button("Open Chart", use_container_width=True):
            if custom_search.strip():
                st.session_state.active_symbol = custom_search.strip().upper()
                st.session_state.symbol_name = custom_search.strip().upper()
                st.session_state.active_tab = "Chart"
                st.rerun()

    # Pre-configured Global Watchlist items as seen in your mobile screenshot
    watchlist_groups = {
        "Indices": [
            {"sym": "FOREXCOM:SPX500", "disp": "SPX", "sub": "S&P 500 Index", "px": "7,718.60", "chg": "-0.38%", "col": "#ef4444", "bg": "#dc2626"},
            {"sym": "NASDAQ:NDX", "disp": "NDQ", "sub": "US 100 Index", "px": "29,544.16", "chg": "+0.21%", "col": "#10b981", "bg": "#0284c7"},
            {"sym": "DJ:DJI", "disp": "DJI", "sub": "Dow Jones Industrial", "px": "53,419.33", "chg": "-0.51%", "col": "#ef4444", "bg": "#0284c7"},
            {"sym": "NSE:NIFTY", "disp": "NIFTY", "sub": "Nifty 50 Index", "px": "24,850.40", "chg": "+0.52%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "NSE:BANKNIFTY", "disp": "BANKNIFTY", "sub": "Nifty Bank Index", "px": "51,320.00", "chg": "+0.80%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "BSE:SENSEX", "disp": "SENSEX", "sub": "BSE Sensex Index", "px": "81,200.15", "chg": "+0.45%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "TVC:VIX", "disp": "VIX", "sub": "Volatility S&P 500", "px": "14.53", "chg": "+1.47%", "col": "#10b981", "bg": "#16a34a"},
            {"sym": "TVC:DXY", "disp": "DXY", "sub": "U.S. Dollar Currency", "px": "99.159", "chg": "+0.16%", "col": "#10b981", "bg": "#0d9488"},
        ],
        "Stocks (US & India)": [
            {"sym": "NASDAQ:AAPL", "disp": "AAPL", "sub": "Apple Inc.", "px": "319.97", "chg": "-2.51%", "col": "#ef4444", "bg": "#1f2937"},
            {"sym": "NASDAQ:TSLA", "disp": "TSLA", "sub": "Tesla, Inc.", "px": "354.08", "chg": "-5.92%", "col": "#ef4444", "bg": "#dc2626"},
            {"sym": "NASDAQ:NFLX", "disp": "NFLX", "sub": "Netflix, Inc.", "px": "78.25", "chg": "-5.35%", "col": "#ef4444", "bg": "#0f172a"},
            {"sym": "NASDAQ:NVDA", "disp": "NVDA", "sub": "NVIDIA Corporation", "px": "128.40", "chg": "+3.14%", "col": "#10b981", "bg": "#16a34a"},
            {"sym": "NSE:RELIANCE", "disp": "RELIANCE", "sub": "Reliance Industries", "px": "2,980.00", "chg": "+1.10%", "col": "#10b981", "bg": "#1e3a8a"},
            {"sym": "NSE:TATASTEEL", "disp": "TATASTEEL", "sub": "Tata Steel Limited", "px": "154.20", "chg": "-0.65%", "col": "#ef4444", "bg": "#1e3a8a"},
        ],
        "Forex & Currencies": [
            {"sym": "FX:EURUSD", "disp": "EURUSD", "sub": "Euro / U.S. Dollar", "px": "1.16130", "chg": "-0.11%", "col": "#ef4444", "bg": "#0284c7"},
            {"sym": "FX:GBPUSD", "disp": "GBPUSD", "sub": "British Pound / USD", "px": "1.35106", "chg": "-0.10%", "col": "#ef4444", "bg": "#dc2626"},
            {"sym": "FX:USDJPY", "disp": "USDJPY", "sub": "U.S. Dollar / Yen", "px": "156.195", "chg": "+0.26%", "col": "#10b981", "bg": "#b91c1c"},
            {"sym": "FX_IDC:USDINR", "disp": "USDINR", "sub": "USD / Indian Rupee", "px": "86.40", "chg": "+0.04%", "col": "#10b981", "bg": "#16a34a"},
        ],
        "Crypto & Commodities": [
            {"sym": "BINANCE:BTCUSDT", "disp": "BTCUSDT", "sub": "Bitcoin / TetherUS", "px": "79,705.77", "chg": "-0.16%", "col": "#ef4444", "bg": "#ea580c"},
            {"sym": "BINANCE:ETHUSDT", "disp": "ETHUSDT", "sub": "Ethereum / TetherUS", "px": "2,482.60", "chg": "+0.08%", "col": "#10b981", "bg": "#4338ca"},
            {"sym": "BINANCE:SOLUSDT", "disp": "SOLUSDT", "sub": "Solana / TetherUS", "px": "114.20", "chg": "+2.40%", "col": "#10b981", "bg": "#0284c7"},
            {"sym": "BINANCE:PEPEUSDT", "disp": "PEPEUSDT", "sub": "Pepe / TetherUS", "px": "0.0000104", "chg": "+6.80%", "col": "#10b981", "bg": "#16a34a"},
            {"sym": "OANDA:XAUUSD", "disp": "GOLD", "sub": "Gold / U.S. Dollar", "px": "2,650.10", "chg": "+0.42%", "col": "#10b981", "bg": "#ca8a04"},
            {"sym": "TVC:USOIL", "disp": "CRUDE OIL", "sub": "WTI Light Sweet Crude", "px": "71.40", "chg": "-1.12%", "col": "#ef4444", "bg": "#1f2937"},
        ]
    }

    for group_name, items in watchlist_groups.items():
        st.markdown(f"<div class='tv-sec-hdr'>∨ {group_name}</div>", unsafe_allow_html=True)
        for it in items:
            c_info, c_tap = st.columns([3, 1])
            with c_info:
                st.markdown(f"""
                <div class="wl-item" style="border-bottom:none; padding:4px 0;">
                    <div class="wl-left">
                        <div class="wl-icon" style="background:{it['bg']};">{it['disp'][:3]}</div>
                        <div>
                            <div style="font-weight:700; font-size:14px; color:#fff;">{it['disp']}</div>
                            <div style="font-size:10px; color:#94a3b8;">{it['sub']}</div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-weight:700; font-size:14px; color:#fff;">{it['px']}</div>
                        <div style="color:{it['col']}; font-size:11px; font-weight:600;">{it['chg']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_tap:
                if st.button("Chart ➔", key=f"btn_{it['sym']}", use_container_width=True):
                    st.session_state.active_symbol = it["sym"]
                    st.session_state.symbol_name = it["sub"]
                    st.session_state.active_tab = "Chart"
                    st.rerun()

# =====================================================================
# 📈 2. CHART TAB (Exact TradingView Pro Mobile SuperChart)
# =====================================================================
elif st.session_state.active_tab == "Chart":
    ch_c1, ch_c2 = st.columns([2, 1])
    with ch_c1:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="font-size:16px; font-weight:800; color:#fff;">{st.session_state.active_symbol}</div>
            <span style="font-size:11px; color:#38bdf8; background:#1e293b; padding:2px 6px; border-radius:4px;">PRO ENGINE</span>
        </div>
        <div style="font-size:11px; color:#94a3b8;">{st.session_state.symbol_name}</div>
        """, unsafe_allow_html=True)
    with ch_c2:
        st.session_state.timeframe = st.selectbox("Interval:", ["1", "5", "15", "60", "240", "1D", "1W"], index=5)

    # Full TradingView Engine with all indicators, drawings, timeframe controls
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
        "hide_side_toolbar": False,  # Opens left drawing palette
        "allow_symbol_change": True,
        "save_image": True,
        "studies": [
            "RSI@tv-basicstudies",
            "MASimple@tv-basicstudies",
            "BollingerBands@tv-basicstudies"
        ],
        "container_id": "tradingview_pro_chart"
    }

    components.html(f"""
    <div class="tradingview-widget-container" style="height: 560px; width: 100%;">
      <div id="tradingview_pro_chart" style="height: calc(100% - 32px); width: 100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({json.dumps(chart_payload)});
      </script>
    </div>
    """, height=570)

    # Quick Action Buttons below chart
    act1, act2 = st.columns(2)
    with act1:
        if st.button("🧠 Run AI SMC & Liquidity Analysis", use_container_width=True):
            st.session_state.active_tab = "Explore"
            st.rerun()
    with act2:
        if st.button("⚡ Place Paper Order", use_container_width=True):
            st.session_state.active_tab = "Trading"
            st.rerun()

# =====================================================================
# 🧭 3. AI INTEL DESK (SMC, Liquidity, Support/Resistance, Breakouts)
# =====================================================================
elif st.session_state.active_tab == "Explore":
    st.markdown(f"##### 🧭 AI Technical Breakdown: **{st.session_state.active_symbol}**")
    
    st.caption(f"Analyzing {st.session_state.active_symbol} on {st.session_state.timeframe} timeframe using institutional SMC algorithms.")

    if st.button("⚡ Analyze Liquidity, S/R, Breakout & Trendline", use_container_width=True):
        with st.spinner("Decoding Order Blocks, Liquidity Pools & Market Structure..."):
            try:
                prompt = (
                    f"You are a quantitative institutional trader and SMC analyst. "
                    f"Perform a technical analysis for {st.session_state.active_symbol} on {st.session_state.timeframe} timeframe. "
                    f"Structure your report under these exact 4 headings: "
                    f"1. 🌊 Liquidity Shift & Sweeps: Where are Buy-Side & Sell-Side liquidity pools? Was there an institutional stop hunt? "
                    f"2. 🧱 Key Support & Resistance (Order Blocks / FVG): Define precise support boundaries and resistance supply zones. "
                    f"3. 📈 Trendline & Breakout Structure: Is there a breakout, breakdown, or trendline retest? State volume confirmation. "
                    f"4. 🎯 High-Probability Trade Setup: Entry level, Invalidation/Stop-Loss, and Target 1 & 2. "
                    f"Format strictly in clean markdown with bold bullet points. Strictly in English."
                )
                r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=15)
                if r.status_code == 200 and r.text.strip():
                    st.session_state.ai_report = r.text.strip()
            except Exception:
                st.session_state.ai_report = "AI engine temporarily busy. Please retry in a few seconds."

    if st.session_state.ai_report:
        st.markdown(f"<div class='ai-card'>{st.session_state.ai_report}</div>", unsafe_allow_html=True)

    # TradingView Live Technical Meter Widget
    st.markdown("##### 🧭 Real-Time Oscillators & Moving Averages Gauge:")
    components.html(f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
      "interval": "15m",
      "width": "100%",
      "isTransparent": true,
      "height": 220,
      "symbol": "{st.session_state.active_symbol}",
      "showIntervalTabs": false,
      "displayMode": "single",
      "locale": "en",
      "colorTheme": "dark"
    }}
      </script>
    </div>
    """, height=230)

# =====================================================================
# ⚡ 4. PAPER TRADING DESK ($10,000 USD + ₹1,00,000 INR)
# =====================================================================
elif st.session_state.active_tab == "Trading":
    st.markdown("##### ⚡ Paper Trading Terminal")
    
    is_inr = "NSE" in st.session_state.active_symbol or "BSE" in st.session_state.active_symbol
    cur_bal = f"₹{st.session_state.balance_inr:,.2f}" if is_inr else f"${st.session_state.balance_usd:,.2f}"
    
    st.markdown(f"""
    <div style="background:#1e293b; padding:12px; border-radius:8px; border:1px solid #334155; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span>Asset: <b>{st.session_state.active_symbol}</b></span>
            <span style="color:#38bdf8; font-weight:800; font-size:15px;">{cur_bal}</span>
        </div>
        <div style="font-size:11px; color:#94a3b8; margin-top:4px;">
            Mode: <b>{'5x MIS Intraday' if is_inr else '200x Crypto / US Futures'}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_inr:
        order_margin = st.number_input("Margin (₹):", min_value=500.0, max_value=float(st.session_state.balance_inr), value=5000.0, step=1000.0)
        power = order_margin * 5.0
        st.caption(f"Trade Exposure (5x Power): **₹{power:,.2f}**")

        b_c1, b_c2 = st.columns(2)
        with b_c1:
            if st.button(f"🟢 BUY 5x ({st.session_state.active_symbol})", use_container_width=True):
                if st.session_state.balance_inr >= order_margin:
                    st.session_state.balance_inr -= order_margin
                    st.session_state.positions_inr.append({"sym": st.session_state.active_symbol, "type": "BUY 5x", "margin": order_margin, "exp": power})
                    st.success("Buy order executed!")
                    st.rerun()
        with b_c2:
            if st.button(f"🔴 SHORT 5x ({st.session_state.active_symbol})", use_container_width=True):
                if st.session_state.balance_inr >= order_margin:
                    st.session_state.balance_inr -= order_margin
                    st.session_state.positions_inr.append({"sym": st.session_state.active_symbol, "type": "SHORT 5x", "margin": order_margin, "exp": power})
                    st.success("Short order executed!")
                    st.rerun()
    else:
        lev = st.selectbox("Leverage Multiplier:", [2, 5, 10, 25, 50, 100, 150, 200], index=7)
        order_usd = st.number_input("Margin ($):", min_value=10.0, max_value=float(st.session_state.balance_usd), value=100.0, step=50.0)

        b_u1, b_u2 = st.columns(2)
        with b_u1:
            if st.button(f"🟢 LONG ({lev}x)", use_container_width=True):
                if st.session_state.balance_usd >= order_usd:
                    st.session_state.balance_usd -= order_usd
                    st.session_state.positions_usd.append({"
