cat << 'EOF' > requirements.txt
streamlit
requests
EOF

cat << 'EOF' > app.py
import streamlit as st
import streamlit.components.v1 as components
import json, requests, urllib.parse
from datetime import datetime

st.set_page_config(
    page_title="TradingView Pro Terminal",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# 1. State Management Setup ($100,000 USD Capital)
defaults = {
    "sym": "OANDA:XAUUSD",
    "tf": "15",
    "usd": 100000.0,
    "pos": [],
    "orders": [],
    "journal": [],
    "ai_cache": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 2. 100% Mobile Edge-to-Edge TradingView Theme
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #0c1017 !important;
        color: #d1d4dc !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow-x: hidden !important;
        width: 100vw !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif !important;
    }
    .block-container {
        padding: 0px 2px 45px 2px !important;
        max-width: 100vw !important;
        margin: 0 !important;
    }
    header, footer, [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    div[data-baseweb="tab-list"] {
        background: #161b22;
        border-radius: 0px;
        padding: 2px 0px;
        border-bottom: 1px solid #2a2e39;
        width: 100%;
        display: flex;
        position: sticky;
        top: 0;
        z-index: 9999;
    }
    button[data-baseweb="tab"] {
        color: #787b86 !important;
        font-size: 10.5px !important;
        font-weight: 700 !important;
        padding: 8px 1px !important;
        flex: 1;
        text-align: center;
        border-radius: 0px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2962ff !important;
        border-bottom: 2px solid #2962ff !important;
        background: rgba(41, 98, 255, 0.08) !important;
    }
    .card {
        background: #161b26;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        padding: 10px;
        margin: 6px 4px;
    }
    .c-green { color: #089981 !important; }
    .c-red { color: #f23645 !important; }
    .stat-badge {
        background: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 4px;
        padding: 6px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 3. Top Floating Status Header
total_pl = sum([p.get("running_pnl", 0.0) for p in st.session_state.pos])
pl_color = "c-green" if total_pl >= 0 else "c-red"

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:8px 10px; background:#131722; border-bottom:1px solid #2a2e39;">
    <div>
        <span style="font-size:15px; font-weight:900; color:#2962ff; letter-spacing:0.5px;">PRO TERMINAL</span>
        <span style="font-size:10px; background:#1e222d; color:#787b86; padding:2px 5px; border-radius:3px; margin-left:4px;">100k DESK</span>
    </div>
    <div style="text-align:right; font-size:11px;">
        <span style="color:#787b86;">Equity: </span><b style="color:#ffffff;">${st.session_state.usd:,.2f}</b>
        <span style="margin-left:6px;" class="{pl_color}">P&L: <b>{total_pl:+,.2f}$</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_chart, tab_order, tab_analytics, tab_tools, tab_markets, tab_ai = st.tabs([
    "📈 Chart", "⚡ Order", "📊 Journal", "🛠 Tools", "🌍 Markets", "🧠 AI SMC"
])

# ================= 1. TRADINGVIEW SUPERCHART =================
with tab_chart:
    all_tfs = [
        "1S", "5S", "15S", "30S",
        "1", "3", "5", "15", "30", "45",
        "60", "120", "180", "240",
        "1D", "2D", "3D", "1W", "1M"
    ]
    
    col_sym, col_tf = st.columns([2.6, 1.4])
    with col_sym:
        st.markdown(f"<div style='padding-top:6px; padding-left:6px; font-size:13px;'>Active: <b style='color:#2962ff;'>{st.session_state.sym}</b></div>", unsafe_allow_html=True)
    with col_tf:
        st.session_state.tf = st.selectbox("Resolution", all_tfs, index=all_tfs.index(st.session_state.tf) if st.session_state.tf in all_tfs else 7, label_visibility="collapsed")

    # Dynamic Position Card on Chart
    cur_pos = [p for p in st.session_state.pos if p["symbol"] == st.session_state.sym]
    if cur_pos:
        for p in cur_pos:
            gain_pct = (p.get("leverage", 1) * 1.35) if "LONG" in p["type"] else -(p.get("leverage", 1) * 1.05)
            pnl = (p["margin"] * gain_pct) / 100
            p["running_pnl"] = pnl
            badge_border = "#089981" if pnl >= 0 else "#f23645"
            st.markdown(f"""
            <div class="card" style="border-left:4px solid {badge_border}; display:flex; justify-content:space-between; align-items:center; margin:2px 4px 6px 4px;">
                <div>
                    <b>{p['type']}</b> | Entry: <b>${p['entry']:,.2f}</b><br>
                    <span style="font-size:10px; color:#787b86;">TP: <b class="c-green">${p['tp']:,.2f}</b> | SL: <b class="c-red">${p['sl']:,.2f}</b></span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:14px; font-weight:bold; color:{'#089981' if pnl >= 0 else '#f23645'};">{pnl:+,.2f}$</span><br>
                    <span style="font-size:10px; color:#787b86;">ROI: {gain_pct:+.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TradingView Native SuperChart with all drawing toolbars
    chart_config = {
        "autosize": True,
        "symbol": st.session_state.sym,
        "interval": st.session_state.tf,
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#0c1017",
        "hide_side_toolbar": False,
        "allow_symbol_change": True,
        "save_image": True,
        "withdateranges": True,
        "details": False,
        "hotlist": False,
        "studies": [
            "RSI@tv-basicstudies",
            "MASimple@tv-basicstudies"
        ],
        "container_id": "tv_master_chart"
    }

    components.html(f"""
    <div style="height:76vh; width:100vw; margin:0; padding:0;">
        <div id="tv_master_chart" style="height:100%; width:100%;"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>new TradingView.widget({json.dumps(chart_config)});</script>
    </div>
    """, height=620)

# ================= 2. ADVANCED ORDER DESK =================
with tab_order:
    st.markdown("#### ⚡ Pro Execution Desk")
    st.markdown(f"<div class='card'>Asset: <b>{st.session_state.sym}</b> | Available Margin: <b style='color:#2962ff;'>${st.session_state.usd:,.2f}</b></div>", unsafe_allow_html=True)

    order_mode = st.radio("Order Type:", ["Market Execution", "Limit Pending Order", "Stop Market"], horizontal=True)

    c1, c2 = st.columns(2)
    with c1:
        margin = st.number_input("Margin Allocation ($):", min_value=10.0, max_value=float(st.session_state.usd), value=1000.0, step=100.0)
        leverage = st.selectbox("Leverage:", [1, 2, 5, 10, 20, 50, 100, 200], index=3)
    with c2:
        entry = st.number_input("Price ($):", value=2680.0 if "XAU" in st.session_state.sym else 84000.0 if "BTC" in st.session_state.sym else 150.0, step=1.0)
        logic = st.selectbox("Strategy / Setup Rationale:", [
            "SMC Order Block Retest",
            "Liquidity Pool Sweep",
            "Fair Value Gap (FVG) Fill",
            "Break of Structure (BOS)",
            "Change of Character (CHoCH)",
            "Multi-Timeframe Trendline Break"
        ])

    liq_long = entry * (1 - (1 / leverage) * 0.9)
    liq_short = entry * (1 + (1 / leverage) * 0.9)

    st.markdown("##### 🎯 Risk Management Targets (TP / SL)")
    col_tp, col_sl = st.columns(2)
    with col_tp:
        tp = st.number_input("Take-Profit (TP):", value=entry * 1.04, step=1.0)
    with col_sl:
        sl = st.number_input("Stop-Loss (SL):", value=entry * 0.98, step=1.0)

    r_val = abs(entry - sl)
    w_val = abs(tp - entry)
    rr = (w_val / r_val) if r_val > 0 else 1.0
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:11px; background:#161b26; padding:6px; border-radius:4px; margin-bottom:8px;">
        <span>Risk:Reward: <b>1 : {rr:.2f}</b></span>
        <span>Est. Liq (Long): <b class="c-red">${liq_long:,.2f}</b></span>
        <span>Est. Liq (Short): <b class="c-red">${liq_short:,.2f}</b></span>
    </div>
    """, unsafe_allow_html=True)

    btn1, btn2 = st.columns(2)
    if btn1.button(f"🟢 BUY / LONG ({leverage}x)", use_container_width=True):
        if st.session_state.usd >= margin:
            st.session_state.usd -= margin
            st.session_state.pos.append({
                "id": len(st.session_state.journal) + 1,
                "symbol": st.session_state.sym,
                "type": f"LONG {leverage}x",
                "margin": margin,
                "leverage": leverage,
                "entry": entry,
                "tp": tp,
                "sl": sl,
                "reason": logic,
                "mode": order_mode,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "running_pnl": 0.0
            })
            st.rerun()

    if btn2.button(f"🔴 SELL / SHORT ({leverage}x)", use_container_width=True):
        if st.session_state.usd >= margin:
            st.session_state.usd -= margin
            st.session_state.pos.append({
                "id": len(st.session_state.journal) + 1,
                "symbol": st.session_state.sym,
                "type": f"SHORT {leverage}x",
                "margin": margin,
                "leverage": leverage,
                "entry": entry,
                "tp": tp,
                "sl": sl,
                "reason": logic,
                "mode": order_mode,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "running_pnl": 0.0
            })
            st.rerun()

    st.markdown("##### 📊 Active Leveraged Positions")
    if st.session_state.pos:
        for idx, pos in enumerate(st.session_state.pos):
            gain = (pos.get("leverage", 1) * 1.25) if "LONG" in pos["type"] else -(pos.get("leverage", 1) * 0.95)
            amt = (pos["margin"] * gain) / 100
            c = "#089981" if amt >= 0 else "#f23645"
            
            st.markdown(f"""
            <div class="card" style="border-left:4px solid {c};">
                <div style="display:flex; justify-content:space-between;">
                    <div><b>{pos['symbol']}</b> ({pos['type']})<br><span style="font-size:10px; color:#787b86;">Setup: {pos['reason']}</span></div>
                    <div style="text-align:right;"><b style="color:{c};">{amt:+,.2f}$</b><br><span style="font-size:10px; color:{c};">{gain:+.2f}%</span></div>
                </div>
                <div style="margin-top:4px; font-size:10px; color:#787b86;">Entry: ${pos['entry']:,.2f} | TP: ${pos['tp']:,.2f} | SL: ${pos['sl']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✕ Close Trade #{idx+1}", key=f"cls_{idx}", use_container_width=True):
                st.session_state.usd += (pos["margin"] + amt)
                st.session_state.journal.insert(0, {
                    "symbol": pos["symbol"],
                    "type": pos["type"],
                    "entry": pos["entry"],
                    "margin": pos["margin"],
                    "pnl": amt,
                    "reason": pos["reason"],
                    "entry_time": pos["time"],
                    "exit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state.pos.pop(idx)
                st.rerun()
    else:
        st.caption("No open trades.")

# ================= 3. TRADING JOURNAL & PERFORMANCE ANALYTICS =================
with tab_analytics:
    st.markdown("#### 📊 Performance Analytics & Journal")
    
    total_trades = len(st.session_state.journal)
    wins = [j for j in st.session_state.journal if j["pnl"] > 0]
    win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
    net_realized = sum([j["pnl"] for j in st.session_state.journal])
    net_c = "#089981" if net_realized >= 0 else "#f23645"

    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div class='stat-badge'><span style='font-size:10px; color:#787b86;'>TOTAL TRADES</span><br><b style='font-size:15px;'>{total_trades}</b></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='stat-badge'><span style='font-size:10px; color:#787b86;'>WIN RATE</span><br><b style='font-size:15px; color:#2962ff;'>{win_rate:.1f}%</b></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='stat-badge'><span style='font-size:10px; color:#787b86;'>REALIZED P&L</span><br><b style='font-size:15px; color:{net_c};'>{net_realized:+,.2f}$</b></div>", unsafe_allow_html=True)

    st.markdown("##### 📖 Trade Audit Log")
    if st.session_state.journal:
        for j in st.session_state.journal:
            jc = "#089981" if j["pnl"] >= 0 else "#f23645"
            st.markdown(f"""
            <div class="card" style="border-left:4px solid {jc};">
                <div style="display:flex; justify-content:space-between;">
                    <div><b>{j['symbol']}</b> <span style="font-size:10px; color:#787b86;">[{j['type']}]</span><br><span style="font-size:10px; color:#2962ff;">Rationale: <b>{j['reason']}</b></span></div>
                    <div style="text-align:right;"><b style="color:{jc};">{j['pnl']:+,.2f}$</b><br><span style="font-size:10px; color:#787b86;">Margin: ${j['margin']:,.0f}</span></div>
                </div>
                <div style="font-size:9px; color:#787b86; margin-top:4px;">In: {j['entry_time']} | Out: {j['exit_time']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("Your closed trades will appear here automatically.")

    if st.button("🔄 Reset Portfolio Capital ($100,000)"):
        st.session_state.usd = 100000.0
        st.session_state.pos = []
        st.session_state.journal = []
        st.rerun()

# ================= 4. TRADINGVIEW SUITE TOOLS (CALENDAR & SCREENER) =================
with tab_tools:
    st.markdown("#### 🛠 TradingView Suite & Indicators")
    tool_select = st.radio("Select Suite Tool:", ["Technical Analysis Gauge", "Economic Macro Calendar", "Crypto Market Heatmap"], horizontal=True)

    if tool_select == "Technical Analysis Gauge":
        st.caption("Live TradingView Oscillators & Moving Averages Gauge:")
        gauge_cfg = {
            "interval": "15m",
            "width": "100%",
            "isTransparent": True,
            "height": "420",
            "symbol": st.session_state.sym,
            "showIntervalTabs": True,
            "displayMode": "single",
            "locale": "en",
            "colorTheme": "dark"
        }
        components.html(f"""
        <div style="height:430px; width:100%;">
            <div class="tradingview-widget-container">
                <div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
                {json.dumps(gauge_cfg)}
                </script>
            </div>
        </div>
        """, height=440)

    elif tool_select == "Economic Macro Calendar":
        st.caption("Global Central Banks, CPI, NFP & GDP Announcements:")
        cal_cfg = {
            "colorTheme": "dark",
            "isTransparent": True,
            "width": "100%",
            "height": "500",
            "locale": "en",
            "importanceFilter": "-1,0,1"
        }
        components.html(f"""
        <div style="height:510px; width:100%;">
            <div class="tradingview-widget-container">
                <div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
                {json.dumps(cal_cfg)}
                </script>
            </div>
        </div>
        """, height=520)

    elif tool_select == "Crypto Market Heatmap":
        st.caption("Live Global Cryptocurrency Market Visual Heatmap:")
        heat_cfg = {
            "dataSource": "Crypto",
            "blockSize": "market_cap_calc",
            "blockColor": "change",
            "locale": "en",
            "symbolUrl": "",
            "colorTheme": "dark",
            "hasTopBar": False,
            "isDataSetEnabled": False,
            "isZoomEnabled": True,
            "hasSymbolTooltip": True,
            "width": "100%",
            "height": "500"
        }
        components.html(f"""
        <div style="height:510px; width:100%;">
            <div class="tradingview-widget-container">
                <div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js" async>
                {json.dumps(heat_cfg)}
                </script>
            </div>
        </div>
        """, height=520)

# ================= 5. ALL GLOBAL MARKETS DIRECTORY =================
with tab_markets:
    st.markdown("##### 🔍 Universal Asset Search")
    st.caption("Search ANY stock, crypto, forex, or commodity across the globe:")
    
    col_s1, col_s2 = st.columns([3.5, 1])
    with col_s1:
        custom_asset = st.text_input("Ticker:", placeholder="e.g. NASDAQ:NVDA, BINANCE:SOLUSDT, FX:EURUSD, OANDA:XAUUSD", label_visibility="collapsed")
    with col_s2:
        if st.button("Load ➔", use_container_width=True) and custom_asset.strip():
            st.session_state.sym = custom_asset.strip().upper()
            st.rerun()

    global_markets = {
        "Gold, Metals & Oil": [
            ("OANDA:XAUUSD", "Gold Spot / USD", "2,682.40", "+0.72%"),
            ("OANDA:XAGUSD", "Silver Spot / USD", "31.85", "+1.15%"),
            ("TVC:USOIL", "WTI Crude Oil", "71.60", "-1.10%"),
            ("TVC:BRENT", "Brent Crude Oil", "75.80", "-0.85%")
        ],
        "Crypto Perpetuals": [
            ("BINANCE:BTCUSDT", "Bitcoin / Tether", "84,210.00", "+2.85%"),
            ("BINANCE:ETHUSDT", "Ethereum / Tether", "2,690.00", "+1.90%"),
            ("BINANCE:SOLUSDT", "Solana / Tether", "152.40", "+5.40%"),
            ("BINANCE:PEPEUSDT", "Pepe / Tether", "0.0000122", "+9.10%")
        ],
        "US Mega-Cap Stocks": [
            ("NASDAQ:NVDA", "NVIDIA Corp", "132.50", "+3.80%"),
            ("NASDAQ:AAPL", "Apple Inc.", "229.80", "+1.10%"),
            ("NASDAQ:TSLA", "Tesla Inc.", "258.40", "-1.85%"),
            ("NASDAQ:MSFT", "Microsoft Corp", "455.20", "+1.25%")
        ],
        "Forex Major Pairs": [
            ("FX:EURUSD", "Euro / US Dollar", "1.10950", "-0.08%"),
            ("FX:GBPUSD", "British Pound / USD", "1.31420", "+0.15%"),
            ("FX:USDJPY", "US Dollar / Japanese Yen", "142.650", "-0.38%"),
            ("FX:AUDUSD", "Australian Dollar / USD", "0.67400", "+0.25%")
        ]
    }

    for cat_name, ticker_list in global_markets.items():
        st.markdown(f"<span style='font-size:11px; font-weight:bold; color:#787b86;'>∨ {cat_name}</span>", unsafe_allow_html=True)
        for sym_code, label_name, last_price, pct_change in ticker_list:
            c1, c2, c3 = st.columns([2.5, 2, 1.2])
            c1.markdown(f"<b>{label_name}</b><br><span style='font-size:9px; color:#787b86;'>{sym_code}</span>", unsafe_allow_html=True)
            colr = "#089981" if "+" in pct_change else "#f23645"
            c2.markdown(f"<div style='text-align:right;'><b>{last_price}</b><br><span sty
