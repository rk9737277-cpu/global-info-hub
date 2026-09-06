import streamlit as st
import requests
import urllib.parse
import feedparser
import streamlit.components.v1 as components

# पेज सेटिंग
st.set_page_config(page_title="R", layout="centered", page_icon="🟡")

# सेशन स्टेट इनिशियलाइज़ेशन (सर्च और हिस्ट्री के लिए)
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# प्रीमियम गोल्डन स्टाइलिंग
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    div[data-baseweb="input"] {
        border-radius: 28px !important;
        background-color: #f8f9fa !important;
        border: 2px solid #FFD700 !important;
        padding: 4px 14px !important;
    }
    .user-bubble {
        background-color: #f1f3f4;
        padding: 10px 18px;
        border-radius: 20px;
        display: inline-block;
        float: right;
        margin-bottom: 15px;
        font-size: 16px;
        color: #1f1f1f;
        max-width: 85%;
        border-left: 4px solid #D4AF37;
    }
    .ai-answer-card {
        clear: both;
        background: #ffffff;
        border: 2px solid #FFD700;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.15);
        margin-top: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 1. गोल्डन R लोगो और ब्रांडिंग
header_html = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 5px; margin-bottom: 15px;">
    <div style="
        width: 75px; 
        height: 75px; 
        background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%); 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        border: 3px solid #FFD700;
        box-shadow: 0 4px 18px rgba(255, 175, 75, 0.45);
    ">
        <span style="font-size: 45px; font-weight: 900; color: #5B3900; font-family: sans-serif;">R</span>
    </div>
    <h1 style="
        margin: 8px 0 0 0; 
        font-size: 34px; 
        font-weight: 900; 
        background: linear-gradient(135deg, #D4AF37 0%, #AA771C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    ">R</h1>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# माइक (Voice Search)
voice_code = """
<div style="display: flex; justify-content: center; margin-bottom: 10px;">
    <button onclick="startVoice()" style="background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%); border: 1px solid #FFD700; border-radius: 20px; padding: 6px 16px; font-weight: bold; cursor: pointer; color: #5B3900; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
        🎤 बोलकर सर्च करें
    </button>
</div>
<script>
function startVoice() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("माइक सपोर्ट उपलब्ध नहीं है");
        return;
    }
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.onresult = function(event) {
        var text = event.results[0][0].transcript;
        navigator.clipboard.writeText(text);
        alert("आपने बोला: '" + text + "'\\nयह कॉपी हो गया है! नीचे सर्च बॉक्स में पेस्ट करके एंटर दबाएं।");
    };
    recognition.start();
}
</script>
"""
components.html(voice_code, height=45)

# सर्च इनपुट बॉक्स
search_input = st.text_input("सर्च", value=st.session_state.current_query, placeholder="Ask R / कुछ भी पूछें (उदा. भारत कब आज़ाद हुआ)...", label_visibility="collapsed")

if search_input != st.session_state.current_query:
    st.session_state.current_query = search_input

# --- यदि यूजर ने सवाल पूछा है (AI डायरेक्ट उत्तर + बोलकर सुनाने वाला स्पीकर) ---
if st.session_state.current_query.strip():
    q = st.session_state.current_query.strip()
    
    # सर्च हिस्ट्री में जोड़ें
    if q not in st.session_state.search_history:
        st.session_state.search_history.insert(0, q)
    
    st.markdown(f'<div class="user-bubble">{q}</div>', unsafe_allow_html=True)
    st.write("")

    with st.spinner("सीधा उत्तर तैयार हो रहा है..."):
        try:
            prompt = (
                "Give a direct, accurate answer in Hindi like Google AI Overview. "
                "Structure: Start with 1 bold sentence giving the core direct answer. "
                "Then provide 'मुख्य बिंदु' with 3 short bullet points. "
                "Do not include links or website URLs. "
                f"Question: {q}"
            )
            encoded = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded}"
            res = requests.get(url, timeout=15)
            
            if res.status_code == 200 and res.text.strip():
                answer_clean = res.text.strip()
                
                # AI उत्तर कार्ड
                st.markdown(f"""
                <div class="ai-answer-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: bold; color: #B8860B;">💡 सीधा जवाब</span>
                    </div>
                    <div>{answer_clean}</div>
                </div>
                """, unsafe_allow_html=True)

                # 2. टेक्स्ट-टू-स्पीच (🔊 बोलकर सुनाने वाला फ़ीचर)
                clean_speech = answer_clean.replace("'", "").replace('"', '').replace('\n', ' ').replace('#', '').replace('*', '')
                tts_code = f"""
                <button onclick="speakText()" style="background-color: #f1f3f4; border: 1px solid #ccc; border-radius: 20px; padding: 6px 14px; cursor: pointer; font-size: 14px; font-weight: bold;">
                    🔊 उत्तर सुनें (Listen)
                </button>
                <script>
                function speakText() {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance('{clean_speech[:250]}');
                    msg.lang = 'hi-IN';
                    window.speechSynthesis.speak(msg);
                }}
                </script>
                """
                components.html(tts_code, height=45)
            else:
                st.warning("जवाब नहीं मिल पाया। कृपया पुनः प्रयास करें।")
        except Exception:
            st.error("नेटवर्क समस्या। कृपया पुनः प्रयास करें।")

    if st.button("⬅️ वापस होम स्क्रीन पर जाएं"):
        st.session_state.current_query = ""
        st.rerun()

# --- यदि सर्च बार खाली है (होम स्क्रीन: ट्रेंडिंग, हिस्ट्री, सभी राज्य/जिले और ग्लोबल न्यूज़) ---
else:
    # 4. सर्च हिस्ट्री (अगर कोई पुरानी खोज है)
    if st.session_state.search_history:
        st.markdown("<p style='color: #888; font-size: 13px; margin-bottom: 4px;'>हालिया सर्च (History):</p>", unsafe_allow_html=True)
        h_cols = st.columns(min(len(st.session_state.search_history[:3]), 3))
        for idx, h_item in enumerate(st.session_state.search_history[:3]):
            if h_cols[idx].button(f"🕒 {h_item[:15]}...", key=f"hist_{idx}"):
                st.session_state.current_query = h_item
                st.rerun()
        st.markdown("---")

    # 1. ट्रेंडिंग सर्च (क्लिक करने पर तुरंत जवाब लोड होगा)
    st.markdown("<p style='color: #70757a; font-size: 14px; font-weight: bold; margin-bottom: 8px;'>🔥 ट्रेंडिंग सर्च (टैप करके सीधा जवाब पाएं):</p>", unsafe_allow_html=True)
    trending_list = [
        "भारत कब आज़ाद हुआ था पूरी जानकारी दें",
        "दही हांडी उत्सव मुंबई और पुणे के मुख्य अपडेट",
        "आज का मौसम और बारिश का तापमान",
        "LIC और ICICI बैंक पर ताज़ा जानकारी",
        "एशिया कप भारत पाकिस्तान मैच का हाल"
    ]
    for idx, trend in enumerate(trending_list):
        if st.button(f"↗ {trend}", key=f"trend_{idx}", use_container_width=True):
            st.session_state.current_query = trend
            st.rerun()

    st.markdown("---")

    # 3. राज्य, ज़िला और ग्लोबल न्यूज़ (हिंदी और इंग्लिश दोनों)
    st.markdown("### 📰 ताज़ा समाचार फ़ीड")
    
    # भाषा का चयन (हिंदी या English)
    news_lang = st.radio("समाचार भाषा (News Language):", ["हिन्दी (Hindi)", "English"], horizontal=True)
    hl = "hi" if "हिन्दी" in news_lang else "en"
    gl = "IN"

    tab_state, tab_india, tab_world = st.tabs(["📍 राज्य व ज़िला (All States & Districts)", "🇮🇳 राष्ट्रीय (India)", "🌍 इंटरनेशनल (Global)"])

    # भारत के सभी राज्य और केंद्र शासित प्रदेश
    all_states = [
        "बिहार (Bihar)", "उत्तर प्रदेश (Uttar Pradesh)", "महाराष्ट्र (Maharashtra)", "दिल्ली (Delhi)",
        "मध्य प्रदेश (Madhya Pradesh)", "राजस्थान (Rajasthan)", "पश्चिम बंगाल (West Bengal)", "गुजरात (Gujarat)",
        "हरियाणा (Haryana)", "पंजाब (Punjab)", "झारखंड (Jharkhand)", "उत्तराखंड (Uttarakhand)",
        "छत्तीसगढ़ (Chhattisgarh)", "तमिलनाडु (Tamil Nadu)", "कर्नाटक (Karnataka)", "केरल (Kerala)",
        "आंध्र प्रदेश (Andhra Pradesh)", "तेलंगाना (Telangana)", "ओडिशा (Odisha)", "असम (Assam)",
        "हिमाचल प्रदेश (Himachal Pradesh)", "जम्मू और कश्मीर (Jammu & Kashmir)", "गोवा (Goa)",
        "त्रिपुरा (Tripura)", "मणिपुर (Manipur)", "मेघालय (Meghalaya)", "नागालैंड (Nagaland)",
        "मिजोरम (Mizoram)", "सिक्किम (Sikkim)", "अरुणाचल प्रदेश (Arunachal Pradesh)"
    ]

    # टैब 1: राज्य और किसी भी जिले का चयन
    with tab_state:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            chosen_state = st.selectbox("राज्य चुनें (Select State):", all_states)
        with col_s2:
            chosen_district = st.text_input("अपना ज़िला / शहर लिखें:", placeholder="उदा. पटना, गया, लखनऊ, गोरखपुर, इंदौर...")

        state_name = chosen_state.split("(")[0].strip()
        final_loc = chosen_district.strip() if chosen_district.strip() else state_name
        
        with st.spinner(f"{final_loc} की खबरें लोड हो रही हैं..."):
            kw = f"{final_loc} news" if hl == "en" else f"{final_loc} समाचार"
            state_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(kw)}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
            s_feed = feedparser.parse(state_url)
            if s_feed.entries:
                for item in s_feed.entries[:6]:
                    st.markdown(f"**[{item.title}]({item.link})**")
                    st.caption(f"समय: {item.get('published', '')[:16]}")
                    st.markdown("---")
            else:
                st.info("कोई ताज़ा खबर नहीं मिली। कृपया ज़िले का नाम सही स्पेलिंग में लिखें।")

    # टैब 2: भारत की मुख्य खबरें
    with tab_india:
        india_url = f"https://news.google.com/rss?hl={hl}&gl={gl}&ceid={gl}:{hl}"
        i_feed = feedparser.parse(india_url)
        for item in i_feed.entries[:6]:
            st.markdown(f"**[{item.title}]({item.link})**")
            st.caption(f"समय: {item.get('published', '')[:16]}")
            st.markdown("---")

    # टैब 3: इंटरनेशनल / ग्लोबल खबरें
    with tab_world:
        world_hl = "en-US" if hl == "en" else "hi"
        world_gl = "US" if hl == "en" else "IN"
        world_url = f"https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl={world_hl}&gl={world_gl}&ceid={world_gl}:{world_hl}"
        w_feed = feedparser.parse(world_url)
        for item in w_feed.entries[:6]:
            st.markdown(f"**[{item.title}]({item.link})**")
            st.caption(f"समय: {item.get('published', '')[:16]}")
            st.markdown("---")
              
