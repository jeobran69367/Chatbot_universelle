"""
Exemple d'utilisation du chatbot web scraper.
Ce script montre comment utiliser les différents modules du projet.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le dossier src au PATH Python
sys.path.append(str(Path(__file__).parent / "src"))

# Définir la clé API OpenAI pour les tests
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

def example_web_scraping():
    """Exemple de scraping web."""
    print("🕷️ Exemple de Web Scraping")
    print("-" * 40)
    
    try:
        from web_scraper import WebScraper
        
        # Créer un scraper
        scraper = WebScraper(use_selenium=False)
        
        # Scraper un site (exemple avec un petit site)
        print("Scraping du site example.com...")
        pages = scraper.scrape_website("https://httpbin.org", max_pages=3)
        
        print(f"✅ {len(pages)} pages scrapées avec succès!")
        
        for i, page in enumerate(pages, 1):
            print(f"\nPage {i}:")
            print(f"  - Titre: {page.title}")
            print(f"  - URL: {page.url}")
            print(f"  - Contenu: {len(page.content)} caractères")
            print(f"  - Langue: {page.language}")
        
        return pages
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")
        return []

def example_vectorization(scraped_pages):
    """Exemple de vectorisation."""
    print("\n🧠 Exemple de Vectorisation")
    print("-" * 40)
    
    try:
        from vector_database import VectorDatabase
        
        if not scraped_pages:
            print("⚠️ Aucune page scrapée disponible")
            return None
        
        # Créer la base de données vectorielle
        print("Initialisation de la base vectorielle...")
        vector_db = VectorDatabase("chroma")
        
        # Ajouter les documents
        print("Ajout des documents à la base vectorielle...")
        vector_db.add_documents_from_scraped_data(scraped_pages)
        
        print("✅ Documents ajoutés avec succès!")
        
        # Test de recherche
        print("\nTest de recherche sémantique...")
        results = vector_db.search_similar("HTTP request response", n_results=3)
        
        print(f"🔍 {len(results)} résultats trouvés:")
        for i, result in enumerate(results, 1):
            print(f"\nRésultat {i}:")
            print(f"  - Contenu: {result['content'][:100]}...")
            print(f"  - Source: {result['metadata'].get('source_url', 'N/A')}")
            print(f"  - Distance: {result.get('distance', 'N/A')}")
        
        return vector_db
        
    except Exception as e:
        print(f"❌ Erreur lors de la vectorisation: {e}")
        return None

def example_chatbot(vector_db):
    """Exemple d'utilisation du chatbot."""
    print("\n🤖 Exemple de Chatbot")
    print("-" * 40)
    
    try:
        from chatbot import ChatBot
        
        if not vector_db:
            print("⚠️ Base vectorielle non disponible")
            return
        
        # Vérifier la clé API
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            print("⚠️ Clé API OpenAI non configurée. Exemple simulé.")
            print("Pour utiliser le chatbot réel:")
            print("1. Obtenez une clé API sur https://platform.openai.com/")
            print("2. Modifiez le fichier .env avec votre clé")
            return
        
        # Initialiser le chatbot
        print("Initialisation du chatbot...")
        chatbot = ChatBot()
        
        # Questions d'exemple
        questions = [
            "What is HTTP?",
            "How do HTTP requests work?",
            "Explain HTTP response codes"
        ]
        
        for question in questions:
            print(f"\n❓ Question: {question}")
            
            # Rechercher du contexte
            search_results = vector_db.search_similar(question, n_results=3)
            
            # Générer une réponse
            response_data = chatbot.generate_response(question, search_results)
            
            if response_data.get("error"):
                print(f"❌ Erreur: {response_data['response']}")
            else:
                print(f"🤖 Réponse: {response_data['response']}")
                print(f"📊 Tokens utilisés: {response_data.get('token_usage', {}).get('total_tokens', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'utilisation du chatbot: {e}")

def example_streamlit_info():
    """Informations pour lancer l'interface Streamlit."""
    print("\n🎨 Interface Streamlit")
    print("-" * 40)
    print("Pour lancer l'interface web complète:")
    print("1. Assurez-vous que toutes les dépendances sont installées:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Configurez votre clé API OpenAI dans le fichier .env:")
    print("   OPENAI_API_KEY=your_actual_api_key")
    print()
    print("3. Lancez l'application:")
    print("   streamlit run app.py")
    print()
    print("4. Ou utilisez le script de démarrage:")
    print("   ./start.sh  (macOS/Linux)")
    print("   start.bat   (Windows)")

def main():
    """Fonction principale d'exemple."""
    print("🤖 Chatbot Web Scraper - Exemples d'utilisation")
    print("=" * 60)
    
    # 1. Web Scraping
    scraped_pages = example_web_scraping()
    
    # 2. Vectorisation
    vector_db = example_vectorization(scraped_pages)
    
    # 3. Chatbot
    example_chatbot(vector_db)
    
    # 4. Information Streamlit
    example_streamlit_info()
    
    print("\n" + "=" * 60)
    print("✅ Exemples terminés!")
    print("📖 Consultez README.md pour plus d'informations")

if __name__ == "__main__":
    main()
