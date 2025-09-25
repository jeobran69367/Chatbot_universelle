#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Chatbot Web Scraper
Démarre l'API Flask en mode production
"""

import os
import sys
import logging
from pathlib import Path
import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', mode='a') if os.path.exists('logs') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Configure l'environnement de production"""
    # Créer les répertoires nécessaires
    directories = [
        'data/embeddings',
        'data/scraped', 
        'data/models',
        'logs',
        '__blobstorage__'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Variables d'environnement par défaut
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_PORT', '5001')
    os.environ.setdefault('OLLAMA_HOST', 'http://localhost:11434')
    os.environ.setdefault('LOG_LEVEL', 'INFO')

def main():
    """Point d'entrée principal"""
    logger.info("🚀 Démarrage de l'application Chatbot Web Scraper")
    
    # Configuration de l'environnement
    setup_environment()
    
    try:
        # Import et configuration de l'API Flask
        from api_server import app
        
        # Configuration de l'application
        app.config['startup_time'] = datetime.datetime.now().isoformat()
        app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
        
        # Port d'écoute
        port = int(os.environ.get('FLASK_PORT', 5001))
        
        logger.info(f"📡 Démarrage du serveur API sur le port {port}")
        logger.info(f"🌐 Application disponible à: http://0.0.0.0:{port}")
        logger.info(f"📊 Status endpoint: http://0.0.0.0:{port}/api/status")
        
        # Démarrage du serveur Flask
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,  # Production mode
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage de l'application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
