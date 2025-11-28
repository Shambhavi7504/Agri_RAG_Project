"""
AgriRAG - Agriculture Intelligence System with Multilingual Support
Streamlit Frontend Application
"""

import streamlit as st
from modules.rag_pipeline import build_hybrid_rag
from modules.query_router import route_query
from modules.neo4j_connection import test_neo4j_connection, get_database_stats
from modules.multilingual import get_multilingual_support
import time

# Try to import voice modules
try:
    from audio_recorder_streamlit import audio_recorder
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    audio_recorder = None

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="AgriRAG - Agricultural Intelligence System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --dark-bg: #0e1117;
        --card-bg: #1e2130;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: #ecf0f1;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #1e2130 0%, #2a2d3e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2563eb;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
    }
    
    .feature-card h3 {
        color: #60a5fa;
        margin-bottom: 0.5rem;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        line-height: 1.6;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #e2e8f0;
        border-left: 4px solid #60a5fa;
        line-height: 1.6;
    }
    
    .kg-message {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        line-height: 1.6;
    }
    
    /* Language selector */
    .language-badge {
        background: #2ecc71;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem;
        font-weight: 600;
    }
    
    /* Simple mode button */
    .big-button {
        font-size: 1.5rem !important;
        padding: 1.5rem !important;
        margin: 0.5rem !important;
    }
    
    /* Stats box */
    .stat-box {
        background: linear-gradient(135deg, #1e2130 0%, #2a2d3e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #2ecc71;
    }
    
    .stat-box h2 {
        color: #2ecc71;
        font-size: 2.5rem;
        margin: 0;
    }
    
    .stat-box p {
        color: #bdc3c7;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'rag_initialized' not in st.session_state:
        st.session_state.rag_initialized = False
        st.session_state.rag_function = None
        st.session_state.memory = None
        st.session_state.kg_available = False
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = 'en'
    
    if 'simple_mode' not in st.session_state:
        st.session_state.simple_mode = False
    
    if 'multilingual' not in st.session_state:
        st.session_state.multilingual = get_multilingual_support()


def home_page():
    """Home page with introduction and features"""
    
    ml = st.session_state.multilingual
    lang = st.session_state.selected_language
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌾 AgriRAG</h1>
        <p>Agricultural Intelligence System powered by AI, Knowledge Graphs & RAG</p>
        <p>🌐 Multilingual Support: Hindi, Kannada, Telugu, Tamil, Bengali, Marathi, Punjabi & More</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    st.markdown("### 🌍 Select Your Language / अपनी भाषा चुनें")
    
    col1, col2, col3, col4 = st.columns(4)
    
    languages_display = [
        ('en', 'English'),
        ('hi', 'हिंदी'),
        ('kn', 'ಕನ್ನಡ'),
        ('te', 'తెలుగు'),
        ('ta', 'தமிழ்'),
        ('bn', 'বাংলা'),
        ('mr', 'मराठी'),
        ('pa', 'ਪੰਜਾਬੀ'),
    ]
    
    for idx, (code, name) in enumerate(languages_display):
        col = [col1, col2, col3, col4][idx % 4]
        with col:
            if st.button(f"{name}", key=f"lang_{code}", use_container_width=True):
                st.session_state.selected_language = code
                st.rerun()
    
    st.markdown("---")
    
    # Simple mode toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📱 Interface Mode")
    with col2:
        simple_mode = st.toggle("Simple Mode (For Low Literacy)", value=st.session_state.simple_mode)
        if simple_mode != st.session_state.simple_mode:
            st.session_state.simple_mode = simple_mode
            st.rerun()
    
    st.markdown("---")
    
    # Introduction
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🚀 Welcome to AgriRAG")
        st.markdown("""
        AgriRAG is an advanced agricultural intelligence system that combines:
        
        - **🤖 AI-Powered Chat**: Get instant answers in your language
        - **🎤 Voice Support**: Speak your questions, hear responses
        - **📚 Document Retrieval**: Search agricultural documents
        - **🌐 Web Integration**: Real-time market information
        - **🔗 Knowledge Graph**: 100+ crops, 15+ schemes, 20+ policies
        - **🌍 12+ Languages**: Support for major Indian languages
        
        Start exploring by visiting the **Chatbot** tab!
        """)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&h=300&fit=crop", 
                use_container_width=True)
    
    st.markdown("---")
    
    # Supported Languages
    st.markdown("## 🌐 Supported Languages")
    
    for code, name in ml.LANGUAGES.items():
        st.markdown(f'<span class="language-badge">{name}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎤 Voice Support</h3>
            <p>Speak in your language, get voice responses. Perfect for farmers with low literacy.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🌍 Multilingual</h3>
            <p>Ask questions in Hindi, Kannada, Telugu, Tamil, and 8 more Indian languages.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🔗 Knowledge Graph</h3>
            <p>Explore connections between crops, schemes, policies, and subsidies.</p>
        </div>
        """, unsafe_allow_html=True)


def simple_chatbot_page():
    """Simplified chatbot page for low literacy users"""
    
    ml = st.session_state.multilingual
    lang = st.session_state.selected_language
    prompts = ml.get_simple_prompts(lang)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>💬 AgriRAG</h1>
        <p>{prompts['ask_question']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize RAG
    if not st.session_state.rag_initialized:
        with st.spinner(prompts['loading']):
            try:
                rag_function, memory = build_hybrid_rag()
                st.session_state.rag_function = rag_function
                st.session_state.memory = memory
                st.session_state.rag_initialized = True
                
                if test_neo4j_connection():
                    st.session_state.kg_available = True
                
                st.success("✅")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")
                return
    
    # Example questions (big buttons)
    st.markdown(f"### {prompts['examples_title']}")
    
    examples = ml.get_example_questions(lang)
    
    for example in examples:
        if st.button(f"📌 {example}", key=example, use_container_width=True):
            st.session_state.current_query = example
            st.rerun()
    
    st.markdown("---")
    
    # Voice input (simplified)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button(f"{prompts['speak_button']}", use_container_width=True, type="primary"):
            st.info("🎤 Speak now...")
            # Voice recognition would go here
    
    with col2:
        if st.button(f"{prompts['clear_button']}", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display last 3 messages only (simplified)
    st.markdown("---")
    for message in st.session_state.chat_history[-3:]:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                <strong>👤:</strong><br>{message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <strong>🤖:</strong><br>{message['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Add listen button
            if st.button(f"{prompts['listen_button']}", key=f"listen_{len(st.session_state.chat_history)}"):
                try:
                    audio_file = ml.text_to_speech(message['content'], lang=lang, slow=True)
                    if audio_file:
                        with open(audio_file, 'rb') as f:
                            st.audio(f.read(), format='audio/mp3')
                except Exception as e:
                    st.error(f"Audio error: {e}")


def chatbot_page():
    """Interactive chatbot page with full features"""
    
    ml = st.session_state.multilingual
    lang = st.session_state.selected_language
    prompts = ml.get_simple_prompts(lang)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>💬 AgriRAG Chatbot</h1>
        <p>{prompts['ask_question']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize RAG system
    if not st.session_state.rag_initialized:
        with st.spinner(prompts['loading']):
            try:
                rag_function, memory = build_hybrid_rag()
                st.session_state.rag_function = rag_function
                st.session_state.memory = memory
                st.session_state.rag_initialized = True
                
                if test_neo4j_connection():
                    st.session_state.kg_available = True
                
                st.success("✅ AgriRAG system ready!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🌍 Language / भाषा")
        
        lang_options = {code: name for code, name in ml.LANGUAGES.items()}
        selected_lang = st.selectbox(
            "Select Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(lang),
            label_visibility="collapsed"
        )
        
        if selected_lang != lang:
            st.session_state.selected_language = selected_lang
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 🔧 System Status")
        st.success("✅ RAG Pipeline Active")
        
        if st.session_state.kg_available:
            st.success("✅ Knowledge Graph Connected")
            try:
                stats = get_database_stats()
                st.info(f"📊 Nodes: {stats.get('total_nodes', 0)}")
                st.info(f"🔗 Relations: {stats.get('total_relationships', 0)}")
            except:
                pass
        else:
            st.warning("⚠️ Knowledge Graph Offline")
        
        st.markdown("---")
        
        st.markdown(f"### {prompts['examples_title']}")
        examples = ml.get_example_questions(lang)
        
        for example in examples:
            if st.button(f"📌 {example[:40]}...", key=f"ex_{example}"):
                st.session_state.current_query = example
                st.rerun()
        
        st.markdown("---")
        
        if st.button(f"🗑️ {prompts['clear_button']}"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Chat display
    chat_container = st.container()
    
    with chat_container:
        for idx, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                css_class = "kg-message" if "🔗" in message['content'] else "bot-message"
                
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>🤖 AgriRAG:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # Add audio button
                col1, col2 = st.columns([5, 1])
                with col2:
                    if st.button(f"🔊", key=f"audio_{idx}"):
                        try:
                            audio_file = ml.text_to_speech(message['content'], lang=lang, slow=False)
                            if audio_file:
                                with open(audio_file, 'rb') as f:
                                    st.audio(f.read(), format='audio/mp3')
                        except Exception as e:
                            st.error(f"Audio error: {e}")
    
    # Input area
    st.markdown("---")
    
    st.info("💡 **Tip**: Use your browser's voice typing feature! Most phones have a 🎤 icon on the keyboard.")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_query = st.text_input(
            prompts['ask_question'],
            placeholder=examples[0] if examples else "",
            key="user_input",
            label_visibility="collapsed",
            help="Tap the microphone icon on your phone's keyboard to speak!"
        )
    
    with col2:
        send_button = st.button(f"{prompts['send_button']} 🚀", use_container_width=True)
    
    # Handle query from sidebar example or user input
    if 'current_query' in st.session_state:
        user_query = st.session_state.current_query
        del st.session_state.current_query
        send_button = True
    
    if send_button and user_query:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })
        
        with st.spinner(prompts['thinking']):
            try:
                # Translate query to English
                english_query = ml.translate_text(user_query, source_lang=lang, target_lang='en')
                
                # Get response
                if st.session_state.kg_available:
                    english_response = route_query(english_query, st.session_state.rag_function, use_kg=True)
                else:
                    english_response = st.session_state.rag_function(english_query)
                
                # Translate response back
                translated_response = ml.translate_text(english_response, source_lang='en', target_lang=lang)
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': translated_response
                })
                
            except Exception as e:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"❌ Error: {str(e)}"
                })
        
        st.rerun()


def about_page():
    """About page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>ℹ️ About AgriRAG</h1>
        <p>Agricultural Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🌾 AgriRAG - Empowering Indian Farmers")
    
    st.markdown("""
    AgriRAG is designed specifically for Indian farmers, including those in rural and backward regions 
    with low literacy rates. Our system provides:
    
    ### 🌍 Multilingual Support
    - **12+ Indian Languages**: Hindi, Kannada, Telugu, Tamil, Bengali, Marathi, Punjabi, Gujarati, Malayalam, Odia, Urdu, and English
    - **Voice Input/Output**: Speak your questions, hear responses
    - **Simple Mode**: Streamlined interface for low literacy users
    
    ### 🤖 AI-Powered Intelligence
    - **100+ Commodities**: Comprehensive crop database with pricing
    - **15+ Government Schemes**: PM-KISAN, PMFBY, and more
    - **20+ Policies & Subsidies**: Complete policy information
    - **Real-time Data**: Market prices, weather, news
    
    ### 📱 Accessible Design
    - **Mobile-Friendly**: Works on any device
    - **Low-Bandwidth**: Optimized for rural internet
    - **Icon-Based Navigation**: Easy to understand
    - **Voice-First**: No typing required
    
    ### 🎯 Built For Farmers
    AgriRAG addresses the unique challenges faced by Indian farmers:
    - Language barriers
    - Low digital literacy
    - Limited internet access
    - Need for quick, accurate information
    - Complex government schemes
    
    **Start using AgriRAG today and empower your farming decisions!**
    """)


def main():
    """Main application"""
    
    initialize_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=200&h=100&fit=crop", 
                use_container_width=True)
        st.markdown("# 🌾 AgriRAG")
        st.markdown("---")
        
        page = st.radio(
            "Navigate",
            ["🏠 Home", "💬 Chatbot", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Simple mode toggle in sidebar
        simple_mode = st.checkbox("📱 Simple Mode", value=st.session_state.simple_mode)
        if simple_mode != st.session_state.simple_mode:
            st.session_state.simple_mode = simple_mode
            st.rerun()
    
    # Route to appropriate page
    if page == "🏠 Home":
        home_page()
    elif page == "💬 Chatbot":
        if st.session_state.simple_mode:
            simple_chatbot_page()
        else:
            chatbot_page()
    elif page == "ℹ️ About":
        about_page()


if __name__ == "__main__":
    main()