#!/usr/bin/env python3
"""
Script de lancement pour l'application Streamlit avec gestion des chemins.
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Configure les chemins Python correctement."""
    # Ajouter le dossier racine du projet
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Ajouter le dossier src
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Ajouter le dossier config
    config_path = project_root / "config"
    sys.path.insert(0, str(config_path))
    
    print(f"✅ Chemins configurés:")
    print(f"   - Projet: {project_root}")
    print(f"   - Src: {src_path}")
    print(f"   - Config: {config_path}")

def check_environment():
    """Vérifie l'environnement."""
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    # Vérifier la clé OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("⚠️ Attention: Clé OpenAI non configurée")
        print("   Modifiez le fichier .env avec votre vraie clé API")
    else:
        print("✅ Clé OpenAI configurée")

def test_imports():
    """Test rapide des imports."""
    try:
        from web_scraper import WebScraper
        from vector_database import VectorDatabase
        from chatbot import ChatBot
        print("✅ Tous les modules importés avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Lancement du Chatbot Web Scraper")
    print("=" * 50)
    
    # Configuration des chemins
    setup_paths()
    
    # Vérification de l'environnement
    check_environment()
    
    # Test des imports
    if not test_imports():
        print("❌ Échec des imports. Vérifiez votre installation.")
        return False
    
    print("=" * 50)
    print("🎉 Tout est prêt ! Lancement de Streamlit...")
    
    # Lancer Streamlit
    os.system("streamlit run app.py")
    
    return True

if __name__ == "__main__":
    main()
