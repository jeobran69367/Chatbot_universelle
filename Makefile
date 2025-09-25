# Makefile pour Chatbot Web Scraper
# Simplifie les commandes de développement et déploiement

.PHONY: help install dev build test clean deploy-local deploy-azure logs status

# Variables
PROJECT_NAME := chatbot-web-scraper
DOCKER_IMAGE := $(PROJECT_NAME):latest
AZURE_ENV := dev

# Couleurs pour l'affichage
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

help: ## Afficher l'aide
	@echo "$(BLUE)🚀 Chatbot Web Scraper - Commandes Disponibles$(NC)"
	@echo "=================================================="
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Installer les dépendances Python localement
	@echo "$(BLUE)📦 Installation des dépendances...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dépendances installées$(NC)"

dev: ## Démarrer l'environnement de développement
	@echo "$(BLUE)🔧 Démarrage environnement de développement...$(NC)"
	python -m streamlit run app.py --server.port 8501 &
	python api_server.py &
	@echo "$(GREEN)✅ Environnement de dev démarré$(NC)"
	@echo "   🌐 Streamlit: http://localhost:8501"
	@echo "   🔌 API: http://localhost:5001"

build: ## Construire l'image Docker
	@echo "$(BLUE)🏗️ Construction de l'image Docker...$(NC)"
	docker build -t $(DOCKER_IMAGE) .
	@echo "$(GREEN)✅ Image construite: $(DOCKER_IMAGE)$(NC)"

test: ## Exécuter les tests
	@echo "$(BLUE)🧪 Exécution des tests...$(NC)"
	mkdir -p tests data/embeddings data/scraped
	export PYTHONPATH=$$PWD && python -m pytest tests/ -v || echo "$(YELLOW)⚠️ Créez des tests dans tests/$(NC)"
	@echo "$(GREEN)✅ Tests terminés$(NC)"

lint: ## Vérifier la qualité du code
	@echo "$(BLUE)🔍 Vérification qualité du code...$(NC)"
	black --check src/ config/ *.py || echo "$(YELLOW)⚠️ Utilisez 'make format' pour corriger$(NC)"
	flake8 src/ config/ --max-line-length=100 --ignore=E203,W503 || echo "$(YELLOW)⚠️ Problèmes de linting détectés$(NC)"
	@echo "$(GREEN)✅ Vérification terminée$(NC)"

format: ## Formater le code avec Black
	@echo "$(BLUE)🎯 Formatage du code...$(NC)"
	black src/ config/ *.py
	@echo "$(GREEN)✅ Code formaté$(NC)"

security: ## Scanner les vulnérabilités
	@echo "$(BLUE)🔒 Scan de sécurité...$(NC)"
	bandit -r src/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "$(GREEN)✅ Scan terminé - Vérifiez les rapports$(NC)"

clean: ## Nettoyer les fichiers temporaires
	@echo "$(BLUE)🧹 Nettoyage...$(NC)"
	docker system prune -f
	rm -rf __pycache__ .pytest_cache .coverage htmlcov/
	rm -rf data/embeddings/chroma_db data/scraped/*.json
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

deploy-local: build ## Déployer localement avec Docker Compose
	@echo "$(BLUE)🏠 Déploiement local...$(NC)"
	./scripts/deploy/local-deploy.sh
	@echo "$(GREEN)✅ Déploiement local terminé$(NC)"

deploy-local-monitoring: build ## Déployer localement avec monitoring
	@echo "$(BLUE)🏠 Déploiement local avec monitoring...$(NC)"
	./scripts/deploy/local-deploy.sh --with-monitoring
	@echo "$(GREEN)✅ Déploiement local avec monitoring terminé$(NC)"

deploy-azure: ## Déployer sur Azure Container Apps
	@echo "$(BLUE)☁️ Déploiement Azure ($(AZURE_ENV))...$(NC)"
	./scripts/deploy/azure-deploy.sh $(AZURE_ENV)
	@echo "$(GREEN)✅ Déploiement Azure terminé$(NC)"

deploy-azure-prod: ## Déployer sur Azure en production
	@echo "$(BLUE)☁️ Déploiement Azure Production...$(NC)"
	./scripts/deploy/azure-deploy.sh prod
	@echo "$(GREEN)✅ Déploiement Production terminé$(NC)"

logs: ## Afficher les logs (local)
	@echo "$(BLUE)📋 Logs de l'application...$(NC)"
	docker-compose logs -f chatbot-app

logs-azure: ## Afficher les logs Azure
	@echo "$(BLUE)📋 Logs Azure...$(NC)"
	azd logs --follow

status: ## Vérifier le statut des services
	@echo "$(BLUE)📊 Statut des services...$(NC)"
	@echo "Local Docker:"
	docker-compose ps
	@echo "\nAzure:"
	azd env get-values | grep -E "(URL|STATUS)" || echo "Pas de déploiement Azure détecté"

restart: ## Redémarrer l'application locale
	@echo "$(BLUE)🔄 Redémarrage...$(NC)"
	docker-compose restart chatbot-app
	@echo "$(GREEN)✅ Application redémarrée$(NC)"

stop: ## Arrêter tous les services locaux
	@echo "$(BLUE)⏹️ Arrêt des services...$(NC)"
	docker-compose down
	pkill -f "streamlit\|api_server.py" || true
	@echo "$(GREEN)✅ Services arrêtés$(NC)"

backup: ## Sauvegarder les données locales
	@echo "$(BLUE)💾 Sauvegarde des données...$(NC)"
	mkdir -p backups
	tar -czf backups/data-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/
	@echo "$(GREEN)✅ Sauvegarde créée dans backups/$(NC)"

restore: ## Restaurer les données depuis la dernière sauvegarde
	@echo "$(BLUE)🔄 Restauration des données...$(NC)"
	@latest_backup=$$(ls -t backups/data-backup-*.tar.gz 2>/dev/null | head -1); \
	if [ -n "$$latest_backup" ]; then \
		tar -xzf "$$latest_backup"; \
		echo "$(GREEN)✅ Données restaurées depuis $$latest_backup$(NC)"; \
	else \
		echo "$(RED)❌ Aucune sauvegarde trouvée$(NC)"; \
	fi

setup: ## Configuration initiale complète
	@echo "$(BLUE)🚀 Configuration initiale...$(NC)"
	@echo "1. Copie de la configuration..."
	cp .env.example .env
	@echo "2. Création des répertoires..."
	mkdir -p data/{embeddings,scraped,models} logs nginx/ssl
	@echo "3. Installation des dépendances..."
	$(MAKE) install
	@echo "4. Construction Docker..."
	$(MAKE) build
	@echo "$(GREEN)✅ Configuration terminée!$(NC)"
	@echo "$(YELLOW)⚠️ Éditez .env avant de déployer$(NC)"

health: ## Vérifier la santé de l'application
	@echo "$(BLUE)🔍 Vérification de santé...$(NC)"
	@curl -sf http://localhost/api/status > /dev/null 2>&1 && \
		echo "$(GREEN)✅ Application locale en ligne$(NC)" || \
		echo "$(RED)❌ Application locale hors ligne$(NC)"
	@azd env get-values 2>/dev/null | grep -q "AZURE_CONTAINER_APP_URL" && \
		curl -sf $$(azd env get-values | grep "AZURE_CONTAINER_APP_URL" | cut -d'=' -f2 | tr -d '"')/api/status > /dev/null 2>&1 && \
		echo "$(GREEN)✅ Application Azure en ligne$(NC)" || \
		echo "$(YELLOW)⚠️ Application Azure non déployée ou hors ligne$(NC)"

monitor: ## Ouvrir les dashboards de monitoring
	@echo "$(BLUE)📊 Ouverture monitoring...$(NC)"
	@echo "Local:"
	@echo "  - Grafana: http://localhost:3000 (admin/admin123)"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "Azure:"
	@app_url=$$(azd env get-values 2>/dev/null | grep "AZURE_CONTAINER_APP_URL" | cut -d'=' -f2 | tr -d '"'); \
	if [ -n "$$app_url" ]; then \
		echo "  - Application: $$app_url"; \
		echo "  - Portal Azure: https://portal.azure.com"; \
	else \
		echo "  - Pas de déploiement Azure détecté"; \
	fi

# Alias pratiques
up: deploy-local ## Alias pour deploy-local
down: stop ## Alias pour stop
ps: status ## Alias pour status
