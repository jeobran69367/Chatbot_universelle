@echo off
REM Script de démarrage pour le Chatbot Web Scraper (Windows)

echo 🤖 Démarrage du Chatbot Web Scraper...

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Veuillez l'installer d'abord.
    pause
    exit /b 1
)

REM Vérifier que l'environnement virtuel existe
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dépendances
echo 📚 Installation des dépendances...
pip install -r requirements.txt

REM Vérifier que le fichier .env existe
if not exist ".env" (
    echo ⚠️  Le fichier .env n'existe pas. Création d'un fichier par défaut...
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo 📝 Veuillez modifier le fichier .env avec votre clé API OpenAI
)

REM Créer les dossiers nécessaires
echo 📁 Création des dossiers de données...
if not exist "data\scraped" mkdir data\scraped
if not exist "data\embeddings" mkdir data\embeddings
if not exist "data\models" mkdir data\models

REM Lancer l'application
echo 🚀 Lancement de l'application Streamlit...
streamlit run app.py

echo ✅ Application démarrée avec succès!
pause
