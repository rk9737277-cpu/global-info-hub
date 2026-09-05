import streamlit as st
from duckduckgo_search import DDGS
import feedparser
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="R", layout="wide", page_icon="🟡")

# गोल्डन R लोगो और नाम
header_html = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 10px; margin-bottom: 20px;">
    <div style="
        width: 80px; 
        height: 80px; 
        background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%); 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        box-shadow: 0 4px 18px rgba(255, 175, 75, 0.45);
        border: 3px solid #FFD700;
    ">
        <span style="font-size: 48px; font-weight: 900; color: #5B3900; font-family: sans-serif;">R</span>
    </div>
    <h1 style="
        margin: 10px 0 0 0; 
        font-size: 38px; 
        font-weight: 900; 
        background: linear-gradient(135deg, #D4AF37 0%, #AA771C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    ">R</h1>
    <p style="margin: 0; color: #888; font-size: 14px;">Smart Search • National, State & Global News</p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# माइक (Voice Search) बटन
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 15px;">
    <button onclick="startVoice()" style="background-color: #D4AF37; color: white; border: none; padding: 10px 24px; border-radius: 25px; font-size: 15px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
        🎤 बोलकर सर्च करें
    </button>
    <span id="voice_status" style="font-size: 14px; color: #555;"></span>
</div>

<script>
function startVoice() {
    var status = document.getElementById('voice_status');
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        status.innerText = "माइक सपोर्ट नहीं कर रहा।";
        return;
    }
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.interimResults = false;

    recognition.onstart = function() {
        status.innerText = "सुन रहा हूँ... बोलिए!";
    };

    recognition.onresult = function(event) {
        var text = event.results[0][0].transcript;
        status.innerText = "सुना: " + text;
        navigator.clipboard.writeText(text);
        alert("आपने बोला: '" + text + "'\\n\\nयह कॉपी हो गया है! नीचे सर्च बॉक्स में पेस्ट करके सर्च दबाएं।");
    };

    recognition.onerror = function(event) {
        status.innerText = "माइक एरर: " + event.error;
    };

    recognition.start();
}
</script>
"""
components.html(voice_html, height=65)

# मुख्य सर्च बार
search_query = st.text_input("सर्च बॉक्स", placeholder="Google की तरह कुछ भी खोजें...", label_visibility="collapsed")

st.markdown("---")

# अगर यूजर ने सर्च किया है तो वेब सर्च परिणाम दिखाएं
if search_query.strip():
    st.subheader(f"🔍 '{search_query}' के परिणाम")
    with st.spinner("जानकारी खोजी जा रही है..."):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=6))
                if results:
                    for r in results:
                        st.markdown(f"#### [{r['title']}]({r['href']})")
                        st.write(r['body'])
                        st.markdown("---")
                else:
                    st.warning("कोई परिणाम नहीं मिला। कृपया अलग शब्दों में सर्च करें।")
        except Exception:
            st.error("सर्च करने में समस्या आई, कृपया दोबारा प्रयास करें।")

# अगर सर्च बार खाली है, तो न्यूज़ फ़ीड दिखाएं
else:
    st.subheader("📰 आज की ताज़ा खबरें")

    tab_state, tab_india, tab_world = st.tabs(["📍 राज्य / स्थानीय समाचार", "🇮🇳 भारत की खबरें", "🌍 दुनिया की खबरें"])

    # 1. राज्य / लोकल खबरें टैब
    with tab_state:
        st.markdown("#### अपने राज्य या शहर की खबर चुनें")
        
        col_st1, col_st2 = st.columns([1, 1])
        with col_st1:
            selected_state = st.selectbox(
                "राज्य चुनें:",
                ["बिहार (Bihar)", "उत्तर प्रदेश (UP)", "दिल्ली (Delhi)", "महाराष्ट्र (Maharashtra)", "राजस्थान (Rajasthan)", "मध्य प्रदेश (MP)", "झारखंड (Jharkhand)", "अन्य (अपना शहर लिखें)"]
            )
        
        with col_st2:
            custom_city = st.text_input("या किसी भी शहर/जिले का नाम लिखें:", placeholder="उदा. Patna, Lucknow, Gaya, Indore")

        if custom_city.strip():
            target_location = custom_city.strip()
        else:
            target_location = selected_state.split()[0]

        with st.spinner(f"{target_location} की ताज़ा खबरें लोड हो रही हैं..."):
            encoded_query = urllib.parse.quote(f"{target_location} news hindi")
            state_feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=hi&gl=IN&ceid=IN:hi"
            state_feed = feedparser.parse(state_feed_url)
            
            if state_feed.entries:
                for item in state_feed.entries[:8]:
                    st.markdown(f"**[{item.title}]({item.link})**")
                    st.caption(f"समय: {item.get('published', '')[:16]}")
                    st.markdown("---")
            else:
                st.info(f"{target_location} से जुड़ी कोई ताज़ा खबर नहीं मिली। कृपया कोई बड़ा शहर या ज़िला लिखकर देखें।")

    # 2. भारत की राष्ट्रीय खबरें टैब
    with tab_india:
        st.markdown("#### 🇮🇳 राष्ट्रीय टॉप हेडलाइंस")
        india_feed = feedparser.parse("https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi")
        for item in india_feed.entries[:8]:
            st.markdown(f"**[{item.title}]({item.link})**")
            st.caption(f"समय: {item.get('published', '')[:16]}")
            st.markdown("---")

    # 3. दुनिया की खबरें टैब
    with tab_world:
        st.markdown("#### 🌍 अंतरराष्ट्रीय टॉप हेडलाइंस")
        world_feed = feedparser.parse("https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en")
        for item in world_feed.entries[:8]:
            st.markdown(f"**[{item.title}]({item.link})**")
            st.caption(f"समय: {item.get('published', '')[:16]}")
            st.markdown("---")
