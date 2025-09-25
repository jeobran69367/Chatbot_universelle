"""
API Flask pour intégrer le chatbot dans un site existant
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sys
import os
sys.path.append('src')

from chatbot import ChatBot
from vector_database import VectorDatabase

app = Flask(__name__, template_folder='templates', static_folder='templates')
CORS(app)  # Permettre les requêtes cross-origin

# Handler pour les requêtes OPTIONS (préflight CORS)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        from flask import make_response
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Initialiser le chatbot
chatbot = None
vector_db = None

# État d'initialisation
initialization_state = {
    'is_initialized': False,
    'initial_url': None,
    'initialization_data': None
}

def initialize_chatbot():
    """Initialiser le chatbot et la base de données"""
    global chatbot, vector_db
    try:
        vector_db = VectorDatabase("chroma")
        chatbot = ChatBot(model="llama3.1:latest")
        print("✅ Chatbot initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur initialisation chatbot: {e}")

@app.route('/api/init', methods=['POST'])
def initialize_with_website():
    """Initialiser le chatbot avec un site web"""
    global initialization_state
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL manquante'}), 400
        
        # Import du scraper
        from src.web_scraper import WebScraper
        scraper = WebScraper(use_selenium=False)
        
        # Scraping du site initial
        pages = scraper.scrape_website(url, max_pages=20)
        
        # Ajout à la base de données
        if vector_db and pages:
            vector_db.add_documents_from_scraped_data(pages)
            
            initialization_state['is_initialized'] = True
            initialization_state['initial_url'] = url
            initialization_state['initialization_data'] = {
                'pages_count': len(pages),
                'content_summary': f"Analysé {len(pages)} pages de {url}"
            }
        
        return jsonify({
            'success': True,
            'message': 'Chatbot initialisé avec succès',
            'pages_scraped': len(pages),
            'url': url,
            'summary': f"J'ai analysé {len(pages)} pages de votre site. Je suis maintenant prêt à répondre à vos questions !"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint pour les messages de chat"""
    try:
        # TEMPORAIRE: Désactiver la vérification d'initialisation pour déboguer
        # if not initialization_state['is_initialized']:
        #     return jsonify({
        #         'error': 'Le chatbot n\'est pas encore initialisé. Veuillez d\'abord analyser un site web.',
        #         'initialization_required': True
        #     }), 400
        
        data = request.json
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'Message vide'}), 400
        
        # Recherche dans la base de données
        search_results = []
        if vector_db:
            search_results = vector_db.search_similar(question, n_results=5)
        
        # Génération de la réponse
        response_data = chatbot.generate_response(
            user_question=question,
            search_results=search_results,
            max_tokens=1000
        )
        
        return jsonify({
            'response': response_data['response'],
            'sources': len(search_results),
            'timestamp': response_data.get('timestamp'),
            'model': response_data.get('model')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_website():
    """Endpoint pour scraper un site web"""
    try:
        data = request.json
        url = data.get('url', '')
        max_pages = data.get('max_pages', 10)
        
        if not url:
            return jsonify({'error': 'URL manquante'}), 400
        
        # Import du scraper
        from src.web_scraper import WebScraper
        scraper = WebScraper(use_selenium=False)
        
        # Scraping
        pages = scraper.scrape_website(url, max_pages)
        
        # Ajout à la base de données
        if vector_db and pages:
            vector_db.add_documents_from_scraped_data(pages)
        
        return jsonify({
            'success': True,
            'pages_scraped': len(pages),
            'url': url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """Status de l'API"""
    return jsonify({
        'status': 'online',
        'chatbot_ready': chatbot is not None,
        'vector_db_ready': vector_db is not None,
        'is_initialized': initialization_state['is_initialized'],
        'initial_url': initialization_state['initial_url'],
        'initialization_data': initialization_state['initialization_data']
    })

@app.route('/')
def index():
    """Page d'accueil avec redirection vers l'initialisation"""
    return render_template('init_page.html')

@app.route('/docs')
def docs():
    """Documentation et guide"""
    return send_from_directory('templates', 'init_page.html')

@app.route('/init')
def init_page():
    """Page d'initialisation"""
    return render_template('init_page.html')

@app.route('/chat')
def chat_page():
    """Page de chat"""
    return render_template('embedded_chat.html')

# Widget HTML à intégrer dans d'autres sites
@app.route('/widget')
def widget():
    """Widget de chat embeddable"""
    from flask import make_response
    response = make_response(render_template('chat_widget.html'))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

@app.route('/widget.js')
def widget_js():
    """Script JavaScript du widget"""
    from flask import make_response
    response = make_response(send_from_directory('templates', 'widget.js', mimetype='application/javascript'))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

if __name__ == '__main__':
    initialize_chatbot()
    app.run(host='0.0.0.0', port=5001, debug=True)
