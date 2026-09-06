import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import feedparser

st.set_page_config(
    page_title="deeepr.ai - Pro Terminal",
    layout="centered",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# --- Session State ---
if "market_mode" not in st.session_state:
    st.session_state.market_mode = "Options Chain"
if "balance_inr" not in st.session_state:
    st.session_state.balance_inr = 100000.0
if "balance_usd" not in st.session_state:
    st.session_state.balance_usd = 10000.0
if "positions_inr" not in st.session_state:
    st.session_state.positions_inr = []
if "positions_crypto" not in st.session_state:
    st.session_state.positions_crypto = []
if "ai_news_intel" not in st.session_state:
    st.session_state.ai_news_intel = ""

# --- Binance API ---
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

# --- Styling ---
st.markdown(
    "<style>"
    ".stApp { background-color: #0c1017 !important; color: #e6edf3 !important; }"
    ".block-container { padding-top: 8px !important; padding-bottom: 75px !important; max-width: 500px !important; }"
    "header, footer { visibility: hidden; }"
    "div[data-baseweb='input'] { border-radius: 18px !important; background-color: #151b26 !important; border: 1px solid #334155 !important; color: #ffffff !important; }"
    ".ticker-belt { display: flex; gap: 12px; overflow-x: auto; padding: 5px 2px 10px 2px; font-size: 11px; color: #94a3b8; border-bottom: 1px solid #232d3f; margin-bottom: 10px; }"
    ".c-green { color: #22c55e; font-weight: bold; }"
    ".c-red { color: #ef4444; font-weight: bold; }"
    ".terminal-card { background: #151b26; border: 1px solid #232d3f; border-radius: 12px; padding: 12px; margin-bottom: 12px; }"
    ".pos-item { background: #0f172a; border-left: 4px solid #38bdf8; padding: 10px; border-radius: 8px; margin-bottom: 8px; font-size: 12px; }"
    ".chain-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; margin-top: 8px; }"
    ".chain-table th { background-color: #1a2332; color: #94a3b8; padding: 6px 4px; border: 1px solid #232d3f; }"
    ".chain-table td { padding: 6px 4px; border: 1px solid #232d3f; }"
    ".atm-row { background-color: #1e293b !important; font-weight: bold; }"
    "</style>",
    unsafe_allow_html=True
)

# Header
h1, h2 = st.columns([1.2, 1])
with h1:
    st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span style='color:#0ea5e9; font-size:20px;'>⚡</span><div><div style='font-size:18px; font-weight:800; color:#38bdf8;'>deeepr.ai</div><div style='font-size:9px; color:#94a3b8; font-weight:600;'>PRO F&O + 200X DESK</div></div></div>", unsafe_allow_html=True)
with h2:
    if st.session_state.market_mode in ["Options Chain", "Indian Stocks"]:
        st.markdown(f"<div style='text-align:right;'><div style='background:#1e293b; border:1px solid #22c55e; border-radius:14px; padding:3px 10px; font-size:12px; color:#22c55e; font-weight:bold; display:inline-block;'>₹{st.session_state.balance_inr:,.2f}</div><div style='font-size:9px; color:#64748b; margin-top:2px;'>₹1L CAPITAL (5X MIS)</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:right;'><div style='background:#1e293b; border:1px solid #38bdf8; border-radius:14px; padding:3px 10px; font-size:12px; color:#38bdf8; font-weight:bold; display:inline-block;'>${st.session_state.balance_usd:,.2f}</div><div style='font-size:9px; color:#64748b; margin-top:2px;'>200X LEVERAGE DESK</div></div>", unsafe_allow_html=True)

# Ticker
btc_m = crypto_rates.get("BTC", {"price": 82450.0, "change": 2.4})
eth_m = crypto_rates.get("ETH", {"price": 2520.0, "change": -0.6})
st.markdown(f"<div class='ticker-belt'><span>NIFTY 50 <b style='color:#fff;'>24,850.40</b> <span class='c-green'>+0.52%</span></span><span>BANKNIFTY <b style='color:#fff;'>51,320.00</b> <span class='c-green'>+0.80%</span></span><span>BTC <b style='color:#fff;'>${btc_m['price']:,.0f}</b> <span class='{'c-green' if btc_m['change']>=0 else 'c-red'}'>{btc_m['change']:+.1f}%</span></span><span>ETH <b style='color:#fff;'>${eth_m['price']:,.0f}</b> <span class='{'c-green' if eth_m['change']>=0 else 'c-red'}'>{eth_m['change']:+.1f}%</span></span></div>", unsafe_allow_html=True)

# Tabs
t_opt, t_in, t_cr = st.columns(3)
if t_opt.button("🎯 Nifty Options", use_container_width=True):
    st.session_state.market_mode = "Options Chain"
    st.rerun()
if t_in.button("🇮🇳 5x Stocks", use_container_width=True):
    st.session_state.market_mode = "Indian Stocks"
    st.rerun()
if t_cr.button("⚡ 200x Crypto", use_container_width=True):
    st.session_state.market_mode = "Crypto Futures"
    st.rerun()

st.markdown("---")

# ==================== 1. OPTION CHAIN ====================
if st.session_state.market_mode == "Options Chain":
    st.markdown("#### 🎯 NIFTY 50 Live Option Chain & Execution")
    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown("<div class='terminal-card'><span style='font-size:11px; color:#94a3b8;'>NIFTY Spot</span><div style='font-size:18px; font-weight:800; color:#38bdf8;'>24,850.40</div></div>", unsafe_allow_html=True)
    with cs2:
        st.markdown("<div class='terminal-card'><span style='font-size:11px; color:#94a3b8;'>Lot Size</span><div style='font-size:18px; font-weight:800; color:#facc15;'>25 Qty / Weekly</div></div>", unsafe_allow_html=True)

    components.html("<iframe src='https://s.tradingview.com/widgetembed/?frameElementId=tv_nifty&symbol=NSE:NIFTY&interval=5&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0c1017&theme=dark&style=1&timezone=Asia%2FKolkata&locale=en' style='width:100%; height:320px; border:none; border-radius:12px;'></iframe>", height=330)

    chain_rows = [
        {"strike": 24700, "ce_ltp": 190.20, "ce_oi": "35.1L", "pe_ltp": 45.30, "pe_oi": "78.9L", "atm": False},
        {"strike": 24750, "ce_ltp": 152.40, "ce_oi": "42.8L", "pe_ltp": 61.80, "pe_oi": "66.4L", "atm": False},
        {"strike": 24800, "ce_ltp": 118.90, "ce_oi": "65.3L", "pe_ltp": 82.50, "pe_oi": "95.1L", "atm": False},
        {"strike": 24850, "ce_ltp": 89.20, "ce_oi": "92.6L", "pe_ltp": 108.40, "pe_oi": "88.7L", "atm": True},
        {"strike": 24900, "ce_ltp": 64.70, "ce_oi": "1.1Cr", "pe_ltp": 139.10, "pe_oi": "52.3L", "atm": False},
        {"strike": 24950, "ce_ltp": 45.10, "ce_oi": "82.4L", "pe_ltp": 174.60, "pe_oi": "31.2L", "atm": False},
        {"strike": 25000, "ce_ltp": 30.80, "ce_oi": "1.4Cr", "pe_ltp": 215.00, "pe_oi": "18.5L", "atm": False},
    ]

    t_rows = ""
    for r in chain_rows:
        cls = " class='atm-row'" if r["atm"] else ""
        bdg = " (ATM)" if r["atm"] else ""
        t_rows += f"<tr{cls}><td style='color:#22c55e;'>₹{r['ce_ltp']:.2f}</td><td style='color:#94a3b8;'>{r['ce_oi']}</td><td style='color:#facc15; font-weight:bold;'>{r['strike']}{bdg}</td><td style='color:#94a3b8;'>{r['pe_oi']}</td><td style='color:#ef4444;'>₹{r['pe_ltp']:.2f}</td></tr>"

    st.markdown(f"<table class='chain-table'><thead><tr><th style='color:#22c55e;'>CALLS LTP</th><th>CALLS OI</th><th style='color:#facc15;'>STRIKE</th><th>PUTS OI</th><th style='color:#ef4444;'>PUTS LTP</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)

    st.markdown("---")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        s_strike = st.selectbox("Strike:", [r["strike"] for r in chain_rows], index=3)
    with sc2:
        s_type = st.selectbox("Type:", ["CALL (CE)", "PUT (PE)"])
    with sc3:
        s_lots = st.number_input("Lots (25 Qty):", min_value=1, max_value=20, value=2, step=1)

    matched = next(r for r in chain_rows if r["strike"] == s_strike)
    opt_ltp = matched["ce_ltp"] if "CALL" in s_type else matched["pe_ltp"]
    tot_qty = s_lots * 25
    tot_prem = tot_qty * opt_ltp

    st.markdown(f"<div class='terminal-card'>Contract: <b>NIFTY {s_strike} {s_type[:2]}</b> | Premium: <b style='color:#38bdf8;'>₹{opt_ltp:.2f}</b><br><span style='font-size:12px; color:#94a3b8;'>Total Qty: <b>{tot_qty}</b> | Margin: <b style='color:#facc15;'>₹{tot_prem:,.2f}</b></span></div>", unsafe_allow_html=True)

    bb, sb = st.columns(2)
    with bb:
        if st.button(f"🟢 BUY {s_type[:2]}", use_container_width=True):
            if st.session_state.balance_inr >= tot_prem:
                st.session_state.balance_inr -= tot_prem
                st.session_state.positions_inr.append({"symbol": f"NIFTY {s_strike} {s_type[:2]}", "type": "BUY OPTION", "qty": tot_qty, "entry": opt_ltp, "margin": tot_prem})
                st.rerun()
            else:
                st.error("Insufficient INR.")
    with sb:
        if st.button(f"🔴 SHORT {s_type[:2]}", use_container_width=True):
            sm = tot_prem * 3.5
            if st.session_state.balance_inr >= sm:
                st.session_state.balance_inr -= sm
                st.session_state.positions_inr.append({"symbol": f"NIFTY {s_strike} {s_type[:2]}", "type": "SELL OPTION", "qty": tot_qty, "entry": opt_ltp, "margin": sm})
                st.rerun()
            else:
                st.error("Insufficient Margin.")

    st.markdown("##### 📊 Active F&O Positions:")
    if st.session_state.positions_inr:
        for idx, pos in enumerate(st.session_state.positions_inr):
            gn = 12.5 if "BUY" in pos["type"] else -6.2
            amt = (pos["margin"] * gn) / 100
            colr = "#22c55e" if amt >= 0 else "#ef4444"
            st.markdown(f"<div class='pos-item'><div style='display:flex; justify-content:space-between; font-weight:bold;'><span>{pos['symbol']} ({pos['type']})</span><span style='color:{colr};'>{gn:+.1f}% (₹{amt:,.2f})</span></div><div style='color:#94a3b8; font-size:11px; margin-top:3px;'>Qty: {pos.get('qty', 50)} | Margin: ₹{pos['margin']:,.0f}</div></div>", unsafe_allow_html=True)
            if st.button(f"✕ Square Off #{idx+1}", key=f"sq_opt_{idx}"):
                st.session_state.balance_inr += (pos["margin"] + amt)
                st.session_state.positions_inr.pop(idx)
                st.rerun()
    else:
        st.caption("No open F&O positions.")

    if st.button("🔄 Reset Portfolio"):
        st.session_state.balance_inr = 100000.0
        st.session_state.positions_inr = []
        st.rerun()

# ==================== 2. INDIAN STOCKS ====================
elif st.session_state.market_mode == "Indian Stocks":
    st.markdown("#### 🇮🇳 Indian Equities (NSE/BSE 5x Leverage)")
    s1, s2 = st.columns([1.2, 1])
    with s1:
        preset_st = st.selectbox("Asset:", POPULAR_INDIAN_STOCKS, index=0)
    with s2:
        custom_st = st.text_input("Custom Symbol:", placeholder="e.g. TRENT, BEL...")

    final_st = custom_st.strip().upper() if custom_st.strip() else preset_st
    components.html(f"<iframe src='https://s.tradingview.com/widgetembed/?frameElementId=tv_in&symbol=NSE:{final_st}&interval=15&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0c1017&theme=dark&style=1&timezone=Asia%2FKolkata&locale=en' style='width:100%; height:340px; border:none; border-radius:12px;'></iframe>", height=350)

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

    st.markdown("##### 📊 Active Equity Positions:")
    if st.session_state.positions_inr:
        for idx, pos in enumerate(st.session_state.positions_inr):
            gn = 1.4 * 5 if "BUY" in pos["type"] else -0.8 * 5
            amt = (pos["margin"] * gn) / 100
            colr = "#22c55e" if amt >= 0 else "#ef4444"
            st.markdown(f"<div class='pos-item'><div style='display:flex; justify-content:space-between; font-weight:bold;'><span>{pos['symbol']} ({pos['type']})</span><span style='color:{colr};'>{gn:+.1f}% (₹{amt:,.2f})</span></div><div style='color:#94a3b8; font-size:11px; margin-top:3px;'>Margin: ₹{pos['margin']:,.0f} | Exposure: ₹{pos.get('exposure', pos['margin']*5):,.0f}</div></div>", unsafe_allow_html=True)
            if st.button(f"✕ Square Off #{idx+1}", key=f"sq_eq_{idx}"):
                st.session_state.balance_inr += (pos["margin"] + amt)
                st.session_state.positions_inr.pop(idx)
                st.rerun()

# ==================== 3. 200X CRYPTO ====================
else:
    st.markdown("#### ⚡ 200x Crypto Futures (Binance Real-Time)")
    c_list = list(crypto_rates.keys()) or ["BTC", "ETH", "SOL", "BNB", "XRP"]
    c1, c2 = st.columns([1.2, 1])
    with c1:
        c_coin = st.selectbox("Asset:", c_list[:30], index=0)
    with c2:
        c_lev = st.selectbox("Leverage:", [2, 5, 10, 25, 50, 100, 150, 200], index=7)

    live_px = crypto_rates.get(c_coin, {"price": 82450.0})["price"]
    st.markdown(f"<div class='terminal-card'>1 {c_coin}: <b style='color:#38bdf8;'>${live_px:,.4f}</b> | Leverage: <b style='color:#facc15;'>{c_lev}x</b></div>", unsafe_allow_html=True)

    components.html(f"<iframe src='https://s.tradingview.com/widgetembed/?frameElementId=tv_cr&symbol=BINANCE:{c_coin}USDT&interval=60&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0c1017&theme=dark&style=1&timezone=Asia%2FKolkata&locale=en' style='width:100%; height:330px; border:none; border-radius:12px;'></iframe>", height=340)

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
            st.markdown(f"<div class='pos-item'><div style='display:flex; justify-content:space-between; font-weight:bold;'><span>{p['coin']} ({p['type']} {p['lev']}x)</span><span style='color:{clr};'>{pct:+.1f}% (${amt:,.2f})</span></div><div style='color:#94a3b8; font-size:11px; margin-top:3px;'>Margin: ${p['margin']} | Entry: ${p['entry']:,.2f}</div></div>", unsafe_allow_html=True)
            if st.button(f"✕ Close #{idx+1}", key=f"cr_cls_{idx}"):
                st.session_state.balance_usd += (p["margin"] + amt)
                st.session_state.positions_crypto.pop(idx)
                st.rerun()

# ==================== 4. AI NEWS DESK ====================
st.markdown("---")
st.markdown("#### 🎙️ AI Market News Desk (Voice & Intel)")

components.html("<div style='display:flex; justify-content:center; margin-bottom:10px;'><button onclick='recordQuery()' style='background:linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color:white; border:none; padding:8px 22px; border-radius:20px; font-weight:bold; cursor:pointer;'>🎤 Speak Command (e.g. 'Nifty options breakout news')</button></div><script>function recordQuery(){if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)){alert('Mic not supported');return;}var r=new(window.SpeechRecognition||window.webkitSpeechRecognition)();r.lang='en-US';r.onresult=function(e){var q=e.results[0][0].transcript;navigator.clipboard.writeText(q);alert('Heard: '+q+'\\nPaste in the box below');};r.start();}</script>", height=45)

news_query = st.text_input("News Query:", placeholder="Type 'Tell me market news' or ask about Nifty Option Chain...", key="news_field")

if st.button("⚡ Generate Intelligence", use_container_width=True) or (news_query and "news" in news_query.lower()):
    with st.spinner("Compiling F&O options data & global trends..."):
        try:
            intel_prompt = (
                "You are an elite quantitative F&O options trader and crypto derivative analyst. "
                "Provide a professional market brief in English covering: "
                "1. NIFTY 50 Option Chain OI max pain, PCR ratio and breakout levels, "
                "2. Indian equity sectoral momentum, "
                "3. Bitcoin & Ethereum leverage liquidations. "
                "Structure: 1 breaking headline summary line, followed by 3 bold concise bullet points. No URLs."
            )
            r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(intel_prompt)}", timeout=15)
            if r.status_code == 200 and r.text.strip():
                st.session_state.ai_news_intel = r.text.strip()
        except Exception:
            st.session_state.ai_news_intel = "Market intelligence service temporarily unavailable."

if st.session_state.ai_news_intel:
    st.markdown(f"<div class='terminal-card' style='border-left: 4px solid #38bdf8; font-size:13px; line-height:1.6;'>{st.session_state.ai_news_intel}</div>", unsafe_allow_html=True)
    clean_txt = st.session_state.ai_news_intel.replace("'", "").replace('"', '').replace('\n', ' ').replace('#', '').replace('*', '')[:350]
    components.html(f"<div style='display:flex; justify-content:flex-end;'><button onclick='speakBrief()' style='background:#1e293b; color:#38bdf8; border:1px solid #0284c7; padding:7px 16px; border-radius:18px; font-weight:bold; cursor:pointer;'>🔊 Listen to Brief (English)</button></div><script>function speakBrief(){{window.speechSynthesis.cancel();var u=new SpeechSynthesisUtteranc
