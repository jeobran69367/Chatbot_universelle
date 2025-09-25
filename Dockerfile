# Dockerfile multi-stage pour l'application Chatbot Web Scraper
# Optimisé pour production avec support Ollama et GPU

#==============================================================================
# Stage 1: Base Python avec dépendances système
#==============================================================================
FROM python:3.11-slim as base

# Métadonnées du conteneur
LABEL maintainer="votre-email@exemple.com"
LABEL description="Chatbot Web Scraper avec Ollama et ChromaDB"
LABEL version="1.0"

# Variables d'environnement pour optimiser Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système essentielles
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    gcc \
    g++ \
    make \
    cmake \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    # Dépendances pour ChromeDriver/Selenium
    chromium-browser \
    chromium-driver \
    # Nettoyage
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Créer utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app /app/data /app/logs \
    && chown -R app:app /app

#==============================================================================
# Stage 2: Installation des dépendances Python
#==============================================================================
FROM base as dependencies

# Copier les fichiers de dépendances
COPY requirements.txt /tmp/requirements.txt

# Mettre à jour pip et installer les dépendances
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Installation spécifique pour Ollama (optionnelle pour le client)
RUN pip install --no-cache-dir ollama

#==============================================================================
# Stage 3: Application finale
#==============================================================================
FROM dependencies as production

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=app:app . .

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p \
    /app/data/embeddings \
    /app/data/scraped \
    /app/data/models \
    /app/logs \
    /app/__blobstorage__ \
    && chown -R app:app /app

# Variables d'environnement pour l'application
ENV PYTHONPATH=/app \
    APP_ENV=production \
    STREAMLIT_SERVER_PORT=8501 \
    FLASK_PORT=5001 \
    # Configuration Ollama
    OLLAMA_HOST=http://localhost:11434 \
    OLLAMA_MODEL=llama3.1:latest \
    # Configuration ChromaDB
    CHROMA_DB_PATH=/app/data/embeddings \
    # Configuration Logging
    LOG_LEVEL=INFO \
    LOG_FILE=/app/logs/app.log

# Configurer ChromeDriver pour Selenium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    CHROME_BIN=/usr/bin/chromium-browser

# Passer à l'utilisateur non-root
USER app

# Ports exposés
EXPOSE 8501 5001

# Script de santé pour Docker
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/status || exit 1

# Script d'entrée par défaut
CMD ["python", "app.py"]

#==============================================================================
# Stage 4: Version avec Ollama intégré (optionnel)
#==============================================================================
FROM production as with-ollama

USER root

# Installer Ollama directement dans le conteneur
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Créer le script de démarrage
COPY <<EOF /app/start-with-ollama.sh
#!/bin/bash
set -e

echo "🚀 Démarrage du conteneur avec Ollama intégré..."

# Démarrer Ollama en arrière-plan
echo "🤖 Démarrage d'Ollama..."
ollama serve &
OLLAMA_PID=$!

# Attendre qu'Ollama soit prêt
echo "⏳ Attente d'Ollama..."
until curl -s http://localhost:11434/api/version >/dev/null 2>&1; do
    sleep 2
done

# Télécharger le modèle par défaut si pas déjà présent
echo "📥 Vérification du modèle Ollama..."
if ! ollama list | grep -q "llama3.1:latest"; then
    echo "📥 Téléchargement du modèle llama3.1:latest..."
    ollama pull llama3.1:latest
fi

echo "✅ Ollama prêt!"

# Démarrer l'application Python
echo "🐍 Démarrage de l'application Python..."
exec python app.py
EOF

RUN chmod +x /app/start-with-ollama.sh \
    && chown app:app /app/start-with-ollama.sh

USER app

# Commande pour la version avec Ollama
CMD ["/app/start-with-ollama.sh"]