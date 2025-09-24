#!/usr/bin/env python3
"""
Script de test simple pour vérifier l'installation et la configuration du chatbot.
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin des modules
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Tester l'importation des modules."""
    print("🧪 Test des importations...")
    
    try:
        print("  ✓ Streamlit...", end=" ")
        import streamlit as st
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ Requests...", end=" ")
        import requests
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ BeautifulSoup...", end=" ")
        from bs4 import BeautifulSoup
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ OpenAI...", end=" ")
        import openai
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ Numpy...", end=" ")
        import numpy
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ ChromaDB...", end=" ")
        import chromadb
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ Sentence Transformers...", end=" ")
        from sentence_transformers import SentenceTransformer
        print("OK")
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    print("✅ Tous les modules importés avec succès!")
    return True

def test_modules():
    """Tester l'importation de nos modules personnalisés."""
    print("\n📦 Test des modules personnalisés...")
    
    try:
        print("  ✓ Web Scraper...", end=" ")
        from web_scraper import WebScraper
        print("OK")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ Vector Database...", end=" ")
        from vector_database import VectorDatabase
        print("OK")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    try:
        print("  ✓ Chatbot...", end=" ")
        from chatbot import ChatBot
        print("OK")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    print("✅ Tous les modules personnalisés importés avec succès!")
    return True

def test_configuration():
    """Tester la configuration."""
    print("\n⚙️ Test de la configuration...")
    
    try:
        print("  ✓ Configuration...", end=" ")
        from config.settings import OPENAI_API_KEY, PAGE_TITLE
        print("OK")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    # Vérifier les dossiers
    print("  ✓ Dossiers de données...", end=" ")
    from config.settings import DATA_DIR, SCRAPED_DATA_DIR, EMBEDDINGS_DIR
    
    if DATA_DIR.exists():
        print("OK")
    else:
        print(f"❌ Dossier manquant: {DATA_DIR}")
        return False
    
    print("✅ Configuration validée!")
    return True

def test_environment():
    """Tester les variables d'environnement."""
    print("\n🔐 Test des variables d'environnement...")
    
    # Charger le fichier .env
    try:
        from python_dotenv import load_dotenv
        load_dotenv()
        print("  ✓ Fichier .env chargé")
    except Exception as e:
        print(f"  ⚠️  Erreur lors du chargement .env: {e}")
    
    # Vérifier la clé OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        print("  ✅ Clé OpenAI configurée")
    else:
        print("  ⚠️  Clé OpenAI non configurée (utiliser votre vraie clé pour les tests complets)")
    
    return True

def run_basic_functionality_test():
    """Test basique de fonctionnalité."""
    print("\n🚀 Test basique de fonctionnalité...")
    
    try:
        from vector_database import VectorDatabase
        print("  ✓ Initialisation de la base vectorielle...", end=" ")
        vector_db = VectorDatabase("chroma")
        print("OK")
        
        # Test d'info
        print("  ✓ Informations de la base...", end=" ")
        info = vector_db.get_database_info()
        print(f"OK (Type: {info['db_type']})")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False
    
    print("✅ Tests de base réussis!")
    return True

def main():
    """Fonction principale de test."""
    print("🤖 Test du Chatbot Web Scraper")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Tests
    if not test_imports():
        all_tests_passed = False
    
    if not test_modules():
        all_tests_passed = False
    
    if not test_configuration():
        all_tests_passed = False
    
    if not test_environment():
        all_tests_passed = False
    
    if not run_basic_functionality_test():
        all_tests_passed = False
    
    # Résultat final
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 Tous les tests sont passés avec succès!")
        print("\n📋 Prochaines étapes:")
        print("1. Configurez votre clé OpenAI dans le fichier .env")
        print("2. Lancez l'application: streamlit run app.py")
        print("3. Ou testez les exemples: python example.py")
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
