import streamlit as st
from modules.rag_pipeline import build_hybrid_rag

# Initialize RAG
rag, memory = build_hybrid_rag()
st.set_page_config(page_title="🌾 Agribot", page_icon="🌱", layout="wide")

# ------------------- Custom CSS -------------------
st.markdown("""
<style>
body {
    background-color: #000000;
    color: #FFFFFF;
}
h1, h2, h3 {
    color: #00FF7F;
}
div.block-container {
    padding: 2rem 4rem;
}
.card {
    background-color: #1C1C1C;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}
.stTextInput > div > input {
    background-color: #2A2A3F;
    color: white;
}
a {
    color: #FFD700;
}
.chat-user {
    background-color: #1A73E8;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}
.chat-bot-pdf {
    background-color: #00BFFF;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}
.chat-bot-web {
    background-color: #20B2AA;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🌾 Agribot")

# ------------------- Initialize chat history -------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------- Tabs -------------------
home_tab, chat_tab, about_tab, explore_tab = st.tabs(
    ["🏠 Home", "💬 Chatbot", "ℹ️ About", "🔍 Explore More"]
)

# ------------------- Home Tab -------------------
with home_tab:
    # First Rectangle: Welcome
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## Welcome to Agribot 🌱")
    st.markdown("""
    Agribot is your intelligent agriculture assistant.  
    Ask questions about government policies, schemes, and guidelines for farmers in India.  
    Get instant answers using PDFs and live web data, all in one place.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    # Second Rectangle: How We Help
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## How We Can Help Farmers")
    st.markdown("""
    - Find relevant agricultural policies for your crop and region  
    - Access government schemes and subsidies  
    - Get guidance on improving yield and crop management  
    - Explore additional resources from trusted agricultural portals  
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- Chatbot Tab -------------------
with chat_tab:
    user_input = st.text_input("Ask a question:")

    if st.button("Send") and user_input:
        answer = rag(user_input)
        st.session_state.chat_history.append({"user": user_input, "bot": answer})

    # Display chat history
    for chat in st.session_state.chat_history:
        st.markdown(f"<div class='chat-user'>🧑‍🌾 <b>{chat['user']}</b></div>", unsafe_allow_html=True)
        if "📌 From PDFs" in chat['bot']:
            st.markdown(f"<div class='chat-bot-pdf'>{chat['bot'].replace('📌 From PDFs:', '')}</div>", unsafe_allow_html=True)
        elif "📌 From Web" in chat['bot']:
            st.markdown(f"<div class='chat-bot-web'>{chat['bot'].replace('📌 From Web:', '')}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot-web'>{chat['bot']}</div>", unsafe_allow_html=True)

# ------------------- About Tab -------------------
with about_tab:
    st.markdown("### About Agribot")
    st.markdown("""
    - **Hybrid RAG:** Uses PDFs + live web search  
    - **LLM:** Google Gemini 1.5  
    - **Memory:** Tracks conversation for follow-ups  
    - **Frontend:** Streamlit web interface with dark-themed tabs
    """)

# ------------------- Explore More Tab -------------------
with explore_tab:
    st.markdown("### Explore More Resources")
    st.markdown("""
    - [AgriWelfare Portal](https://agriwelfare.gov.in/)  
    - [Kisan Schemes](https://agricoop.nic.in/en/schemes)  
    - [Vikaspedia Agriculture](https://vikaspedia.in/agriculture)  
    """)
