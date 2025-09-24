"""
OpenAI integration module for generating intelligent responses.
This module handles communication with OpenAI API for chat completion.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import tiktoken

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import config with fallback
try:
    from config.settings import OPENAI_API_KEY, OPENAI_MODEL
except ImportError:
    # Fallback values if config import fails
    import os
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-3.5-turbo"

class ChatBot:
    """
    Intelligent chatbot using OpenAI GPT models with RAG (Retrieval Augmented Generation).
    """
    
    def __init__(self, model: str = OPENAI_MODEL, temperature: float = 0.7):
        """
        Initialize the chatbot.
        
        Args:
            model: OpenAI model to use (e.g., 'gpt-3.5-turbo', 'gpt-4')
            temperature: Temperature for response generation (0.0-1.0)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature
        self.conversation_history: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # System prompt for the chatbot
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
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            self.logger.warning(f"Error counting tokens: {e}")
            return len(text.split()) * 1.3  # Rough estimation
    
    def trim_context(self, context: str, max_tokens: int = 3000) -> str:
        """
        Trim context to fit within token limits.
        
        Args:
            context: Context text to trim
            max_tokens: Maximum number of tokens allowed
            
        Returns:
            Trimmed context
        """
        if self.count_tokens(context) <= max_tokens:
            return context
        
        # Split into chunks and keep the most relevant ones
        lines = context.split('\n')
        trimmed_lines = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self.count_tokens(line)
            if current_tokens + line_tokens <= max_tokens:
                trimmed_lines.append(line)
                current_tokens += line_tokens
            else:
                break
        
        trimmed_context = '\n'.join(trimmed_lines)
        if len(trimmed_context) < len(context):
            trimmed_context += "\n... (contexte tronqué pour respecter les limites de tokens)"
        
        return trimmed_context
    
    def format_context_from_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for the prompt.
        
        Args:
            search_results: List of search results from vector database
            
        Returns:
            Formatted context string
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
        Format conversation history for the prompt.
        
        Returns:
            Formatted conversation history
        """
        if not self.conversation_history:
            return "Aucune conversation précédente."
        
        history_parts = []
        # Keep only last few exchanges to avoid token limits
        recent_history = self.conversation_history[-6:]  # Last 3 exchanges (user + assistant)
        
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
                         search_results: List[Dict[str, Any]] = None,
                         max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate a response using OpenAI with RAG.
        
        Args:
            user_question: User's question
            search_results: Relevant search results from vector database
            max_tokens: Maximum tokens for response
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Format context from search results
            context = ""
            if search_results:
                context = self.format_context_from_search_results(search_results)
                context = self.trim_context(context, max_tokens=3000)
            else:
                context = "Aucun contexte spécifique fourni."
            
            # Format conversation history
            conversation_history = self.format_conversation_history()
            
            # Create the system prompt with context
            system_message = self.system_prompt.format(
                context=context,
                conversation_history=conversation_history
            )
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_question}
            ]
            
            # Log the request (without sensitive data)
            self.logger.info(f"Generating response for question: {user_question[:100]}...")
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=self.temperature,
                top_p=0.95,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract the response
            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_question})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Prepare response data
            response_data = {
                "response": assistant_response,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "sources_used": len(search_results) if search_results else 0,
                "temperature": self.temperature
            }
            
            self.logger.info(f"Response generated successfully. Tokens used: {response.usage.total_tokens}")
            
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
        """Clear the conversation history."""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
    
    def set_system_prompt(self, new_prompt: str):
        """
        Update the system prompt.
        
        Args:
            new_prompt: New system prompt
        """
        self.system_prompt = new_prompt
        self.logger.info("System prompt updated")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "conversation_length": len(self.conversation_history),
            "api_available": OPENAI_AVAILABLE
        }

class ResponseFormatter:
    """Utility class for formatting chatbot responses."""
    
    @staticmethod
    def format_for_streamlit(response_data: Dict[str, Any]) -> str:
        """
        Format response for Streamlit display.
        
        Args:
            response_data: Response data from chatbot
            
        Returns:
            Formatted response string
        """
        response = response_data.get("response", "")
        
        if response_data.get("error"):
            return f"❌ **Erreur**: {response}"
        
        # Add metadata footer if available
        footer_parts = []
        
        if "sources_used" in response_data and response_data["sources_used"] > 0:
            footer_parts.append(f"📚 Sources consultées: {response_data['sources_used']}")
        
        if "token_usage" in response_data:
            tokens = response_data["token_usage"]["total_tokens"]
            footer_parts.append(f"🔤 Tokens utilisés: {tokens}")
        
        if footer_parts:
            footer = "\n\n---\n*" + " | ".join(footer_parts) + "*"
            return response + footer
        
        return response
    
    @staticmethod
    def extract_sources(search_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract source information from search results.
        
        Args:
            search_results: Search results from vector database
            
        Returns:
            List of source information
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

# Example usage
if __name__ == "__main__":
    # Initialize chatbot
    chatbot = ChatBot()
    
    # Example search results (would come from vector database)
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
    
    # Generate response
    response = chatbot.generate_response(
        user_question="Qu'est-ce que l'intelligence artificielle ?",
        search_results=example_search_results
    )
    
    print("Response:", response["response"])
    print("Tokens used:", response.get("token_usage", {}).get("total_tokens", "N/A"))
