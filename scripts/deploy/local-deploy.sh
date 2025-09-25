#!/bin/bash
# Script de déploiement local avec Docker Compose
# Usage: ./scripts/deploy/local-deploy.sh [--with-monitoring]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"

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
    log_info "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    log_success "Prérequis validés"
}

# Préparation de l'environnement
setup_environment() {
    log_info "Préparation de l'environnement..."
    
    cd "$PROJECT_ROOT"
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Fichier .env non trouvé, création depuis .env.example"
        cp .env.example .env
    fi
    
    # Créer les répertoires nécessaires
    mkdir -p data/{embeddings,scraped,models} logs nginx/ssl
    
    # Générer un mot de passe Redis s'il n'existe pas
    if ! grep -q "REDIS_PASSWORD=" .env; then
        REDIS_PASS=$(openssl rand -base64 32)
        echo "REDIS_PASSWORD=$REDIS_PASS" >> .env
        log_info "Mot de passe Redis généré"
    fi
    
    log_success "Environnement préparé"
}

# Construction et démarrage des services
deploy_services() {
    local with_monitoring=$1
    
    log_info "Construction et démarrage des services..."
    
    # Arrêter les services existants
    docker-compose down --remove-orphans
    
    # Construire l'image de l'application
    log_info "Construction de l'image Docker..."
    docker-compose build chatbot-app
    
    # Démarrer les services core
    if [ "$with_monitoring" = "true" ]; then
        log_info "Démarrage avec monitoring..."
        docker-compose --profile monitoring up -d
    else
        log_info "Démarrage des services principaux..."
        docker-compose up -d chatbot-app ollama redis nginx
    fi
    
    log_success "Services démarrés"
}

# Vérification de l'état des services
check_services() {
    log_info "Vérification de l'état des services..."
    
    # Attendre que les services soient prêts
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep -q "Up"; then
            break
        fi
        
        log_info "Tentative $attempt/$max_attempts - Attente des services..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    # Afficher l'état des services
    echo
    log_info "État des services:"
    docker-compose ps
    
    echo
    log_info "Logs récents:"
    docker-compose logs --tail=20
}

# Test de connectivité
test_connectivity() {
    log_info "Test de connectivité..."
    
    local app_url="http://localhost"
    local api_url="http://localhost/api/status"
    
    # Attendre que l'application soit prête
    local max_attempts=20
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$api_url" > /dev/null 2>&1; then
            log_success "Application accessible sur $app_url"
            break
        fi
        
        log_info "Test $attempt/$max_attempts - Application en cours de démarrage..."
        sleep 15
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_warning "L'application met du temps à démarrer, vérifiez les logs"
    fi
}

# Affichage des informations de déploiement
show_deployment_info() {
    echo
    log_success "🎉 Déploiement local terminé!"
    echo
    echo "📋 Informations de connexion:"
    echo "   🌐 Application Streamlit: http://localhost"
    echo "   🔌 API Flask:           http://localhost/api"
    echo "   🤖 Ollama:              http://localhost:11434"
    echo "   📊 Redis:               localhost:6379"
    
    if docker-compose ps | grep -q "prometheus"; then
        echo "   📈 Prometheus:          http://localhost:9090"
        echo "   📊 Grafana:             http://localhost:3000"
    fi
    
    echo
    echo "🛠️  Commandes utiles:"
    echo "   docker-compose logs -f chatbot-app  # Voir les logs de l'app"
    echo "   docker-compose down                 # Arrêter tous les services"
    echo "   docker-compose restart chatbot-app  # Redémarrer l'app"
    echo "   docker-compose exec chatbot-app bash # Accéder au conteneur"
}

# Fonction principale
main() {
    local with_monitoring=false
    
    # Parser les arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-monitoring)
                with_monitoring=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [--with-monitoring]"
                echo "  --with-monitoring  Démarrer avec Prometheus et Grafana"
                exit 0
                ;;
            *)
                log_error "Option inconnue: $1"
                exit 1
                ;;
        esac
    done
    
    echo "🚀 Déploiement Local Chatbot Web Scraper"
    echo "========================================"
    
    check_prerequisites
    setup_environment
    deploy_services "$with_monitoring"
    check_services
    test_connectivity
    show_deployment_info
}

# Gestion des erreurs
trap 'log_error "Erreur lors du déploiement. Vérifiez les logs avec: docker-compose logs"' ERR

# Exécution
main "$@"
