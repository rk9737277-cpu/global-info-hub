import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import feedparser

# Page Config - Fullscreen Pro Terminal
st.set_page_config(
    page_title="deeepr.ai - Pro Derivatives Terminal",
    layout="centered",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# --- Session State Initialization ---
if "market_mode" not in st.session_state:
    st.session_state.market_mode = "Options Chain"
if "balance_inr" not in st.session_state:
    st.session_state.balance_inr = 100000.0  # ₹1,00,000 F&O Capital
if "balance_usd" not in st.session_state:
    st.session_state.balance_usd = 10000.0   # $10,000 Crypto Capital
if "positions_inr" not in st.session_state:
    st.session_state.positions_inr = []
if "positions_crypto" not in st.session_state:
    st.session_state.positions_crypto = []
if "ai_news_intel" not in st.session_state:
    st.session_state.ai_news_intel = ""

# --- Binance Public API Live Data ---
@st.cache_data(ttl=8)
def fetch_binance_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        res = requests.get(url, timeout=4).json()
        rates = {}
        for row in res:
            sym = row.get("symbol", "")
            if sym.endswith("USDT"):
                rates[sym.replace("USDT", "")] = {
                    "price": float(row["lastPrice"]),
                    "change": float(row["priceChangePercent"])
                }
        return rates
    except Exception:
        return {
            "BTC": {"price": 82450.0, "change": 2.4},
            "ETH": {"price": 2520.0, "change": -0.6},
            "SOL": {"price": 114.2, "change": 4.1}
        }

crypto_rates = fetch_binance_data()

POPULAR_INDIAN_STOCKS = [
    "NIFTY", "BANKNIFTY", "RELIANCE", "TCS", "HDFCBANK", "TATAMOTORS",
    "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "LT", "BAJFINANCE",
    "ADANIENT", "ZOMATO", "SUZLON", "PAYTM", "HAL", "BEL", "TRENT"
]

# --- Native Dark Terminal CSS (No config.toml required) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0c1017 !important;
        color: #e6edf3 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 8px !important;
        padding-bottom: 75px !important;
        max-width: 500px !important;
    }
    header, footer { visibility: hidden; }

    div[data-baseweb="input"] {
        border-radius: 18px !important;
        background-color: #151b26 !important;
        border: 1px solid #334155 !important;
        color: #ffffff !important;
    }

    .ticker-belt {
        display: flex;
        gap: 12px;
        overflow-x: auto;
        padding: 5px 2px 10px 2px;
        font-size: 11px;
        color: #94a3b8;
        border-bottom: 1px solid #232d3f;
        margin-bottom: 10px;
    }
    .c-green { color: #22c55e; font-weight: bold; }
    .c-red { color: #ef4444; font-weight: bold; }

    .terminal-card {
        background: #151b26;
        border: 1px solid #232d3f;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .pos-item {
        background: #0f172a;
        border-left: 4px solid #38bdf8;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 12px;
    }
    .chain-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        text-align: center;
        margin-top: 8px;
    }
    .chain-table th {
        background-color: #1a2332;
        color: #94a3b8;
        padding: 6px 4px;
        border: 1px solid #232d3f;
    }
    .chain-table td {
        padding: 6px 4px;
        border: 1px solid #232d3f;
    }
    .atm-row {
        background-color: #1e293b !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 1. Header & Capital Overview
head_col1, head_col2 = st.columns([1.2, 1])
with head_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px;">
        <span style="color:#0ea5e9; font-size:20px;">⚡</span>
        <div>
            <div style="font-size:18px; font-weight:800; color:#38bdf8;">deeepr.ai</div>
            <div style="font-size:9px; color:#94a3b8; font-weight:600;">PRO F&O + 200X DESK</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    if st.session_state.market_mode in ["Options Chain", "Indian Stocks"]:
        st.markdown(f"""
        <div style="text-align:right;">
            <div style="background:#1e293b; border:1px solid #22c55e; border-radius:14px; padding:3px 10px; font-size:12px; color:#22c55e; font-weight:bold; display:inline-block;">
                ₹{st.session_state.balance_inr:,.2f}
            </div>
            <div style="font-size:9px; color:#64748b; margin-top:2px;">₹1L CAPITAL (5X MIS)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:right;">
            <div style="background:#1e293b; border:1px solid #38bdf8; border-radius:14px; padding:3px 10px; font-size:12px; color:#38bdf8; font-weight:bold; display:inline-block;">
                ${st.session_state.balance_usd:,.2f}
            </div>
            <div style="font-size:9px; color:#64748b; margin-top:2px;">200X LEVERAGE DESK</div>
        </div>
        """, unsafe_allow_html=True)

# 2. Live Market Ticker Belt
btc_meta = crypto_rates.get("BTC", {"price": 82450.0, "change": 2.4})
eth_meta = crypto_rates.get("ETH", {"price": 2520.0, "change": -0.6})
sol_meta = crypto_rates.get("SOL", {"price": 114.2, "change": 4.1})

st.markdown(f"""
<div class="ticker-belt">
    <span>NIFTY 50 <b style="color:#fff;">24,850.40</b> <span class="c-green">+0.52%</span></span>
    <span>BANKNIFTY <b style="color:#fff;">51,320.00</b> <span class="c-green">+0.80%</span></span>
    <span>BTC <b style="color:#fff;">${btc_meta['price']:,.0f}</b> <span class="{'c-green' if btc_meta['change']>=0 else 'c-red'}">{btc_meta['change']:+.1f}%</span></span>
    <span>ETH <b style="color:#fff;">${eth_meta['price']:,.0f}</b> <span class="{'c-green' if eth_meta['change']>=0 else 'c-red'}">{eth_meta['change']:+.1f}%</span></span>
</div>
""", unsafe_allow_html=True)

# 3. Mode Switcher Tabs
tab_opt, tab_in, tab_cr = st.columns(3)
if tab_opt.button("🎯 Nifty Options", use_container_width=True):
    st.session_state.market_mode = "Options Chain"
    st.rerun()
if tab_in.button("🇮🇳 5x Stocks", use_container_width=True):
    st.session_state.market_mode = "Indian Stocks"
    st.rerun()
if tab_cr.button("⚡ 200x Crypto", use_container_width=True):
    st.session_state.market_mode = "Crypto Futures"
    st.rerun()

st.markdown("---")

# ==========================================
# 🎯 TAB 1: NIFTY 50 OPTION CHAIN DESK
# ==========================================
if st.session_state.market_mode == "Options Chain":
    st.markdown("#### 🎯 NIFTY 50 Live Option Chain & Execution")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown('<div class="terminal-card"><span style="font-size:11px; color:#94a3b8;">NIFTY Spot</span><div style="font-size:18px; font-weight:800; color:#38bdf8;">24,850.40</div></div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown('<div class="terminal-card"><span style="font-size:11px; color:#94a3b8;">Lot Size</span><div style="font-size:18px; font-weight:800; color:#facc15;">25 Qty / Weekly</div></div>', unsafe_allow_html=True)

    components.html("""
    <div style="height: 320px; width: 100%;">
        <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tv_nifty&symbol=NSE:NIFTY&interval=5&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0c1017&theme=dark&style=1&timezone=Asia%2FKolkata&locale=en"
                style="width: 100%; height: 320px; border: none; border-radius: 12px;"></iframe>
    </div>
    """, height=330)

    chain_rows = [
        {"strike": 24700, "ce_ltp": 190.20, "ce_oi": "35.1L", "pe_ltp": 45.30, "pe_oi": "78.9L", "atm": False},
        {"strike": 24750, "ce_ltp": 152.40, "ce_oi": "42.8L", "pe_ltp": 61.80, "pe_oi": "66.4L", "atm": False},
        {"strike": 24800, "ce_ltp": 118.90, "ce_oi": "65.3L", "pe_ltp": 82.50, "pe_oi": "95.1L", "atm": False},
        {"strike": 24850, "ce_ltp": 89.20, "ce_oi": "92.6L", "pe_ltp": 108.40, "pe_oi": "88.7L", "atm": True},
        {"strike": 24900, "ce_ltp": 64.70, "ce_oi": "1.1Cr", "pe_ltp": 139.10, "pe_oi": "52.3L", "atm": False},
        {"strike": 24950, "ce_ltp": 45.10, "ce_oi": "82.4L", "pe_ltp": 174.60, "pe_oi": "31.2L", "atm": False},
        {"strike": 25000, "ce_ltp": 30.80, "ce_oi": "1.4Cr", "pe_ltp": 215.00, "pe_oi": "18.5L", "atm": False},
    ]

    table_html = """<table class="chain-table"><thead><tr><th style="color:#22c55e;">CALLS LTP</th><th>CALLS OI</th><th style="color:#facc15;">STRIKE</th><th>PUTS OI</th><th style="color:#ef4444;">PUTS LTP</th></tr></thead><tbody>"""
    for r in chain_rows:
        row_cls = ' class="atm-row"' if r["atm"] else ""
        badge = " (ATM)" if r["atm"] else ""
        table_html += f"""<tr{row_cls}><td style="color:#22c55e;">₹{r['ce_ltp']:.2f}</td><td style="color:#94a3b8;">{r['ce_oi']}</td><td style="color:#facc15; font-weight:bold;">{r['strike']}{badge}</td><td style="color:#94a3b8;">{r['pe_oi']}</td><td style="color:#ef4444;">₹{r['pe_ltp']:.2f}</td></tr>"""
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")
    st_c1, st_c2, st_c3 = st.columns(3)
    with st_c1:
        sel_strike = st.selectbox("Strike Price:", [r["strike"] for r in chain_rows], index=3)
    with st_c2:
        sel_type = st.selectbox("Type:", ["CALL (CE)", "PUT (PE)"])
    with st_c3:
        sel_lots = st.number_input("Lots (25 Qty):", min_value=1, max_value=20, value=2, step=1)

    matched = next(r for r in chain_rows if r["strike"] == sel_strike)
    opt_ltp = matched["ce_ltp"] if "CALL" in sel_type else matched["pe_ltp"]
    total_qty = sel_lots * 25
    total_premium = total_qty * opt_ltp

    st.markdown(f'<div class="terminal-card">Contract: <b>NIFTY {sel_strike} {sel_type[:2]}</b> | Premium: <b style="color:#38bdf8;">₹{opt_ltp:.2f}</b><br><span style="font-size:12px; color:#94a3b8;">Total Qty: <b>{total_qty}</b> | Margin: <b style="color:#facc15;">₹{total_premium:,.2f}</b></span></div>', unsafe_allow_html=True)

    b_buy, b_sell = st.columns(2)
    with b_buy:
        if st.button(f"🟢 BUY {sel_type[:2]}", use_container_width=True):
            if st.session_state.balance_inr >= total_premium:
                st.session_state.balance_inr -= total_premium
                st.session_state.positions_inr.append({
                    "symbol": f"NIFTY {sel_strike} {sel_type[:2]}", "type": "BUY OPTION", "qty": total_qty, "entry": opt_ltp, "margin": total_premium
                })
                st.rerun()
            else:
                st.error("Insufficient INR balance.")
    with b_sell:
        if st.button(f"🔴 SHORT {sel_type[:2]}", use_container_width=True):
            sm = total_premium * 3.5
            if st.session_state.balance_inr >= sm:
                st.session_state.balance_inr -= sm
                st.session_state.positions_inr.append({
                    "symbol": f"NIFTY {sel_strike} {sel_type[:2]}", "type": "SELL OPTION", "qty": total_qty, "entry": opt_ltp, "margin": sm
                })
                st.rerun()
            else:
                st.error("Insufficient margin for option selling.")

    st.markdown("##### 📊 Active F&O Positions:")
    if st.session_state.positions_inr:
        for idx, pos in enumerate(st.session_state.positions_inr):
            gain = 12.5 if "BUY" in pos["type"] else -6.2
            pnl_amt = (pos["margin"] * gain) / 100
            pnl_col = "#22c55e" if pnl_amt >= 0 else "#ef4444"
            st.markdown(f"""
            <div class="pos-item">
                <div style="display:flex; justify-content:space-between; font-weight:bold;">
                    <span>{pos['symbol']} ({pos['type']})</span>
                    <span style="color:{pnl_col};">{gain:+.1f}% (₹{pnl_amt:,.2f})</span>
                </div>
                <div style="color:#94a3b8; font-size:11px; margin-top:3px;">
                    Qty: {pos.get('qty', 50)} | Margin: ₹{pos['margin']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"✕ Square Off #{idx+1}", key=f"sq_opt_{idx}"):
                st.session_state.balance_inr += (pos["margin"] + pnl_amt)
                st.session_state.positions_inr.pop(idx)
                st.rerun()
    else:
        st.caption("No open F&O positions.")

    if st.button("🔄 Reset ₹1,00,000 Portfolio"):
        st.session_state.balance_inr = 100000.0
        st.session_state.positions_inr = []
        st.rerun()

# ==========================================
# 🇮🇳 TAB 2: ALL INDIAN STOCKS (5X MIS)
# ==========================================
elif st.session_state.market_mode == "Indian Stocks":
    st.markdown("#### 🇮🇳 Indian Equities (NSE/BSE 5x Leverage)")
    s1, s2 = st.columns([1.2, 1])
    with s1:
        preset_st = st.selectbox("Asset:", POPULAR_INDIAN_STOCKS, index=0)
    with s2:
        custom_st = st.text_input("Custom Symbol:", placeholder="e.g. TRENT, BEL...")

    final_st = custom_st.strip().upper() if custom_st.strip() else preset_st

    components.html(f"""
    <div style="height: 340px; width: 100%;">
        <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tv_in&symbol=NSE:{final_st}&interval=15&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0c1017&theme=dark&style=1&timezone=Asia%2FKolkata&locale=en"
                style="width: 100%; height: 340px; border: none; border-radius: 12px;"></iframe>
    </div>
    """, height=350)

    mc1, mc2 = st.columns(2)
    with mc1:
        m_inr = st.number_input("Margin (₹):", min_value=500.0, max_value=float(st.session_state.balance_inr), value=5000.0, step=1000.0)
    with mc2:
        p_inr = m_inr * 5.0
        st.markdown(f"<div style='padding-top:28px; font-size:13px; color:#22c55e;'>5x Power: <b>₹{p_inr:,.0f}</b></div>", unsafe_allow_html=True)

    b1, s1 = st.columns(2)
    with b1:
        if st.button(f"🟢 BUY 5x ({final_st})", use_container_width=True):
            if st.session_state.balance_inr >= m_inr:
                st.session_state.balance_inr -= m_inr
                st.session_state.positions_inr.append({"symbol": final_st, "type": "BUY 5x", "margin": m_inr, "exposure": p_inr})
                st.rerun()
    with s1:
        if st.button(f"🔴 SHORT 5x ({final_st})", use_container_width=True):
            if st.session_state.balance_inr >= m_inr:
                st.session_state.balance_inr -= m_inr
                st.session_state.positions_inr.append({"symbol": final_st, "type": "SHORT 5x", "margin": m_inr, "exposure": p_inr})
                st.rerun()

    st.markdown("##### 📊 Active 5x Equity Positions:")
    if st.session_state.positions_inr:
        for idx, pos in enumerate(st.session_state.positions_inr):
            gain = 1.4 * 5 if "BUY" in pos["type"] else -0.8 * 5
            pnl_amt = (pos["margin"] * gain) / 100
            pnl_col = "#22c55e" if pnl_amt >= 0 else "#ef4444"
            st.markdown(f"""
            <div class="pos-item">
                <div style="display:flex; justify-content:space-between; font-weight:bold;">
                    <span>{pos['symbol']} ({pos['type']})</span>
                    <span style="color:{pnl_col};">{gain:+.1f}% (₹{pnl_amt:,.2f})</span>
                </div>
                <div style="color:#94a3b8; font-size:11px; margin-top:3px;">Margin: ₹{pos['margin']:,.0f} | Exposure: ₹{pos['exposure']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"✕ Square Off #{idx+1}", key=f"sq_eq_{idx}"):
                st.session_state.balance_inr += (pos["margin"] + pnl_amt)
                st.session_state.positions_inr.pop(idx)
                st.rerun()

# ==========================================
# ⚡ TAB 3: 200X CRYPTO FUTURES DESK
# ==========================================
else:
    st.markdown("#### ⚡ 200x Crypto Futures (Binance Real-Time)")
    c_list = list(crypto_rates.keys()) or ["BTC", "ETH", "SOL", "BNB", "XRP"]
    c1, c2 = st.columns([1.2, 1])
    with c1:
        c_coin = st.selectbox("Asset:", c_list[:30], index=0)
    with c2:
        c_lev = st.selectbox("Leverage:", [2, 5, 10, 25, 50, 100, 150, 200], index=7)

    live_px = crypto_rates.get(c_coin, {"price": 82450.0})["price"]
    st.markdown(f'<div class="terminal-card">1 {c_coin}: <b style="color:#38bdf8;">${live_px:,.4f}</b> | Leverage: <b style="color:#facc15;">{c_lev}x</b></div>', unsafe_allow_html=True)

    components.html(f"""
    <div style="height: 330px; width: 100%;">
        <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tv_cr&symbol=BINANCE:{c_coin}USDT&interval=60&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0c1017&theme=dark&style=1&timezone=Asia%2FKolkata&locale=en"
                style="width: 100%; height: 330px; border: none; border-radius: 12px;"></iframe>
    </div>
    """, height=340)

    cm1, cm2 = st.columns(2)
    with cm1:
        m_usd = st.number_input("Margin ($):", min_value=10.0, value=100.0, step=50.0)
    with cm2:
        liq = live_px * (1 - (100.0 / c_lev) / 100)
        st.markdown(f"<div style='padding-top:25px; font-size:11px; color:#ef4444;'>Est. Liq: <b>${liq:,.2f}</b></div>", unsafe_allow_html=True)

    cb1, cs1 = st.columns(2)
    with cb1:
        if st.button(f"🟢 LONG ({c_lev}x)", use_container_width=True):
            if st.session_state.balance_usd >= m_usd:
                st.session_state.balance_usd -= m_usd
                st.session_state.positions_crypto.append({"coin": c_coin, "type": "LONG", "margin": m_usd, "lev": c_lev, "entry": live_px})
                st.rerun()
    with cs1:
        if st.button(f"🔴 SHORT ({c_lev}x)", use_container_width=True):
            if st.session_state.balance_usd >= m_usd:
                st.session_state.balance_usd -= m_usd
                st.session_state.positions_crypto.append({"coin": c_coin, "type": "SHORT", "margin": m_usd, "lev": c_lev, "entry": live_px})
                st.rerun()

    st.markdown("##### 📊 Active Crypto Positions:")
    if st.session_state.positions_crypto:
        for idx, p in enumerate(st.session_state.positions_crypto):
            pct = 2.4 * p["lev"] if p["type"] == "LONG" else -1.2 * p["lev"]
            amt = (p["margin"] * pct) / 100
            clr = "#22c55e" if amt >= 0 else "#ef4444"
            st.markdown(f"""
            <div class="pos-item">
                <div style="display:flex; justify-content:space-between; font-weight:bold;">
                    <span>{p['coin']} ({p['type']} {p['lev']}x)</span>
                    <span style="color:{clr};">{pct:+.1f}% (${amt:,.2f})</span>
                </div>
                <div style="color:#94a3b8; font-size:11px; margin-top:3px;">Margin: ${p['margin']} | Entry: ${p['entry']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"✕ Close #{idx+1}", key=f"cr_cls_{idx}"):
                st.session_state.balance_usd += (p["margin"] + amt)
                st.session_state.positions_crypto.pop(idx)
                st.rerun()
    else:
        st.caption("No open crypto futures positions.")

    if st.button("🔄 Reset $10,000 Portfolio"):
        st.session_state.balance_usd = 10000.0
        st.session_state.positions_crypto = []
        st.rerun()

# ==========================================
# 🎙️ TAB 4: AI TRADING NEWS & VOICE ASSISTANT
# ==========================================
st.markdown("---")
st.markdown("#### 🎙️ AI Market News Desk (Voice & Intel)")

components.html("""
<div style="display:flex; justify-content:center; margin-bottom:10px;">
    <button onclick=
