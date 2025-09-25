# Configuration file for the Chatbot
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
SCRAPED_DATA_DIR = DATA_DIR / "scraped"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, EMBEDDINGS_DIR, SCRAPED_DATA_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"  # ou "mistral", "codellama", etc.
EMBEDDING_MODEL = "all-minilm"  # Modèle d'embedding local

# Scraping Configuration
MAX_PAGES_PER_SITE = 100  # Limit to prevent infinite crawling
REQUEST_DELAY = 1  # Seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"  # or "faiss"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SIMILARITY_THRESHOLD = 0.7

# Streamlit Configuration
PAGE_TITLE = "Chatbot Web Scraper"
PAGE_ICON = "🤖"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
