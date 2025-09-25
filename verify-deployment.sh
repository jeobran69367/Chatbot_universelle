#!/bin/bash
# Script de vérification finale du déploiement
# Usage: ./verify-deployment.sh [local|azure]

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOYMENT_TYPE=${1:-local}

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

check_file_exists() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        log_success "$description trouvé: $file"
        return 0
    else
        log_error "$description manquant: $file"
        return 1
    fi
}

check_directory_exists() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        log_success "$description trouvé: $dir"
        return 0
    else
        log_warning "$description manquant: $dir"
        return 1
    fi
}

verify_local_deployment() {
    log_info "🏠 Vérification du déploiement local..."
    
    local errors=0
    
    # Vérification des fichiers essentiels
    check_file_exists "Dockerfile" "Dockerfile" || errors=$((errors+1))
    check_file_exists "docker-compose.yml" "Docker Compose" || errors=$((errors+1))
    check_file_exists "requirements.txt" "Requirements Python" || errors=$((errors+1))
    check_file_exists ".env.example" "Template environnement" || errors=$((errors+1))
    check_file_exists "nginx/nginx.conf" "Configuration Nginx" || errors=$((errors+1))
    
    # Vérification des répertoires
    check_directory_exists "src" "Code source"
    check_directory_exists "config" "Configuration"
    check_directory_exists "scripts/deploy" "Scripts de déploiement"
    
    # Vérification Docker
    if command -v docker &> /dev/null; then
        log_success "Docker installé"
        if docker-compose config > /dev/null 2>&1; then
            log_success "Docker Compose configuration valide"
        else
            log_error "Configuration Docker Compose invalide"
            errors=$((errors+1))
        fi
    else
        log_error "Docker non installé"
        errors=$((errors+1))
    fi
    
    # Test de connectivité (si déployé)
    if docker-compose ps | grep -q "Up"; then
        log_info "Services Docker en cours d'exécution"
        
        if curl -sf http://localhost/api/status > /dev/null 2>&1; then
            log_success "Application accessible sur http://localhost"
        else
            log_warning "Application non accessible (peut être en cours de démarrage)"
        fi
    else
        log_info "Services Docker non démarrés (utilisez 'make up' pour démarrer)"
    fi
    
    return $errors
}

verify_azure_deployment() {
    log_info "☁️ Vérification du déploiement Azure..."
    
    local errors=0
    
    # Vérification des fichiers Azure
    check_file_exists "azure.yaml" "Configuration AZD" || errors=$((errors+1))
    check_file_exists "infra/main.bicep" "Infrastructure Bicep" || errors=$((errors+1))
    check_file_exists "infra/main.parameters.json" "Paramètres Bicep" || errors=$((errors+1))
    check_file_exists ".github/workflows/deploy.yml" "Pipeline CI/CD" || errors=$((errors+1))
    
    # Vérification Azure CLI
    if command -v az &> /dev/null; then
        log_success "Azure CLI installé"
        if az account show > /dev/null 2>&1; then
            log_success "Connecté à Azure"
            subscription=$(az account show --query name -o tsv)
            log_info "Subscription active: $subscription"
        else
            log_warning "Non connecté à Azure (utilisez 'az login')"
        fi
    else
        log_error "Azure CLI non installé"
        errors=$((errors+1))
    fi
    
    # Vérification AZD
    if command -v azd &> /dev/null; then
        log_success "Azure Developer CLI installé"
        
        if azd env list > /dev/null 2>&1; then
            log_success "Environnements AZD configurés"
            azd env list
        else
            log_info "Aucun environnement AZD configuré"
        fi
    else
        log_error "Azure Developer CLI non installé"
        errors=$((errors+1))
    fi
    
    # Test de l'application déployée (si disponible)
    if command -v azd &> /dev/null && azd env get-values > /dev/null 2>&1; then
        app_url=$(azd env get-values | grep "AZURE_CONTAINER_APP_URL" | cut -d'=' -f2 | tr -d '"')
        if [ -n "$app_url" ]; then
            log_info "URL de l'application: $app_url"
            if curl -sf "$app_url/api/status" > /dev/null 2>&1; then
                log_success "Application Azure accessible"
            else
                log_warning "Application Azure non accessible"
            fi
        else
            log_info "Application non encore déployée sur Azure"
        fi
    fi
    
    return $errors
}

show_quick_start() {
    echo
    log_info "🚀 Guide de Démarrage Rapide"
    echo "=============================="
    
    if [ "$DEPLOYMENT_TYPE" = "local" ]; then
        echo "Déploiement Local:"
        echo "  1. make setup              # Configuration initiale"
        echo "  2. cp .env.example .env    # Copier configuration"
        echo "  3. make up                 # Démarrer l'application"
        echo "  4. make health             # Vérifier l'état"
        echo
        echo "URLs utiles:"
        echo "  - Application: http://localhost"
        echo "  - API: http://localhost/api/status"
        echo "  - Monitoring: make monitor"
    else
        echo "Déploiement Azure:"
        echo "  1. az login                # Connexion Azure"
        echo "  2. make deploy-azure       # Déploiement complet"
        echo "  3. make logs-azure         # Voir les logs"
        echo "  4. make health             # Vérifier l'état"
        echo
        echo "CI/CD GitHub Actions:"
        echo "  - Configurez les secrets Azure dans GitHub"
        echo "  - Push sur main/develop pour déclencher le déploiement"
    fi
    
    echo
    echo "Documentation complète: DEPLOYMENT.md"
}

main() {
    echo "🔍 Vérification du Déploiement Chatbot Web Scraper"
    echo "=================================================="
    echo "Type: $DEPLOYMENT_TYPE"
    echo
    
    if [ "$DEPLOYMENT_TYPE" = "azure" ]; then
        verify_azure_deployment
        azure_errors=$?
    else
        verify_local_deployment  
        local_errors=$?
    fi
    
    echo
    echo "📊 Résumé de la Vérification"
    echo "============================="
    
    if [ "$DEPLOYMENT_TYPE" = "azure" ]; then
        if [ $azure_errors -eq 0 ]; then
            log_success "Configuration Azure prête pour le déploiement!"
        else
            log_warning "Quelques problèmes détectés ($azure_errors)"
        fi
    else
        if [ $local_errors -eq 0 ]; then
            log_success "Configuration locale prête pour le déploiement!"
        else
            log_warning "Quelques problèmes détectés ($local_errors)"
        fi
    fi
    
    show_quick_start
}

case "$1" in
    local|azure)
        main
        ;;
    -h|--help)
        echo "Usage: $0 [local|azure]"
        echo "  local  - Vérifier la configuration locale"
        echo "  azure  - Vérifier la configuration Azure"
        exit 0
        ;;
    *)
        log_info "Type de déploiement non spécifié, vérification locale par défaut"
        main
        ;;
esac
