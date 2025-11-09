"""
AgriRAG - Agriculture Intelligence System
Streamlit Frontend Application
"""

import streamlit as st
from modules.rag_pipeline import build_hybrid_rag
from modules.query_router import route_query
from modules.neo4j_connection import test_neo4j_connection, get_database_stats
import time

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
        --primary-green: #2ecc71;
        --dark-bg: #0e1117;
        --card-bg: #1e2130;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
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
        border-left: 4px solid #2ecc71;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(46, 204, 113, 0.3);
    }
    
    .feature-card h3 {
        color: #2ecc71;
        margin-bottom: 0.5rem;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    
    .kg-message {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
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
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(46, 204, 113, 0.5);
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


def home_page():
    """Home page with introduction and features"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌾 AgriRAG</h1>
        <p>Agricultural Intelligence System powered by AI, Knowledge Graphs & RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Introduction
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🚀 Welcome to AgriRAG")
        st.markdown("""
        AgriRAG is an advanced agricultural intelligence system that combines:
        
        - **🤖 AI-Powered Chat**: Get instant answers to your agriculture queries
        - **📚 Document Retrieval**: Search through comprehensive agricultural documents
        - **🌐 Web Integration**: Access real-time information from the internet
        - **🔗 Knowledge Graph**: Explore structured relationships between crops, schemes, and policies
        - **💡 Smart Routing**: Intelligent query routing for optimal responses
        
        Start exploring by visiting the **Chatbot** tab!
        """)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&h=300&fit=crop", 
                use_container_width=True)
    
    st.markdown("---")
    
    # Features
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📖 Document Search</h3>
            <p>Search through thousands of agricultural documents, research papers, and policy documents instantly.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔗 Knowledge Graph</h3>
            <p>Explore connections between 100+ commodities, government schemes, policies, and subsidies.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🌐 Real-time Web Data</h3>
            <p>Get the latest market prices, weather updates, and agricultural news from verified sources.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Statistics
    st.markdown("## 📊 System Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <h2>100+</h2>
            <p>Commodities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <h2>15+</h2>
            <p>Govt Schemes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <h2>20+</h2>
            <p>Policies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-box">
            <h2>24/7</h2>
            <p>Available</p>
        </div>
        """, unsafe_allow_html=True)


def chatbot_page():
    """Interactive chatbot page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>💬 AgriRAG Chatbot</h1>
        <p>Ask anything about agriculture, crops, schemes, and policies</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize RAG system
    if not st.session_state.rag_initialized:
        with st.spinner("🔧 Initializing AgriRAG system..."):
            try:
                rag_function, memory = build_hybrid_rag()
                st.session_state.rag_function = rag_function
                st.session_state.memory = memory
                st.session_state.rag_initialized = True
                
                # Check KG availability
                if test_neo4j_connection():
                    st.session_state.kg_available = True
                
                st.success("✅ AgriRAG system ready!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error initializing system: {e}")
                return
    
    # Sidebar with system status
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        
        st.markdown("**Components:**")
        st.success("✅ RAG Pipeline Active")
        
        if st.session_state.kg_available:
            st.success("✅ Knowledge Graph Connected")
            
            # Show KG stats
            try:
                stats = get_database_stats()
                st.info(f"📊 KG Nodes: {stats.get('total_nodes', 0)}")
                st.info(f"🔗 KG Relations: {stats.get('total_relationships', 0)}")
            except:
                pass
        else:
            st.warning("⚠️ Knowledge Graph Offline")
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        
        example_queries = [
            "What schemes are available for wheat farmers?",
            "Tell me about PM-KISAN eligibility",
            "How to grow rice organically?",
            "What is the price of cotton?",
            "Which subsidies are available in Punjab?"
        ]
        
        for query in example_queries:
            if st.button(f"📌 {query[:30]}...", key=query):
                st.session_state.current_query = query
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Chat interface
    st.markdown("### 💬 Conversation")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Detect message type
                if "🔗 Knowledge Graph" in message['content']:
                    css_class = "kg-message"
                    icon = "🤖"
                else:
                    css_class = "bot-message"
                    icon = "🤖"
                
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>{icon} AgriRAG:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_query = st.text_input(
            "Ask your question:",
            placeholder="E.g., What schemes are available for rice farmers?",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 🚀", use_container_width=True)
    
    # Handle query from sidebar example
    if 'current_query' in st.session_state:
        user_query = st.session_state.current_query
        del st.session_state.current_query
        send_button = True
    
    # Process query
    if send_button and user_query:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })
        
        # Get response
        with st.spinner("🤔 Thinking..."):
            try:
                if st.session_state.kg_available:
                    response = route_query(
                        user_query, 
                        st.session_state.rag_function,
                        use_kg=True
                    )
                else:
                    response = st.session_state.rag_function(user_query)
                
                # Add bot response
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
            except Exception as e:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"❌ Error: {str(e)}"
                })
        
        st.rerun()


def about_page():
    """About page with system information"""
    
    st.markdown("""
    <div class="main-header">
        <h1>ℹ️ About AgriRAG</h1>
        <p>Learn more about our agricultural intelligence system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # What is AgriRAG
    st.markdown("## 🌾 What is AgriRAG?")
    st.markdown("""
    AgriRAG (Agricultural Retrieval-Augmented Generation) is a cutting-edge AI system designed to 
    revolutionize how farmers, policymakers, and agricultural stakeholders access information.
    
    By combining multiple AI technologies, AgriRAG provides accurate, contextual, and up-to-date 
    information about crops, government schemes, market prices, and agricultural best practices.
    """)
    
    st.markdown("---")
    
    # Technology Stack
    st.markdown("## 🔧 Technology Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Backend Technologies
        - **🤖 Google Gemini**: Advanced language model for natural responses
        - **📚 LangChain**: Framework for building RAG pipelines
        - **🔗 Neo4j**: Graph database for knowledge representation
        - **🔍 FAISS**: Vector similarity search for documents
        - **🌐 SerpAPI**: Real-time web search integration
        """)
    
    with col2:
        st.markdown("""
        ### AI Components
        - **Retrieval-Augmented Generation (RAG)**: Combines retrieval with generation
        - **Knowledge Graph**: Structured relationships between entities
        - **Semantic Search**: HuggingFace embeddings for context understanding
        - **Query Routing**: Intelligent routing to appropriate data sources
        """)
    
    st.markdown("---")
    
    # Features in detail
    st.markdown("## ✨ Features in Detail")
    
    with st.expander("📖 Document Retrieval"):
        st.markdown("""
        - Search through agricultural PDFs, research papers, and policy documents
        - Semantic search using state-of-the-art embeddings
        - Context-aware responses based on relevant document chunks
        - Support for multiple file formats
        """)
    
    with st.expander("🔗 Knowledge Graph"):
        st.markdown("""
        - 100+ commodities with pricing and market data
        - 15+ government schemes (PM-KISAN, PMFBY, etc.)
        - 20+ policies and subsidies
        - Complex relationship queries (e.g., "Which schemes cover wheat in Punjab?")
        """)
    
    with st.expander("🌐 Web Search Integration"):
        st.markdown("""
        - Real-time market prices and news
        - Weather updates and forecasts
        - Latest policy announcements
        - Verified sources only
        """)
    
    with st.expander("💡 Intelligent Query Routing"):
        st.markdown("""
        - Automatically detects query type (factual, relational, procedural)
        - Routes to appropriate data source (KG, documents, or web)
        - Combines multiple sources for comprehensive answers
        - Natural language understanding
        """)
    
    st.markdown("---")
    
    # Use Cases
    st.markdown("## 🎯 Use Cases")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 👨‍🌾 For Farmers
        - Find eligible schemes
        - Get crop recommendations
        - Market price information
        - Best practices guidance
        """)
    
    with col2:
        st.markdown("""
        ### 🏛️ For Policymakers
        - Scheme coverage analysis
        - Policy impact assessment
        - Crop-wise subsidy data
        - Regional insights
        """)
    
    with col3:
        st.markdown("""
        ### 📊 For Researchers
        - Agricultural data access
        - Trend analysis
        - Policy research
        - Market studies
        """)
    
    st.markdown("---")
    
    # Credits
    st.markdown("## 👥 Team")
    st.markdown("""
    AgriRAG is developed as part of an agricultural technology initiative to democratize 
    access to agricultural information and support data-driven farming decisions.
    
    **Technologies Used:**
    - Google Gemini 1.5 Flash
    - LangChain v0.2+
    - Neo4j 5.x
    - Streamlit
    - HuggingFace Transformers
    """)


def main():
    """Main application"""
    
    # Initialize session state
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
        st.markdown("### 📞 Support")
        st.markdown("Need help? Contact us!")
        st.markdown("📧 support@agrirag.com")
    
    # Route to appropriate page
    if page == "🏠 Home":
        home_page()
    elif page == "💬 Chatbot":
        chatbot_page()
    elif page == "ℹ️ About":
        about_page()


if __name__ == "__main__":
    main()