#!/bin/bash
# Script de déploiement sur Azure avec azd
# Usage: ./scripts/deploy/azure-deploy.sh [environment]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENVIRONMENT=${1:-dev}

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis Azure..."
    
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI n'est pas installé"
        log_info "Installez avec: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        exit 1
    fi
    
    if ! command -v azd &> /dev/null; then
        log_error "Azure Developer CLI (azd) n'est pas installé"
        log_info "Installez avec: curl -fsSL https://aka.ms/install-azd.sh | bash"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier la connexion Azure
    if ! az account show &> /dev/null; then
        log_warning "Non connecté à Azure, connexion en cours..."
        az login
    fi
    
    log_success "Prérequis Azure validés"
}

# Configuration de l'environnement Azure
setup_azure_environment() {
    log_info "Configuration de l'environnement Azure ($ENVIRONMENT)..."
    
    cd "$PROJECT_ROOT"
    
    # Initialiser azd si nécessaire
    if [ ! -f .azure/$ENVIRONMENT/.env ]; then
        log_info "Initialisation de l'environnement azd..."
        azd env new "$ENVIRONMENT"
    fi
    
    # Configuration des variables d'environnement
    azd env select "$ENVIRONMENT"
    
    # Variables par défaut
    azd env set AZURE_ENV_NAME "$ENVIRONMENT"
    azd env set AZURE_LOCATION "${AZURE_LOCATION:-eastus}"
    
    # Variables spécifiques à l'application
    azd env set APP_VERSION "$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')"
    azd env set CONTAINER_IMAGE "chatbot-web-scraper:$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')"
    
    log_success "Environnement Azure configuré"
}

# Provisioning de l'infrastructure
provision_infrastructure() {
    log_info "Provisioning de l'infrastructure Azure..."
    
    # Vérifier si l'infrastructure existe déjà
    if azd env get-values | grep -q "AZURE_RESOURCE_GROUP"; then
        log_info "Infrastructure existante détectée"
        read -p "Voulez-vous reprovisioner l'infrastructure? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Provisioning ignoré"
            return
        fi
    fi
    
    # Exécuter le provisioning
    azd provision --no-prompt
    
    log_success "Infrastructure provisionnée"
}

# Construction et push de l'image Docker
build_and_push_image() {
    log_info "Construction et push de l'image Docker..."
    
    # Récupérer les informations du registry
    local registry_name=$(azd env get-values | grep "AZURE_CONTAINER_REGISTRY_NAME" | cut -d'=' -f2 | tr -d '"')
    local registry_endpoint=$(azd env get-values | grep "AZURE_CONTAINER_REGISTRY_ENDPOINT" | cut -d'=' -f2 | tr -d '"')
    local image_tag=$(azd env get-values | grep "CONTAINER_IMAGE" | cut -d'=' -f2 | tr -d '"')
    
    if [ -z "$registry_endpoint" ]; then
        log_error "Registry endpoint non trouvé. Vérifiez le provisioning."
        exit 1
    fi
    
    # Login au registry
    log_info "Connexion à Azure Container Registry..."
    az acr login --name "$registry_name"
    
    # Construction de l'image
    log_info "Construction de l'image Docker..."
    docker build -t "$registry_endpoint/$image_tag" .
    
    # Push de l'image
    log_info "Push de l'image vers le registry..."
    docker push "$registry_endpoint/$image_tag"
    
    log_success "Image construite et poussée"
}

# Déploiement de l'application
deploy_application() {
    log_info "Déploiement de l'application..."
    
    azd deploy --no-prompt
    
    log_success "Application déployée"
}

# Test de l'application déployée
test_deployment() {
    log_info "Test du déploiement..."
    
    local app_url=$(azd env get-values | grep "AZURE_CONTAINER_APP_URL" | cut -d'=' -f2 | tr -d '"')
    
    if [ -z "$app_url" ]; then
        log_warning "URL de l'application non trouvée"
        return
    fi
    
    log_info "Test de l'application sur $app_url"
    
    # Test de santé avec retry
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$app_url/api/status" > /dev/null 2>&1; then
            log_success "Application accessible et fonctionnelle!"
            break
        fi
        
        log_info "Test $attempt/$max_attempts - Attente du démarrage..."
        sleep 30
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_warning "L'application met du temps à démarrer. Vérifiez manuellement."
    fi
}

# Affichage des informations de déploiement
show_deployment_info() {
    local app_url=$(azd env get-values | grep "AZURE_CONTAINER_APP_URL" | cut -d'=' -f2 | tr -d '"')
    local resource_group=$(azd env get-values | grep "AZURE_RESOURCE_GROUP" | cut -d'=' -f2 | tr -d '"')
    local location=$(azd env get-values | grep "AZURE_LOCATION" | cut -d'=' -f2 | tr -d '"')
    
    echo
    log_success "🎉 Déploiement Azure terminé!"
    echo
    echo "📋 Informations du déploiement:"
    echo "   🌍 Environnement:       $ENVIRONMENT"
    echo "   📍 Région:              $location"
    echo "   📦 Resource Group:      $resource_group"
    echo "   🌐 URL Application:     $app_url"
    echo "   🔌 API Status:          $app_url/api/status"
    echo
    echo "🛠️  Commandes utiles:"
    echo "   azd monitor             # Voir les métriques de monitoring"
    echo "   azd logs                # Voir les logs de l'application"
    echo "   azd down                # Supprimer toute l'infrastructure"
    echo "   az portal               # Ouvrir le portail Azure"
    echo
    echo "📊 Monitoring:"
    echo "   - Application Insights configuré"
    echo "   - Logs centralisés dans Log Analytics"
    echo "   - Redis Cache pour les sessions"
    echo "   - Stockage persistant configuré"
}

# Fonction principale
main() {
    echo "🚀 Déploiement Azure Chatbot Web Scraper"
    echo "========================================"
    echo "Environnement: $ENVIRONMENT"
    echo
    
    check_prerequisites
    setup_azure_environment
    provision_infrastructure
    build_and_push_image
    deploy_application
    test_deployment
    show_deployment_info
}

# Gestion des erreurs
trap 'log_error "Erreur lors du déploiement Azure. Vérifiez les logs avec: azd logs"' ERR

# Exécution
main "$@"
