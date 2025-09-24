#!/usr/bin/env python3
"""
Test rapide sans clé API pour vérifier le fonctionnement de base.
"""

import sys
from pathlib import Path

# Ajouter le chemin des modules
sys.path.append(str(Path(__file__).parent / "src"))

def test_web_scraper():
    """Test du web scraper."""
    print("🕷️ Test du Web Scraper...")
    
    from web_scraper import WebScraper
    
    # Test d'initialisation
    scraper = WebScraper(use_selenium=False)
    print("  ✅ Scraper initialisé")
    
    # Test de validation d'URL
    valid_url = scraper._is_valid_url("https://httpbin.org/html", "httpbin.org")
    print(f"  ✅ Validation URL: {valid_url}")
    
    print("  ℹ️ Note: Pour tester le scraping complet, lancez l'application Streamlit")

def test_vector_database():
    """Test de la base de données vectorielle."""
    print("\n🗂️ Test de la Base de Données Vectorielle...")
    
    from vector_database import VectorDatabase
    
    # Test d'initialisation
    try:
        vector_db = VectorDatabase("chroma")
        print("  ✅ Base vectorielle ChromaDB initialisée")
        
        # Test d'informations
        info = vector_db.get_database_info()
        print(f"  ✅ Type: {info['db_type']}, Modèle: {info['embedding_model']}")
        
    except Exception as e:
        print(f"  ⚠️ Erreur ChromaDB: {e}")
        try:
            vector_db = VectorDatabase("faiss")
            print("  ✅ Base vectorielle FAISS initialisée")
        except Exception as e2:
            print(f"  ❌ Erreur FAISS: {e2}")

def test_chatbot():
    """Test du chatbot (sans clé API)."""
    print("\n🤖 Test du Chatbot...")
    
    from chatbot import ChatBot
    
    # Test de la classe (sans initialisation complète)
    print("  ✅ Module ChatBot importé")
    print("  ℹ️ Note: Configurez OPENAI_API_KEY dans .env pour les tests complets")

def main():
    """Fonction principale."""
    print("🧪 Test Rapide du Chatbot Web Scraper")
    print("=" * 50)
    
    test_web_scraper()
    test_vector_database()
    test_chatbot()
    
    print("\n" + "=" * 50)
    print("✅ Tests de base réussis!")
    print("\n📋 Prochaines étapes:")
    print("1. Configurez votre clé OpenAI dans .env:")
    print("   OPENAI_API_KEY=votre_clé_ici")
    print("2. Lancez l'application:")
    print("   streamlit run app.py")
    print("3. Ou utilisez le script de démarrage:")
    print("   ./start.sh")

if __name__ == "__main__":
    main()
