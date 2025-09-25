"""
Streamlit web interface for the chatbot with web scraping capabilities.
This is the main entry point for the application.
"""

import streamlit as st
import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

# Import our custom modules
import sys
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from web_scraper import WebScraper, ScrapedPage
    from vector_database import VectorDatabase
    from chatbot import ChatBot, ResponseFormatter
except ImportError as e:
    st.error(f"Erreur d'importation des modules: {e}")
    st.stop()

try:
    from config.settings import PAGE_TITLE, PAGE_ICON, SCRAPED_DATA_DIR
except ImportError as e:
    # Fallback values if config import fails
    PAGE_TITLE = "Chatbot Web Scraper"
    PAGE_ICON = "🤖"
    SCRAPED_DATA_DIR = Path(__file__).parent / "data" / "scraped"
    SCRAPED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
    }
    
    .bot-message {
        background-color: #e8f4f8;
        border-left-color: #764ba2;
    }
    
    .source-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = None
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_sources' not in st.session_state:
        st.session_state.current_sources = []

def load_scraped_data() -> List[Dict]:
    """Load previously scraped data from files."""
    scraped_files = []
    if SCRAPED_DATA_DIR.exists():
        for file_path in SCRAPED_DATA_DIR.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    scraped_files.extend(data)
            except Exception as e:
                st.warning(f"Erreur lors du chargement de {file_path.name}: {e}")
    return scraped_files

def initialize_components():
    """Initialize chatbot and vector database components."""
    try:
        # Initialize vector database
        if st.session_state.vector_db is None:
            with st.spinner("Initialisation de la base de données vectorielle..."):
                st.session_state.vector_db = VectorDatabase("chroma")
        
        # Initialize chatbot
        if st.session_state.chatbot is None:
            with st.spinner("Initialisation du chatbot..."):
                st.session_state.chatbot = ChatBot()
        
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        return False

def scrape_website(url: str, max_pages: int, use_selenium: bool = False) -> List[ScrapedPage]:
    """Scrape a website and return the results."""
    try:
        scraper = WebScraper(use_selenium=use_selenium)
        
        with st.spinner(f"Scraping du site {url}... (max {max_pages} pages)"):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # This is a simplified progress simulation
            # In a real implementation, you might want to use callbacks or threading
            pages = scraper.scrape_website(url, max_pages)
            
            progress_bar.progress(100)
            status_text.text(f"Scraping terminé! {len(pages)} pages collectées.")
        
        return pages
    except Exception as e:
        st.error(f"Erreur lors du scraping: {e}")
        return []

def process_and_store_data(scraped_pages: List[ScrapedPage]):
    """Process scraped data and store in vector database."""
    try:
        with st.spinner("Traitement et stockage des données..."):
            st.session_state.vector_db.add_documents_from_scraped_data(scraped_pages)
            
            # Convert to dict format for session storage
            scraped_data = []
            for page in scraped_pages:
                scraped_data.append({
                    'url': page.url,
                    'title': page.title,
                    'content': page.content,
                    'language': page.language,
                    'scraped_at': page.scraped_at.isoformat(),
                    'links': page.links
                })
            
            st.session_state.scraped_data.extend(scraped_data)
        
        st.success(f"Données traitées et stockées avec succès! {len(scraped_pages)} pages ajoutées.")
        
    except Exception as e:
        st.error(f"Erreur lors du traitement des données: {e}")

def display_chat_interface():
    """Display the main chat interface."""
    st.markdown('<div class="main-header"><h1>🤖 Chatbot Intelligence Web</h1></div>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        if message['role'] == 'user':
            with chat_container:
                st.markdown(f'''
                <div class="chat-message user-message">
                    <strong>👤 Vous:</strong><br>
                    {message['content']}
                </div>
                ''', unsafe_allow_html=True)
        else:
            with chat_container:
                st.markdown(f'''
                <div class="chat-message bot-message">
                    <strong>🤖 Assistant:</strong><br>
                    {message['content']}
                </div>
                ''', unsafe_allow_html=True)
    
    # Input area
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Posez votre question:",
            placeholder="Tapez votre question ici...",
            height=100,
            key="user_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_button = st.form_submit_button("Envoyer", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("Effacer l'historique", use_container_width=True)
    
    # Handle form submissions
    if submit_button and user_input.strip():
        handle_user_question(user_input.strip())
    
    if clear_button:
        st.session_state.chat_history.clear()
        if st.session_state.chatbot:
            st.session_state.chatbot.clear_conversation_history()
        st.rerun()

def handle_user_question(question: str):
    """Process user question and generate response."""
    try:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': question,
            'timestamp': datetime.now()
        })
        
        # Search for relevant context
        search_results = []
        if st.session_state.vector_db:
            with st.spinner("Recherche dans la base de connaissances..."):
                search_results = st.session_state.vector_db.search_similar(question, n_results=5)
        
        # Generate response
        with st.spinner("Génération de la réponse..."):
            response_data = st.session_state.chatbot.generate_response(
                user_question=question,
                search_results=search_results,
                max_tokens=1000
            )
        
        # Format response for display
        formatted_response = ResponseFormatter.format_for_streamlit(response_data)
        
        # Add assistant message to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': formatted_response,
            'timestamp': datetime.now(),
            'sources': search_results
        })
        
        # Store current sources for sidebar display
        st.session_state.current_sources = ResponseFormatter.extract_sources(search_results)
        
        # Rerun to display new messages
        st.rerun()
        
    except Exception as e:
        st.error(f"Erreur lors du traitement de la question: {e}")

def display_sidebar():
    """Display sidebar with controls and information."""
    with st.sidebar:
        st.header("🛠️ Configuration")
        
        # Chatbot Configuration
        st.subheader("🤖 Configuration du Chatbot")
        
        # Prompt style selector
        if st.session_state.chatbot:
            available_styles = st.session_state.chatbot.list_available_prompt_styles()
            current_style = st.selectbox(
                "Style de réponse:",
                options=available_styles,
                help="Choisissez le style de réponse du chatbot"
            )
            
            if st.button("Appliquer le style"):
                st.session_state.chatbot.set_system_prompt(style=current_style)
                st.success(f"Style '{current_style}' appliqué!")
                st.rerun()
        
        st.divider()
        
        # Web Scraping Section
        st.subheader("📡 Scraping Web")
        
        with st.form("scraping_form"):
            website_url = st.text_input(
                "URL du site à analyser:",
                placeholder="https://example.com",
                help="Entrez l'URL du site web que vous souhaitez analyser"
            )
            
            max_pages = st.number_input(
                "Nombre maximum de pages:",
                min_value=1,
                max_value=100,
                value=20,
                help="Limite le nombre de pages à scraper pour éviter les longs traitements"
            )
            
            use_selenium = st.checkbox(
                "Utiliser Selenium (pour les sites avec JavaScript)",
                help="Cochez cette case si le site utilise beaucoup de JavaScript"
            )
            
            scrape_button = st.form_submit_button("🚀 Lancer le Scraping")
            
            if scrape_button and website_url:
                scraped_pages = scrape_website(website_url, max_pages, use_selenium)
                if scraped_pages:
                    process_and_store_data(scraped_pages)
        
        st.divider()
        
        # Database Information
        st.subheader("📊 Informations Base de Données")
        
        if st.session_state.vector_db:
            db_info = st.session_state.vector_db.get_database_info()
            
            st.metric("Type de DB", db_info.get('db_type', 'N/A'))
            st.metric("Modèle d'embedding", db_info.get('embedding_model', 'N/A'))
            st.metric("Taille des chunks", db_info.get('chunk_size', 'N/A'))
            
            if 'total_vectors' in db_info:
                st.metric("Vecteurs stockés", db_info['total_vectors'])
        
        st.divider()
        
        # Current Sources
        st.subheader("📚 Sources Actuelles")
        
        if st.session_state.current_sources:
            for i, source in enumerate(st.session_state.current_sources, 1):
                with st.expander(f"Source {i}: {source['title'][:30]}..."):
                    st.write(f"**Titre:** {source['title']}")
                    st.write(f"**URL:** [{source['url']}]({source['url']})")
                    st.write(f"**Extrait:** {source['snippet']}")
        else:
            st.info("Aucune source utilisée pour la dernière réponse.")
        
        st.divider()
        
        # Statistics
        st.subheader("📈 Statistiques")
        
        total_scraped = len(st.session_state.scraped_data)
        total_messages = len(st.session_state.chat_history)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pages analysées", total_scraped)
        with col2:
            st.metric("Messages échangés", total_messages)

def display_data_management():
    """Display data management interface."""
    st.header("📁 Gestion des Données")
    
    # Load existing data
    existing_data = load_scraped_data()
    
    if existing_data:
        st.subheader(f"Données existantes ({len(existing_data)} documents)")
        
        # Option to load existing data
        if st.button("🔄 Charger les données existantes dans la base vectorielle"):
            # Convert to ScrapedPage objects
            scraped_pages = []
            for data in existing_data:
                try:
                    page = ScrapedPage(
                        url=data['url'],
                        title=data['title'],
                        content=data['content'],
                        language=data.get('language', 'unknown'),
                        scraped_at=datetime.fromisoformat(data['scraped_at']),
                        links=data.get('links', [])
                    )
                    scraped_pages.append(page)
                except Exception as e:
                    st.warning(f"Erreur lors du chargement d'un document: {e}")
            
            if scraped_pages:
                process_and_store_data(scraped_pages)
        
        # Display data summary
        with st.expander("📋 Aperçu des données"):
            for i, data in enumerate(existing_data[:5], 1):  # Show first 5
                st.write(f"**{i}. {data['title']}**")
                st.write(f"URL: {data['url']}")
                st.write(f"Contenu: {data['content'][:200]}...")
                st.divider()
            
            if len(existing_data) > 5:
                st.info(f"... et {len(existing_data) - 5} autres documents")
    else:
        st.info("Aucune donnée existante trouvée. Commencez par scraper un site web.")

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Initialize components
    if not initialize_components():
        st.stop()
    
    # Main navigation
    tab1, tab2 = st.tabs(["💬 Chat", "📁 Données"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_data_management()
    
    # Sidebar
    display_sidebar()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🤖 Chatbot Web Scraper - Développé avec Streamlit, OpenAI et des technologies de pointe"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
