#!/bin/bash
# Script de démarrage robuste pour le chatbot

set -e  # Arrêter le script en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Démarrage du Chatbot Web Scraper${NC}"
echo "========================================"

# Vérification de l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Environnement virtuel non trouvé!${NC}"
    echo "Créez d'abord l'environnement virtuel avec: python -m venv .venv"
    exit 1
fi

echo -e "${GREEN}✅ Environnement virtuel trouvé${NC}"

# Vérification de l'activation automatique
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Activation de l'environnement virtuel...${NC}"
    source .venv/bin/activate
fi

# Vérification des modules critiques
echo -e "${BLUE}🔍 Vérification des modules...${NC}"

python -c "
import sys
modules = ['streamlit', 'selenium', 'requests', 'bs4', 'chromadb', 'sentence_transformers']
missing = []

for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        missing.append(module)

if missing:
    print(f'\n❌ Modules manquants: {missing}')
    print('Installez-les avec: pip install -r requirements.txt')
    sys.exit(1)
else:
    print('\n🎉 Tous les modules sont disponibles!')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Échec de la vérification des modules${NC}"
    exit 1
fi

# Vérification d'Ollama
echo -e "${BLUE}🔍 Vérification d'Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama non trouvé. Assurez-vous qu'il est installé et démarré.${NC}"
else
    echo -e "${GREEN}✅ Ollama disponible${NC}"
    # Vérifier si le modèle est disponible
    if ollama list | grep -q "llama3.1:latest"; then
        echo -e "${GREEN}✅ Modèle llama3.1:latest disponible${NC}"
    else
        echo -e "${YELLOW}⚠️  Modèle llama3.1:latest non trouvé${NC}"
        echo "Téléchargez-le avec: ollama pull llama3.1:latest"
    fi
fi

# Vérification du port 8501
echo -e "${BLUE}🔍 Vérification du port 8501...${NC}"
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Le port 8501 est déjà utilisé${NC}"
    echo "Arrêtez l'application existante ou utilisez un autre port"
else
    echo -e "${GREEN}✅ Port 8501 disponible${NC}"
fi

# Lancement de Streamlit
echo -e "${GREEN}🚀 Lancement de Streamlit...${NC}"
echo ""

streamlit run app.py
