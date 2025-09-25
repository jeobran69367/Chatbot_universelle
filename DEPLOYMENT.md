# 🚀 Guide de Déploiement - Chatbot Web Scraper

Ce guide vous explique comment déployer votre application Chatbot Web Scraper avec Docker et Azure Container Apps.

## 📋 Table des Matières

1. [Architecture](#architecture)
2. [Prérequis](#prérequis)
3. [Déploiement Local](#déploiement-local)
4. [Déploiement Azure](#déploiement-azure)
5. [Configuration CI/CD](#configuration-cicd)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

### Stack Technologique
- **🐍 Backend**: Python 3.11 + Streamlit + Flask
- **🤖 IA**: Ollama (LLaMA 3.1) pour les réponses intelligentes
- **🗄️ Base Vectorielle**: ChromaDB pour la recherche sémantique
- **🕷️ Web Scraping**: Selenium + BeautifulSoup + Scrapy
- **🔄 Cache**: Redis pour les sessions et cache
- **🐳 Containerisation**: Docker + Docker Compose
- **☁️ Cloud**: Azure Container Apps + Azure Storage + Redis Cache

### Architecture Déployée

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  Container App   │────│   Redis Cache   │
│   Load Balancer │    │  (Streamlit +    │    │   (Sessions)    │
└─────────────────┘    │   Flask + Ollama)│    └─────────────────┘
                       └──────────────────┘              
                                │                         
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Azure Storage   │────│  Log Analytics  │
                       │  (Embeddings +   │    │  (Monitoring)   │
                       │   Scraped Data)  │    └─────────────────┘
                       └──────────────────┘              
```

## 🛠️ Prérequis

### Outils Requis

```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Azure Developer CLI (azd)
curl -fsSL https://aka.ms/install-azd.sh | bash

# Git (si pas déjà installé)
sudo apt install git -y
```

### Comptes et Permissions
- ✅ Compte Azure avec subscription active
- ✅ Permissions pour créer des ressources (Contributor)
- ✅ GitHub account pour CI/CD
- ✅ Docker Hub account (optionnel)

## 🏠 Déploiement Local

### 1. Préparation

```bash
# Cloner le projet
git clone <votre-repo>
cd chatbot-web-scraper

# Copier la configuration
cp .env.example .env

# Éditer les variables si nécessaire
nano .env
```

### 2. Déploiement Simple

```bash
# Déploiement avec script automatisé
./scripts/deploy/local-deploy.sh

# Ou déploiement manuel
docker-compose up -d
```

### 3. Déploiement avec Monitoring

```bash
# Inclure Prometheus + Grafana
./scripts/deploy/local-deploy.sh --with-monitoring
```

### 4. Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| 🌐 Application | http://localhost | Interface Streamlit |
| 🔌 API | http://localhost/api | API Flask |
| 🤖 Ollama | http://localhost:11434 | Service IA |
| 📊 Redis | localhost:6379 | Cache |
| 📈 Prometheus | http://localhost:9090 | Métriques |
| 📊 Grafana | http://localhost:3000 | Dashboards |

## ☁️ Déploiement Azure

### 1. Configuration Initiale

```bash
# Connexion à Azure
az login

# Sélectionner la subscription
az account set --subscription "Votre-Subscription-ID"

# Vérifier la configuration
az account show
```

### 2. Déploiement Automatisé

```bash
# Déploiement complet avec script
./scripts/deploy/azure-deploy.sh dev

# Ou pour production
./scripts/deploy/azure-deploy.sh prod
```

### 3. Déploiement Manuel avec azd

```bash
# Initialiser l'environnement
azd auth login
azd init

# Configurer l'environnement
azd env new dev
azd env set AZURE_LOCATION eastus

# Déployer
azd up
```

### 4. Variables d'Environnement Azure

Les variables suivantes seront configurées automatiquement :

```bash
AZURE_CONTAINER_APP_URL=https://your-app.azurecontainerapps.io
AZURE_STORAGE_ACCOUNT=your-storage-account
AZURE_REDIS_CACHE_HOSTNAME=your-redis.redis.cache.windows.net
APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string
```

## 🔄 Configuration CI/CD

### 1. Secrets GitHub

Configurez ces secrets dans votre repository GitHub :

```bash
# Settings > Secrets and Variables > Actions

AZURE_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id  
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### 2. Variables d'Environnement

```bash
# Settings > Secrets and Variables > Actions > Variables

AZURE_LOCATION=eastus
AZURE_ENV_NAME=prod
```

### 3. Activation OIDC

```bash
# Créer l'identité managée pour GitHub Actions
az ad app create --display-name "GitHub-Actions-ChatBot"

# Configurer la fédération OIDC
az ad app federated-credential create \
  --id <app-id> \
  --parameters @federated-credential.json
```

### 4. Workflows Disponibles

| Workflow | Trigger | Description |
|----------|---------|-------------|
| 🧪 test.yml | Pull Requests | Tests et qualité code |
| 🚀 deploy.yml | Push main/develop | Déploiement automatique |

## 📊 Monitoring & Maintenance

### Logs et Debugging

```bash
# Logs en local
docker-compose logs -f chatbot-app

# Logs sur Azure
azd logs --follow
az containerapp logs show --name <app-name> --resource-group <rg-name>
```

### Métriques Importantes

- **CPU/Memory Usage** : < 80%
- **Response Time** : < 2 secondes
- **Error Rate** : < 1%
- **Ollama Model Loading** : Vérifier la mémoire

### Commandes de Maintenance

```bash
# Redémarrage local
docker-compose restart chatbot-app

# Redémarrage Azure
az containerapp revision restart --name <app-name> --resource-group <rg-name>

# Scaling Azure
az containerapp update --name <app-name> --resource-group <rg-name> \
  --min-replicas 1 --max-replicas 5
```

## 🔧 Troubleshooting

### Problèmes Fréquents

#### 1. Ollama ne démarre pas
```bash
# Vérifier les ressources
docker stats
# Solution : Augmenter la mémoire du conteneur
```

#### 2. ChromaDB corruption
```bash
# Réinitialiser la base vectorielle
rm -rf data/embeddings/chroma_db
docker-compose restart chatbot-app
```

#### 3. Selenium ne fonctionne pas
```bash
# Vérifier ChromeDriver
docker-compose exec chatbot-app which chromedriver
# Solution : Vérifier la variable CHROMEDRIVER_PATH
```

#### 4. Application lente au démarrage
```bash
# Cause : Téléchargement modèle Ollama
# Solution : Pre-pull du modèle ou augmenter timeout
```

### Logs de Debug

```bash
# Activer le debug
export LOG_LEVEL=DEBUG
docker-compose up -d

# Logs détaillés Azure
az monitor activity-log list --resource-group <rg-name>
```

### Support et Contact

- 📧 **Issues** : Créer une issue GitHub
- 📖 **Documentation** : Voir `/docs/`
- 🔍 **Monitoring** : Application Insights sur Azure

---

## 🚀 Commandes Rapides

```bash
# Déploiement local rapide
./scripts/deploy/local-deploy.sh

# Déploiement Azure rapide  
./scripts/deploy/azure-deploy.sh prod

# Tests complets
docker-compose exec chatbot-app python -m pytest

# Backup des données
docker-compose exec chatbot-app tar -czf /tmp/backup.tar.gz /app/data
```

---

*Dernière mise à jour : $(date '+%Y-%m-%d')*
