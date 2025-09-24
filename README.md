# 🤖 Chatbot Web Scraper Intelligent

Un chatbot intelligent capable de scraper des sites web, vectoriser le contenu et répondre aux questions en utilisant OpenAI et des techniques de RAG (Retrieval Augmented Generation).

## ✨ Fonctionnalités

- 🕷️ **Web Scraping Avancé**: Scrape automatiquement un site web et toutes ses pages liées
- 🧠 **Intelligence Artificielle**: Utilise OpenAI GPT pour générer des réponses contextuelles
- 📊 **Base de Données Vectorielle**: Stocke et recherche efficacement dans le contenu scrapé
- 🎨 **Interface Intuitive**: Interface web moderne avec Streamlit
- 🔍 **Recherche Sémantique**: Trouve le contenu pertinent pour chaque question
- 💬 **Conversation Contextuelle**: Maintient l'historique des conversations

## 🛠️ Technologies Utilisées

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT, Sentence Transformers
- **Web Scraping**: BeautifulSoup, Selenium, Requests
- **Base de Données Vectorielle**: ChromaDB ou FAISS
- **Traitement de Texte**: NLTK, spaCy, LangChain
- **Langages**: Python 3.8+

## 📦 Installation

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd Model
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement
Copiez le fichier `.env` et ajustez les valeurs :
```bash
cp .env.example .env
```

Modifiez le fichier `.env` avec vos clés API :
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Lancer l'application
```bash
streamlit run app.py
```

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
├── config/
│   └── settings.py       # Configuration de l'application
├── src/
│   ├── web_scraper.py    # Module de scraping web
│   ├── vector_database.py # Base de données vectorielle
│   └── chatbot.py        # Intégration OpenAI
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

### Modèles OpenAI

```python
OPENAI_MODEL = "gpt-3.5-turbo"  # ou "gpt-4"
EMBEDDING_MODEL = "text-embedding-ada-002"
```

## 🔧 Personnalisation

### Ajouter de Nouvelles Sources de Données

```python
# Dans web_scraper.py
def scrape_api_data(api_url):
    # Implémentez votre logique de scraping d'API
    pass
```

### Modifier le Prompt Système

```python
# Dans chatbot.py
chatbot = ChatBot()
chatbot.set_system_prompt("Votre nouveau prompt système...")
```

### Changer de Base de Données Vectorielle

```python
# Utiliser FAISS au lieu de ChromaDB
vector_db = VectorDatabase("faiss")
```

## 🐛 Dépannage

### Erreurs Communes

1. **Erreur d'API OpenAI** : Vérifiez votre clé API dans le fichier `.env`
2. **Erreur de Selenium** : Installez ChromeDriver ou utilisez `use_selenium=False`
3. **Problèmes de mémoire** : Réduisez `MAX_PAGES_PER_SITE` ou `CHUNK_SIZE`

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
- Token limit OpenAI (4K pour GPT-3.5-turbo)
- Pas de mise à jour automatique du contenu

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- OpenAI pour les modèles GPT et les embeddings
- L'équipe Streamlit pour l'interface utilisateur
- La communauté ChromaDB pour la base de données vectorielle
- Tous les contributeurs des librairies open-source utilisées

## 📞 Support

Pour des questions ou du support :
- Ouvrez une issue sur GitHub
- Consultez la documentation des modules individuels
- Vérifiez les logs d'application

---

**Développé avec ❤️ pour l'intelligence artificielle et la recherche sémantique.**
