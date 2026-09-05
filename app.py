import streamlit as st
import wikipedia
import feedparser

st.set_page_config(page_title="Global Info & News Hub", layout="wide", page_icon="🌐")

st.title("🌐 ग्लोबल नॉलेज और न्यूज़ पोर्टल")
st.caption("विकिपीडिया • दुनिया भर की ताज़ा खबरें • जनरल नॉलेज")

tab1, tab2, tab3 = st.tabs(["📚 विकिपीडिया व ज्ञान", "🌍 दुनिया की खबरें", "🇮🇳 भारत की खबरें"])

with tab1:
    st.subheader("🔍 विकिपीडिया सर्च इंजन")
    query = st.text_input("कोई भी टॉपिक, देश, व्यक्ति या सवाल लिखें:", placeholder="उदा. Narendra Modi, India, Black Hole")
    lang = st.selectbox("भाषा चुनें:", ["hi (हिंदी)", "en (English)"])
    
    if st.button("सर्च करें"):
        if query.strip():
            wikipedia.set_lang(lang.split()[0])
            with st.spinner("जानकारी खोजी जा रही है..."):
                try:
                    summary = wikipedia.summary(query, sentences=6)
                    page = wikipedia.page(query)
                    
                    st.success(f"### {page.title}")
                    st.write(summary)
                    st.markdown("---")
                    st.write(f"🔗 **विस्तार से पढ़ें:** [{page.title}]({page.url})")
                except wikipedia.exceptions.DisambiguationError as e:
                    st.warning("इस नाम से कई विषय मिले। इनमें से कोई एक नाम लिखें:")
                    st.write(e.options[:8])
                except Exception:
                    st.error("जानकारी नहीं मिली। कृपया सही स्पेलिंग जांचें।")
        else:
            st.warning("कृपया कुछ नाम लिखकर सर्च करें।")

with tab2:
    st.subheader("🌍 दुनिया की ताज़ा खबरें (Global Headlines)")
    if st.button("विश्व समाचार लोड करें"):
        with st.spinner("ग्लोबल न्यूज़ लोड हो रही है..."):
            world_feed = feedparser.parse("https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en")
            for entry in world_feed.entries[:10]:
                st.markdown(f"#### [{entry.title}]({entry.link})")
                st.caption(f"समय: {entry.get('published', 'N/A')}")
                st.markdown("---")

with tab3:
    st.subheader("🇮🇳 भारत और ट्रेंडिंग हेडलाइंस")
    category = st.selectbox("कैटेगरी चुनें:", ["मुख्य खबरें", "बिजनेस", "टेक्नोलॉजी", "स्पोर्ट्स"])
    
    cat_urls = {
        "मुख्य खबरें": "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi",
        "बिजनेस": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=hi&gl=IN&ceid=IN:hi",
        "टेक्नोलॉजी": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=hi&gl=IN&ceid=IN:hi",
        "स्पोर्ट्स": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=hi&gl=IN&ceid=IN:hi"
    }
    
    if st.button("भारत की खबरें लोड करें"):
        with st.spinner("समाचार लोड हो रहे हैं..."):
            india_feed = feedparser.parse(cat_urls[category])
            for item in india_feed.entries[:10]:
                st.markdown(f"#### [{item.title}]({item.link})")
                st.caption(f"समय: {item.get('published', 'N/A')}")
                st.markdown("---")
              
