# 🤖 Chatbot Web Scraper Intelligent

Un chatbot intelligent capable de scraper des sites web, vectoriser le contenu et répondre aux questions en utilisant **Ollama** (LLaMA, Mistral, etc.) et des techniques de RAG (Retrieval Augmented Generation) - **100% local et privé**.

## 🚀 **DÉPLOIEMENT PROFESSIONNEL DOCKER + AZURE** 

Ce projet est maintenant équipé d'une **infrastructure complète de déploiement** :
- 🐳 **Docker & Docker Compose** pour le développement local
- ☁️ **Azure Container Apps** pour la production 
- 🔄 **CI/CD Pipeline GitHub Actions** 
- 📊 **Monitoring intégré** (Prometheus, Grafana, Application Insights)
- 🛡️ **Sécurité et bonnes pratiques**

## ✨ Fonctionnalités

- 🕷️ **Web Scraping Avancé**: Scrape automatiquement un site web et toutes ses pages liées
- 🧠 **Intelligence Artificielle Locale**: Utilise Ollama avec LLaMA 3.1, Mistral ou d'autres modèles open-source
- 📊 **Base de Données Vectorielle**: Stocke et recherche efficacement dans le contenu scrapé
- 🎨 **Interface Intuitive**: Interface web moderne avec Streamlit + API Flask
- 🔍 **Recherche Sémantique**: Trouve le contenu pertinent pour chaque question
- 💬 **Conversation Contextuelle**: Maintient l'historique des conversations
- 🔒 **100% Privé**: Toutes les données restent en local, aucune API externe requise
- 🎭 **Prompts Personnalisables**: Styles de réponse adaptables (défaut, expert, casual)
- 🔄 **Cache Redis** : Performance optimisée avec cache distribué
- 📈 **Monitoring complet** : Métriques, logs centralisés, alertes

## 🛠️ Technologies Utilisées

### Stack Application
- **Frontend**: Streamlit + API Flask
- **AI/ML**: Ollama (LLaMA, Mistral, etc.), Sentence Transformers
- **Web Scraping**: BeautifulSoup, Selenium, Requests, Scrapy
- **Base de Données Vectorielle**: ChromaDB ou FAISS
- **Cache**: Redis pour sessions et performance
- **Traitement de Texte**: NLTK, spaCy, LangChain
- **Langages**: Python 3.11+

### Stack Infrastructure
- **🐳 Containerisation**: Docker, Docker Compose
- **☁️ Cloud**: Azure Container Apps, Azure Storage, Redis Cache
- **🔄 CI/CD**: GitHub Actions, Azure DevOps
- **📊 Monitoring**: Application Insights, Prometheus, Grafana
- **🛡️ Sécurité**: Managed Identity, Key Vault, HTTPS/TLS
- **🏗️ IaC**: Azure Bicep, Azure Developer CLI (azd)

## � Démarrage Rapide

### ⚡ Installation & Déploiement Ultra-Rapide

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd Model

# 2. Configuration initiale complète
make setup

# 3. Déploiement local avec Docker
make up

# 4. Vérifier que tout fonctionne
make health
```

**🌐 Application disponible sur http://localhost**

---

## �📦 Installation Détaillée

### 🐳 Option A : Déploiement Docker (Recommandé)

```bash
# Configuration et déploiement en une commande
make setup && make up

# Avec monitoring (Prometheus + Grafana)
make deploy-local-monitoring

# Accès aux services
# - Application: http://localhost
# - API: http://localhost/api
# - Grafana: http://localhost:3000 (admin/admin123)
# - Prometheus: http://localhost:9090
```

### ☁️ Option B : Déploiement Azure

```bash
# Prérequis: Azure CLI + azd installés
az login

# Déploiement complet sur Azure
make deploy-azure

# URL générée automatiquement: https://votre-app.azurecontainerapps.io
```

### 🛠️ Option C : Installation Manuelle

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd Model
```

### 2. Créer un environnement virtuel
```bash
python -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate  # Sur Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Installer et configurer Ollama

**Sur macOS:**
```bash
# Installer Ollama
brew install ollama

# Ou télécharger depuis https://ollama.ai/download
curl -fsSL https://ollama.ai/install.sh | sh
```

**Sur Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Sur Windows:**
- Téléchargez l'installateur depuis [https://ollama.ai/download](https://ollama.ai/download)
- Exécutez l'installateur et suivez les instructions

### 5. Démarrer Ollama et télécharger un modèle
```bash
# Démarrer le service Ollama (si pas auto-démarré)
ollama serve

# Dans un nouveau terminal, télécharger le modèle LLaMA 3.1
ollama pull llama3.1:latest

# Optionnel: Télécharger des modèles plus légers
ollama pull qwen2:0.5b    # Modèle très léger (500MB)
ollama pull mistral:7b    # Modèle Mistral (4.1GB)

# Vérifier les modèles installés
ollama list
```

### 6. Configuration des variables d'environnement
Créez un fichier `.env` à la racine du projet :
```bash
cp .env.example .env
```

Modifiez le fichier `.env` avec vos configurations :
```env
# Configuration Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:latest

# Configuration Streamlit (optionnel)
STREAMLIT_THEME_BASE=light
STREAMLIT_THEME_PRIMARY_COLOR=#FF6B6B
STREAMLIT_THEME_BACKGROUND_COLOR=#FFFFFF
```

### 7. Lancer l'application

**🔍 Vérification rapide avant de commencer :**
```bash
# Vérifier qu'Ollama fonctionne
ollama list

# Tester un modèle
ollama run llama3.1:latest "Bonjour, comment ça va ?"

# Vérifier l'environnement Python
source .venv/bin/activate
python -c "import streamlit, chromadb, sentence_transformers; print('✅ Tous les modules OK')"
```

**Option 1 : Avec l'environnement virtuel activé**
```bash
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate  # Sur Windows
streamlit run app.py
```

**Option 2 : Directement avec le chemin complet**
```bash
./.venv/bin/streamlit run app.py  # Sur macOS/Linux
# ou
.venv\Scripts\streamlit run app.py  # Sur Windows
```

**Option 3 : Script de démarrage automatique**
```bash
chmod +x start_chatbot.sh
./start_chatbot.sh
```

**🚀 Accès à l'application :**
- Interface web : http://localhost:8501
- L'application se lance automatiquement dans votre navigateur

## 🚀 Utilisation

### Interface Web

1. **Scraping d'un Site Web**:
   - Entrez l'URL du site dans la sidebar
   - Configurez le nombre maximum de pages
   - Choisissez d'utiliser Selenium si nécessaire
   - Cliquez sur "Lancer le Scraping"

2. **Poser des Questions**:
   - Tapez votre question dans la zone de texte
   - Le chatbot utilisera le contenu scrapé pour répondre
   - Les sources utilisées sont affichées dans la sidebar

3. **Gestion des Données**:
   - Consultez l'onglet "Données" pour voir les informations scrapées
   - Chargez des données existantes si disponibles

### Utilisation Programmatique

```python
from src.web_scraper import WebScraper
from src.vector_database import VectorDatabase
from src.chatbot import ChatBot

# 1. Scraper un site web
scraper = WebScraper()
pages = scraper.scrape_website("https://example.com", max_pages=20)

# 2. Créer la base de données vectorielle
vector_db = VectorDatabase("chroma")
vector_db.add_documents_from_scraped_data(pages)

# 3. Initialiser le chatbot
chatbot = ChatBot()

# 4. Poser une question
search_results = vector_db.search_similar("ma question", n_results=5)
response = chatbot.generate_response("ma question", search_results)
print(response["response"])
```

## 📁 Structure du Projet

```
Model/
├── app.py                 # Interface Streamlit principale
├── requirements.txt       # Dépendances Python
├── .env                  # Variables d'environnement
├── README.md             # Documentation
├── start_chatbot.sh      # Script de démarrage automatique
├── config/
│   ├── settings.py       # Configuration de l'application
│   └── prompts.py        # Configuration des prompts système
├── src/
│   ├── web_scraper.py    # Module de scraping web
│   ├── vector_database.py # Base de données vectorielle
│   ├── chatbot.py        # Intégration Ollama
│   └── robust_vector_db.py # Solution robuste ChromaDB
└── data/                 # Données scrapées et modèles
    ├── scraped/          # Données JSON brutes
    ├── embeddings/       # Base de données vectorielle
    └── models/           # Modèles téléchargés
```

## ⚙️ Configuration Avancée

### Paramètres de Scraping

Dans `config/settings.py` :

```python
MAX_PAGES_PER_SITE = 100    # Limite de pages par site
REQUEST_DELAY = 1           # Délai entre les requêtes (secondes)
MAX_RETRIES = 3             # Nombre de tentatives
TIMEOUT = 30                # Timeout des requêtes
```

### Paramètres de Vectorisation

```python
CHUNK_SIZE = 1000           # Taille des chunks de texte
CHUNK_OVERLAP = 200         # Chevauchement entre chunks
SIMILARITY_THRESHOLD = 0.7  # Seuil de similarité
```

### Modèles Ollama

```python
# Configuration dans .env ou directement
OLLAMA_MODEL = "llama3.1:latest"  # Modèle par défaut
OLLAMA_MODEL = "mistral:7b"       # Modèle Mistral
OLLAMA_MODEL = "qwen2:0.5b"       # Modèle léger pour tests
```

**Modèles recommandés :**
- `llama3.1:latest` - Excellent équilibre performance/qualité (4.6GB)
- `mistral:7b` - Très bon pour le français (4.1GB)
- `qwen2:0.5b` - Ultra-léger pour développement (500MB)
- `codellama:latest` - Spécialisé en programmation (3.8GB)

## 🔧 Personnalisation

### Ajouter de Nouvelles Sources de Données

```python
# Dans web_scraper.py
def scrape_api_data(api_url):
    # Implémentez votre logique de scraping d'API
    pass
```

### Modifier le Prompt Système

**Option 1: Via l'interface Streamlit**
- Utilisez le sélecteur "Style de réponse" dans la sidebar
- Styles disponibles: `default`, `expert`, `casual`

**Option 2: Par programmation**
```python
# Dans chatbot.py
chatbot = ChatBot(prompt_style="expert")  # Style au démarrage

# Ou changer dynamiquement
chatbot.set_system_prompt(style="casual")
chatbot.set_system_prompt("Votre prompt personnalisé...")
```

**Option 3: Personnalisation avancée**
Modifiez le fichier `config/prompts.py` pour ajouter vos propres styles de prompts.

### Changer de Base de Données Vectorielle

```python
# Utiliser FAISS au lieu de ChromaDB
vector_db = VectorDatabase("faiss")
```

## 🐛 Dépannage

### Erreurs Communes

1. **Erreur de connexion Ollama** : 
   - Vérifiez qu'Ollama est démarré : `ollama serve`
   - Vérifiez le modèle : `ollama list`
   - Redémarrez Ollama si nécessaire

2. **Modèle non trouvé** :
   ```bash
   ollama pull llama3.1:latest
   ```

3. **Erreur de Selenium** : 
   - Installez ChromeDriver ou utilisez `use_selenium=False`
   - Sur macOS : `brew install chromedriver`

4. **Problèmes de mémoire** : 
   - Réduisez `MAX_PAGES_PER_SITE` ou `CHUNK_SIZE`
   - Utilisez un modèle plus léger comme `qwen2:0.5b`

5. **Port 11434 occupé** :
   ```bash
   # Arrêter Ollama
   killall ollama
   # Redémarrer
   ollama serve
   ```

### Logs de Debug

Pour activer les logs détaillés :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Métriques et Performance

### Optimisations Recommandées

- Utilisez FAISS pour de gros volumes de données
- Ajustez `CHUNK_SIZE` selon votre contenu
- Utilisez un cache Redis pour les embeddings fréquents
- Implémentez une pagination pour l'interface web

### Limites Actuelles

- Maximum 100 pages par site (configurable)
- Limite de contexte Ollama (variable selon le modèle)
- Pas de mise à jour automatique du contenu
- Nécessite Ollama en local (peut être déployé en remote)

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Ollama** pour l'infrastructure d'IA locale
- **Meta AI** pour les modèles LLaMA
- **Mistral AI** pour les modèles Mistral
- L'équipe **Streamlit** pour l'interface utilisateur
- La communauté **ChromaDB** pour la base de données vectorielle
- Tous les contributeurs des librairies open-source utilisées

## � Commandes Make Utiles

| Commande | Description |
|----------|-------------|
| `make help` | Afficher toutes les commandes disponibles |
| `make setup` | Configuration initiale complète |
| `make up` | Démarrer l'application localement |
| `make deploy-azure` | Déployer sur Azure |
| `make logs` | Voir les logs en temps réel |
| `make health` | Vérifier l'état de l'application |
| `make clean` | Nettoyer les fichiers temporaires |
| `make backup` | Sauvegarder les données |

## 📋 Architecture de Production

```
                    ┌─────────────────┐
                    │   GitHub Repo   │
                    │   (CI/CD Push)  │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │ GitHub Actions  │
                    │ (Build & Deploy)│
                    └─────────┬───────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │            Azure Container Apps           │
        │  ┌─────────────────┐ ┌─────────────────┐ │
        │  │   Streamlit     │ │    Ollama       │ │
        │  │   (Port 8501)   │ │  (Port 11434)   │ │
        │  └─────────────────┘ └─────────────────┘ │
        │  ┌─────────────────┐ ┌─────────────────┐ │
        │  │   Flask API     │ │   ChromaDB      │ │
        │  │   (Port 5001)   │ │  (Embeddings)   │ │
        │  └─────────────────┘ └─────────────────┘ │
        └─────────────────────┬─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │  ┌─────────────────┐│┌─────────────────┐  │
        │  │  Azure Storage  │││   Redis Cache   │  │
        │  │  (Persistent)   │││   (Sessions)    │  │
        │  └─────────────────┘│└─────────────────┘  │
        │  ┌─────────────────┐│┌─────────────────┐  │
        │  │App Insights     │││  Log Analytics  │  │
        │  │(Monitoring)     │││    (Logs)       │  │
        │  └─────────────────┘│└─────────────────┘  │
        └──────────────────────────────────────────┘
```

## 🔗 Liens Utiles

- 📖 **Documentation complète** : [DEPLOYMENT.md](./DEPLOYMENT.md)
- 🐳 **Guide Docker** : Voir `docker-compose.yml`
- ☁️ **Configuration Azure** : Voir `infra/main.bicep`
- 🔄 **Pipeline CI/CD** : Voir `.github/workflows/`
- 📊 **Monitoring** : Voir `monitoring/prometheus.yml`

## �📞 Support

Pour des questions ou du support :
- 📋 **Ouvrez une issue** sur GitHub
- 📖 **Consultez** `DEPLOYMENT.md` pour les détails de déploiement
- 🔍 **Vérifiez les logs** : `make logs` (local) ou `make logs-azure` (Azure)
- 🏥 **Status santé** : `make health`

## 🆕 Nouveautés v2.0

- ✅ **Déploiement Docker complet** avec orchestration
- ✅ **Infrastructure Azure** automatisée avec Bicep
- ✅ **CI/CD Pipeline** GitHub Actions
- ✅ **Monitoring intégré** (Prometheus, Grafana, App Insights)
- ✅ **Cache Redis** pour améliorer les performances
- ✅ **Sécurité renforcée** (Managed Identity, HTTPS)
- ✅ **Scripts automatisés** pour simplifier le déploiement
- ✅ **Documentation complète** et guides d'utilisation

---

**Développé avec ❤️ pour l'intelligence artificielle, la recherche sémantique et l'infrastructure moderne.**

🚀 **Prêt pour la production - Scalable - Sécurisé - Monitored**
