#!/bin/bash
# Script pour lancer l'application Streamlit avec le bon environnement Python

echo "🚀 Lancement du Chatbot avec Ollama"
echo "======================================"

# Vérifier qu'Ollama est actif
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️ Ollama ne semble pas être actif."
    echo "💡 Démarrez Ollama avec: ollama serve"
    exit 1
fi

echo "✅ Ollama est actif"

# Aller dans le répertoire du projet
cd "$(dirname "$0")"

# Lancer Streamlit avec le bon environnement Python
echo "🌐 Lancement de l'interface web..."
./.venv/bin/streamlit run app.py
