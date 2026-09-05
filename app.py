import streamlit as st
import requests
import urllib.parse
import feedparser
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
    <p style="margin: 0; color: #888; font-size: 14px;">कोई भी सवाल पूछें • सीधा उत्तर पाएं</p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# माइक (Voice Search) बटन
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 15px;">
    <button onclick="startVoice()" style="background-color: #D4AF37; color: white; border: none; padding: 10px 24px; border-radius: 25px; font-size: 15px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
        🎤 बोलकर पूछें
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
        alert("आपने बोला: '" + text + "'\\n\\nयह कॉपी हो गया है! नीचे बॉक्स में पेस्ट करके एंटर दबाएं।");
    };

    recognition.onerror = function(event) {
        status.innerText = "माइक एरर: " + event.error;
    };

    recognition.start();
}
</script>
"""
components.html(voice_html, height=65)

# मुख्य सवाल पूछने का बॉक्स
user_query = st.text_input("सर्च बॉक्स", placeholder="यहाँ कोई भी सवाल लिखें या बोलकर पेस्ट करें (उदा. भारत कब आजाद हुआ, बिहार की राजधानी क्या है)...", label_visibility="collapsed")

st.markdown("---")

# अगर यूजर ने कोई सवाल पूछा है
if user_query.strip():
    with st.spinner("उत्तर तैयार किया जा रहा है..."):
        try:
            # सीधे सादे शब्दों में उत्तर देने के लिए AI API
            prompt = f"उत्तर सीधा, सरल और हिंदी में दें। कोई लिंक या वेबसाइट का नाम मत दें। सवाल: {user_query}"
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded_prompt}"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200 and response.text.strip():
                answer_text = response.text.strip()
                
                # सुंदर गोल्डन हाइलाइट कार्ड में सीधा जवाब
                st.markdown(f"""
                <div style="
                    background: #ffffff;
                    border: 2px solid #FFD700;
                    border-radius: 12px;
                    padding: 22px;
                    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
                    margin-bottom: 25px;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                        <span style="font-size: 24px;">💡</span>
                        <h3 style="margin: 0; color: #5B3900; font-size: 20px;">सीधा जवाब:</h3>
                    </div>
                    <p style="font-size: 19px; color: #1a1a1a; line-height: 1.6; margin: 0; font-weight: 500;">
                        {answer_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("जवाब नहीं मिल पाया। कृपया दोबारा प्रयास करें।")
        except Exception:
            st.error("जवाब लाने में समस्या आई। कृपया थोड़ी देर बाद प्रयास करें।")

# अगर बॉक्स खाली है, तब नीचे आज की ताज़ा खबरें दिखेंगी
else:
    st.subheader("📰 आज की ताज़ा खबरें")

    tab_state, tab_india, tab_world = st.tabs(["📍 राज्य / स्थानीय समाचार", "🇮🇳 भारत की खबरें", "🌍 दुनिया की खबरें"])

    with tab_state:
        st.markdown("#### अपने राज्य या शहर की खबर चुनें")
        col_st1, col_st2 = st.columns([1, 1])
        with col_st1:
            selected_state = st.selectbox(
                "राज्य चुनें:",
                ["बिहार (Bihar)", "उत्तर प्रदेश (UP)", "दिल्ली (Delhi)", "महाराष्ट्र (Maharashtra)", "राजस्थान (Rajasthan)", "मध्य प्रदेश (MP)", "झारखंड (Jharkhand)", "अन्य"]
            )
        with col_st2:
            custom_city = st.text_input("या शहर/ज़िला लिखें:", placeholder="उदा. Patna, Lucknow, Gaya")

        target_location = custom_city.strip() if custom_city.strip() else selected_state.split()[0]

        with st.spinner(f"{target_location} की खबरें लोड हो रही हैं..."):
            encoded_query = urllib.parse.quote(f"{target_location} news hindi")
            state_feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded_query}&hl=hi&gl=IN&ceid=IN:hi")
            if state_feed.entries:
                for item in state_feed.entries[:6]:
                    st.markdown(f"**[{item.title}]({item.link})**")
                    st.caption(f"समय: {item.get('published', '')[:16]}")
                    st.markdown("---")

    with tab_india:
        st.markdown("#### 🇮🇳 राष्ट्रीय टॉप हेडलाइंस")
        india_feed = feedparser.parse("https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi")
        for item in india_feed.entries[:6]:
            st.markdown(f"**[{item.title}]({item.link})**")
            st.caption(f"समय: {item.get('published', '')[:16]}")
            st.markdown("---")

    with tab_world:
        st.markdown("#### 🌍 अंतरराष्ट्रीय टॉप हेडलाइंस")
        world_feed = feedparser.parse("https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en")
        for item in world_feed.entries[:6]:
            st.markdown(f"**[{item.title}]({item.link})**")
            st.caption(f"समय: {item.get('published', '')[:16]}")
            st.markdown("---")
      
