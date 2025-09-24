#!/bin/bash
# Script de démarrage pour le Chatbot Web Scraper

echo "🤖 Démarrage du Chatbot Web Scraper..."

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier que le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Le fichier .env n'existe pas. Création d'un fichier par défaut..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "📝 Veuillez modifier le fichier .env avec votre clé API OpenAI"
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers de données..."
mkdir -p data/scraped data/embeddings data/models

# Lancer l'application
echo "🚀 Lancement de l'application Streamlit..."
streamlit run app.py

echo "✅ Application démarrée avec succès!"
