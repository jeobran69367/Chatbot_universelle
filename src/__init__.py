# Initilization file for the src package
"""
Chatbot Web Scraper Package

This package provides a complete solution for web scraping, 
text vectorization, and intelligent question answering using OpenAI.

Modules:
- web_scraper: Web scraping functionality
- vector_database: Vector storage and similarity search
- chatbot: OpenAI integration and response generation
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .web_scraper import WebScraper, ScrapedPage
from .vector_database import VectorDatabase, DocumentChunk
from .chatbot import ChatBot, ResponseFormatter

__all__ = [
    "WebScraper",
    "ScrapedPage", 
    "VectorDatabase",
    "DocumentChunk",
    "ChatBot",
    "ResponseFormatter"
]
