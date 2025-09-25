#!/usr/bin/env python3
"""
Test simple du chatbot avec Ollama.
Ce script teste directement la classe ChatBot modifiée.
"""

import sys
from pathlib import Path

# Ajouter les répertoires nécessaires au PATH
current_dir = Path(__file__).parent
project_dir = current_dir.parent
sys.path.append(str(project_dir))
sys.path.append(str(project_dir / "src"))

try:
    from src.chatbot import ChatBot, ResponseFormatter
    from src.vector_database import VectorDatabase
    print("✅ Imports des modules réussis")
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    exit(1)

def test_chatbot():
    """Test du chatbot avec Ollama."""
    print("\n🤖 Test du ChatBot avec Ollama")
    print("=" * 40)
    
    try:
        # Initialiser le chatbot
        print("Initialisation du chatbot...")
        chatbot = ChatBot()
        print(f"✅ ChatBot initialisé avec le modèle : {chatbot.model}")
        
        # Test des informations du modèle
        model_info = chatbot.get_model_info()
        print(f"📊 Informations du modèle : {model_info}")
        
        # Test de génération simple
        print("\n🧪 Test de génération simple...")
        question = "Peux-tu te présenter brièvement ?"
        
        response_data = chatbot.generate_response(question)
        
        if response_data.get("error"):
            print(f"❌ Erreur : {response_data['response']}")
            return False
        else:
            print("✅ Réponse générée avec succès :")
            print(f"   {response_data['response']}")
            
        # Test avec contexte simulé
        print("\n🧪 Test avec contexte simulé...")
        search_results = [
            {
                'content': "Ollama est un outil qui permet d'exécuter des modèles de langage en local. Il offre une API simple pour interagir avec des LLMs sans avoir besoin d'internet.",
                'metadata': {
                    'source_url': 'https://ollama.ai',
                    'title': 'Documentation Ollama',
                    'chunk_index': 0
                }
            }
        ]
        
        question_with_context = "Qu'est-ce qu'Ollama et quels sont ses avantages ?"
        response_data_context = chatbot.generate_response(
            question_with_context, 
            search_results=search_results
        )
        
        if response_data_context.get("error"):
            print(f"❌ Erreur avec contexte : {response_data_context['response']}")
            return False
        else:
            print("✅ Réponse avec contexte générée :")
            formatted_response = ResponseFormatter.format_for_streamlit(response_data_context)
            print(f"   {formatted_response}")
            
        print(f"\n📈 Historique de conversation : {len(chatbot.get_conversation_history())} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_database():
    """Test rapide de la base de données vectorielle."""
    print("\n🗂️ Test de la base vectorielle")
    print("=" * 40)
    
    try:
        # Initialiser la base vectorielle
        vector_db = VectorDatabase()
        print("✅ Base vectorielle initialisée")
        
        # Test d'ajout de documents simple
        test_docs = [
            {
                'content': 'Ceci est un test de document.',
                'metadata': {'source_url': 'test', 'title': 'Test Doc'}
            }
        ]
        
        vector_db.add_documents(test_docs)
        print("✅ Documents de test ajoutés")
        
        # Test de recherche
        results = vector_db.search("test document", top_k=1)
        if results:
            print(f"✅ Recherche réussie : {len(results)} résultat(s)")
        else:
            print("⚠️ Aucun résultat trouvé")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test vectoriel : {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Tests complets du système Chatbot + Ollama")
    print("=" * 60)
    
    # Test du chatbot
    chatbot_ok = test_chatbot()
    
    # Test de la base vectorielle
    vector_ok = test_vector_database()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"ChatBot Ollama : {'✅' if chatbot_ok else '❌'}")
    print(f"Base vectorielle : {'✅' if vector_ok else '❌'}")
    
    if chatbot_ok and vector_ok:
        print("\n🎉 Tous les tests sont réussis ! Le système est opérationnel.")
        print("💡 Vous pouvez maintenant utiliser l'interface Streamlit.")
    else:
        print("\n⚠️ Certains composants ne fonctionnent pas correctement.")

if __name__ == "__main__":
    main()
