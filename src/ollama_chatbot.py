"""
Chatbot intégrant Ollama pour des réponses intelligentes locales.
Cette version remplace OpenAI par Ollama pour une solution entièrement locale.
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin pour les imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from config.settings import OLLAMA_HOST, OLLAMA_MODEL

class OllamaChatBot:
    """
    Chatbot intelligent utilisant Ollama avec RAG (Retrieval Augmented Generation).
    """
    
    def __init__(self, model: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        """
        Initialise le chatbot Ollama.
        
        Args:
            model: Modèle Ollama à utiliser (ex: 'llama3.1', 'mistral', 'codellama')
            host: Adresse du serveur Ollama
        """
        self.model = model
        self.host = host
        self.conversation_history: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)
        
        # Vérifier si Ollama est disponible
        self._check_ollama_availability()
        
        # System prompt pour le chatbot
        self.system_prompt = """
        Vous êtes un assistant IA intelligent et serviable qui aide les utilisateurs en répondant à leurs questions 
        en utilisant les informations provenant de sites web qui ont été analysés et indexés.
        
        Instructions importantes:
        1. Utilisez principalement les informations fournies dans le contexte pour répondre aux questions
        2. Si l'information n'est pas disponible dans le contexte, indiquez-le clairement
        3. Soyez précis et informatif dans vos réponses
        4. Citez la source (URL) quand c'est pertinent
        5. Répondez en français de manière naturelle et conversationnelle
        6. Si vous n'êtes pas sûr d'une information, dites-le explicitement
        
        Contexte des documents analysés:
        {context}
        
        Conversation précédente:
        {conversation_history}
        """
    
    def _check_ollama_availability(self):
        """Vérifie si Ollama est disponible."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                
                if self.model not in available_models:
                    self.logger.warning(f"Modèle {self.model} non trouvé. Modèles disponibles: {available_models}")
                    if available_models:
                        self.model = available_models[0]
                        self.logger.info(f"Utilisation du modèle: {self.model}")
                
                self.logger.info(f"Ollama disponible avec le modèle: {self.model}")
            else:
                raise Exception("Serveur Ollama non accessible")
                
        except Exception as e:
            error_msg = f"Erreur de connexion à Ollama: {e}"
            self.logger.error(error_msg)
            raise Exception(f"Assurez-vous qu'Ollama est installé et lancé: {error_msg}")
    
    def _call_ollama_api(self, prompt: str) -> str:
        """Appelle l'API Ollama pour générer une réponse."""
        try:
            if OLLAMA_AVAILABLE:
                # Utiliser la bibliothèque ollama si disponible
                response = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    stream=False
                )
                return response['message']['content']
            else:
                # Utiliser l'API REST directement
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 1000
                    }
                }
                
                response = requests.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    raise Exception(f"Erreur API Ollama: {response.status_code} - {response.text}")
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de l'appel à Ollama: {e}")
            raise
    
    def format_context_from_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Formate les résultats de recherche en contexte pour le prompt.
        
        Args:
            search_results: Liste des résultats de recherche de la base vectorielle
            
        Returns:
            Chaîne de contexte formatée
        """
        if not search_results:
            return "Aucun contexte pertinent trouvé dans les documents analysés."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            source_url = metadata.get('source_url', 'Source inconnue')
            title = metadata.get('title', 'Titre inconnu')
            
            context_part = f"""
Document {i}:
Titre: {title}
Source: {source_url}
Contenu: {content}
---
"""
            context_parts.append(context_part)
        
        return '\n'.join(context_parts)
    
    def format_conversation_history(self) -> str:
        """
        Formate l'historique de conversation pour le prompt.
        
        Returns:
            Historique de conversation formaté
        """
        if not self.conversation_history:
            return "Aucune conversation précédente."
        
        history_parts = []
        # Garder seulement les derniers échanges pour éviter les limites
        recent_history = self.conversation_history[-6:]  # 3 derniers échanges
        
        for message in recent_history:
            role = message['role']
            content = message['content']
            if role == 'user':
                history_parts.append(f"Utilisateur: {content}")
            elif role == 'assistant':
                history_parts.append(f"Assistant: {content}")
        
        return '\n'.join(history_parts)
    
    def generate_response(self, 
                         user_question: str, 
                         search_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Génère une réponse utilisant Ollama avec RAG.
        
        Args:
            user_question: Question de l'utilisateur
            search_results: Résultats de recherche pertinents de la base vectorielle
            
        Returns:
            Dictionnaire contenant la réponse et les métadonnées
        """
        try:
            # Formater le contexte à partir des résultats de recherche
            context = ""
            if search_results:
                context = self.format_context_from_search_results(search_results)
            else:
                context = "Aucun contexte spécifique fourni."
            
            # Formater l'historique de conversation
            conversation_history = self.format_conversation_history()
            
            # Créer le prompt avec le contexte
            full_prompt = self.system_prompt.format(
                context=context,
                conversation_history=conversation_history
            )
            
            # Ajouter la question de l'utilisateur
            full_prompt += f"\n\nQuestion de l'utilisateur: {user_question}\n\nRéponse:"
            
            # Enregistrer la requête
            self.logger.info(f"Génération de réponse pour: {user_question[:100]}...")
            
            # Faire l'appel à Ollama
            assistant_response = self._call_ollama_api(full_prompt)
            
            # Mettre à jour l'historique de conversation
            self.conversation_history.append({"role": "user", "content": user_question})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            # Garder l'historique gérable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Préparer les données de réponse
            response_data = {
                "response": assistant_response,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "sources_used": len(search_results) if search_results else 0,
                "host": self.host
            }
            
            self.logger.info("Réponse générée avec succès")
            
            return response_data
            
        except Exception as e:
            error_message = f"Erreur lors de la génération de la réponse: {str(e)}"
            self.logger.error(error_message)
            
            return {
                "response": error_message,
                "error": True,
                "timestamp": datetime.now().isoformat(),
                "model": self.model
            }
    
    def clear_conversation_history(self):
        """Efface l'historique de conversation."""
        self.conversation_history.clear()
        self.logger.info("Historique de conversation effacé")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Récupère l'historique de conversation actuel.
        
        Returns:
            Liste des messages de conversation
        """
        return self.conversation_history.copy()
    
    def set_system_prompt(self, new_prompt: str = None, style: str = None):
        """
        Met à jour le prompt système.
        
        Args:
            new_prompt: Nouveau prompt système direct
            style: Style de prompt à appliquer
        """
        if style:
            # Définir les styles de prompts disponibles
            prompt_styles = {
                "Assistant Professionnel": """
                Vous êtes un assistant IA professionnel et efficace qui aide les utilisateurs en répondant à leurs questions 
                de manière précise et structurée. Utilisez les informations des documents analysés pour fournir des réponses 
                complètes et bien organisées.

                Instructions:
                1. Structurez vos réponses clairement avec des points ou des sections
                2. Citez les sources quand c'est pertinent
                3. Soyez concis mais complet
                4. Utilisez un ton professionnel et courtois
                
                Contexte: {context}
                Conversation précédente: {conversation_history}
                """,
                
                "Expert Technique": """
                Vous êtes un expert technique qui fournit des analyses approfondies et des explications détaillées. 
                Utilisez les informations techniques des documents pour donner des réponses précises et expertes.

                Instructions:
                1. Fournissez des détails techniques pertinents
                2. Expliquez les concepts complexes clairement
                3. Mentionnez les limitations ou considérations importantes
                4. Citez les sources techniques
                
                Contexte: {context}
                Conversation précédente: {conversation_history}
                """,
                
                "Guide Pédagogique": """
                Vous êtes un guide pédagogique qui aide à comprendre et apprendre. Expliquez les concepts de manière 
                accessible et progressive, en utilisant des exemples et des analogies quand c'est utile.

                Instructions:
                1. Expliquez étape par étape
                2. Utilisez des exemples concrets
                3. Adaptez le niveau d'explication à l'utilisateur
                4. Encouragez l'apprentissage progressif
                
                Contexte: {context}
                Conversation précédente: {conversation_history}
                """,
                
                "Conseiller Bienveillant": """
                Vous êtes un conseiller bienveillant qui aide avec empathie et compréhension. Fournissez des conseils 
                réfléchis et du support en utilisant les informations disponibles.

                Instructions:
                1. Montrez de l'empathie dans vos réponses
                2. Fournissez des conseils pratiques
                3. Soyez encourageant et supportif
                4. Respectez les préoccupations de l'utilisateur
                
                Contexte: {context}
                Conversation précédente: {conversation_history}
                """,
                
                "Analyste Concis": """
                Vous êtes un analyste qui fournit des réponses concises et directes. Allez droit au but avec les 
                informations les plus importantes tirées des documents.

                Instructions:
                1. Soyez direct et concis
                2. Priorisez les informations clés
                3. Évitez les détails superflus
                4. Structurez vos réponses en points essentiels
                
                Contexte: {context}
                Conversation précédente: {conversation_history}
                """
            }
            
            if style in prompt_styles:
                self.system_prompt = prompt_styles[style]
                self.logger.info(f"Style de prompt appliqué: {style}")
            else:
                self.logger.warning(f"Style inconnu: {style}. Styles disponibles: {list(prompt_styles.keys())}")
        elif new_prompt:
            self.system_prompt = new_prompt
            self.logger.info("Prompt système mis à jour directement")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Récupère des informations sur la configuration actuelle du modèle.
        
        Returns:
            Dictionnaire avec les informations du modèle
        """
        return {
            "model": self.model,
            "host": self.host,
            "conversation_length": len(self.conversation_history),
            "ollama_available": OLLAMA_AVAILABLE
        }
    
    def list_available_models(self) -> List[str]:
        """Liste les modèles Ollama disponibles."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                return []
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
    
    def list_available_prompt_styles(self) -> List[str]:
        """Liste les styles de prompt disponibles."""
        # Styles de réponse disponibles pour le chatbot
        available_styles = [
            "Assistant Professionnel",
            "Expert Technique", 
            "Guide Pédagogique",
            "Conseiller Bienveillant",
            "Analyste Concis"
        ]
        return available_styles

class ResponseFormatter:
    """Classe utilitaire pour formater les réponses du chatbot."""
    
    @staticmethod
    def format_for_streamlit(response_data: Dict[str, Any]) -> str:
        """
        Formate la réponse pour l'affichage Streamlit.
        
        Args:
            response_data: Données de réponse du chatbot
            
        Returns:
            Chaîne de réponse formatée
        """
        response = response_data.get("response", "")
        
        if response_data.get("error"):
            return f"❌ **Erreur**: {response}"
        
        # Ajouter un pied de page avec métadonnées si disponible
        footer_parts = []
        
        if "sources_used" in response_data and response_data["sources_used"] > 0:
            footer_parts.append(f"📚 Sources consultées: {response_data['sources_used']}")
        
        if "model" in response_data:
            footer_parts.append(f"🤖 Modèle: {response_data['model']}")
        
        if footer_parts:
            footer = "\n\n---\n*" + " | ".join(footer_parts) + "*"
            return response + footer
        
        return response
    
    @staticmethod
    def extract_sources(search_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extrait les informations de source des résultats de recherche.
        
        Args:
            search_results: Résultats de recherche de la base vectorielle
            
        Returns:
            Liste des informations de source
        """
        sources = []
        for result in search_results:
            metadata = result.get('metadata', {})
            source = {
                'title': metadata.get('title', 'Titre inconnu'),
                'url': metadata.get('source_url', '#'),
                'snippet': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', '')
            }
            sources.append(source)
        
        return sources

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le chatbot
    chatbot = OllamaChatBot()
    
    # Exemples de résultats de recherche (viendraient de la base vectorielle)
    example_search_results = [
        {
            'content': "L'intelligence artificielle est une technologie révolutionnaire...",
            'metadata': {
                'source_url': 'https://example.com/ai-article',
                'title': 'Introduction à l\'IA',
                'chunk_index': 0
            }
        }
    ]
    
    # Générer une réponse
    response = chatbot.generate_response(
        user_question="Qu'est-ce que l'intelligence artificielle ?",
        search_results=example_search_results
    )
    
    print("Réponse:", response["response"])
    print("Modèle:", response.get("model", "N/A"))
