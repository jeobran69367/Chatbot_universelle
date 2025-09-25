#!/usr/bin/env python3
"""
Script de vérification et test d'Ollama pour le chatbot.
Ce script vérifie que Ollama est installé, configuré et fonctionne correctement.
"""

import sys
import requests
import json
import os
from typing import List, Dict, Any
import subprocess

def check_ollama_installation() -> bool:
    """Vérifie si Ollama est installé."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama installé : {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama n'est pas installé ou pas dans le PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama n'est pas installé ou pas accessible")
        return False

def check_ollama_server(host: str = "http://localhost:11434") -> bool:
    """Vérifie si le serveur Ollama est en cours d'exécution."""
    try:
        response = requests.get(f"{host}/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"✅ Serveur Ollama actif sur {host}")
            return True
        else:
            print(f"❌ Serveur Ollama non accessible (statut: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de se connecter au serveur Ollama : {e}")
        return False

def list_available_models(host: str = "http://localhost:11434") -> List[Dict[str, Any]]:
    """Liste les modèles Ollama disponibles."""
    try:
        response = requests.get(f"{host}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                print(f"✅ {len(models)} modèle(s) Ollama disponible(s) :")
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"  - {name} ({size_gb:.1f} GB)")
            else:
                print("⚠️ Aucun modèle Ollama installé")
            return models
        else:
            print(f"❌ Erreur lors de la récupération des modèles : {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion lors de la récupération des modèles : {e}")
        return []

def test_model_generation(model_name: str, host: str = "http://localhost:11434") -> bool:
    """Teste la génération de texte avec un modèle."""
    try:
        payload = {
            "model": model_name,
            "prompt": "Bonjour, peux-tu te présenter brièvement en français ?",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 100
            }
        }
        
        print(f"🧪 Test de génération avec le modèle {model_name}...")
        response = requests.post(f"{host}/api/generate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get("response", "").strip()
            if generated_text:
                print(f"✅ Génération réussie :")
                print(f"   {generated_text[:200]}...")
                return True
            else:
                print("❌ Aucun texte généré")
                return False
        else:
            print(f"❌ Erreur de génération : {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du test de génération : {e}")
        return False

def check_env_configuration() -> Dict[str, str]:
    """Vérifie la configuration du fichier .env."""
    env_path = ".env"
    config = {}
    
    if os.path.exists(env_path):
        print(f"✅ Fichier .env trouvé")
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
            
            ollama_host = config.get('OLLAMA_HOST', 'Non configuré')
            ollama_model = config.get('OLLAMA_MODEL', 'Non configuré')
            
            print(f"  - OLLAMA_HOST: {ollama_host}")
            print(f"  - OLLAMA_MODEL: {ollama_model}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du .env : {e}")
    else:
        print("⚠️ Fichier .env non trouvé")
        
    return config

def suggest_model_installation():
    """Suggère l'installation d'un modèle si aucun n'est disponible."""
    print("\n📥 Suggestions d'installation de modèles :")
    print("\nModèles recommandés :")
    print("  1. Pour usage général : ollama pull llama3.1")
    print("  2. Pour machines modestes : ollama pull phi3:mini")
    print("  3. Pour l'analyse de code : ollama pull codellama")
    print("\nPour installer un modèle :")
    print("  ollama pull <nom_du_modele>")

def suggest_server_start():
    """Suggère comment démarrer le serveur Ollama."""
    print("\n🚀 Pour démarrer le serveur Ollama :")
    print("  ollama serve")
    print("\nOu en arrière-plan :")
    print("  nohup ollama serve &")

def main():
    """Fonction principale de vérification."""
    print("🔍 Vérification de la configuration Ollama")
    print("=" * 50)
    
    # Vérification de l'installation
    ollama_installed = check_ollama_installation()
    
    # Configuration depuis .env
    config = check_env_configuration()
    host = config.get('OLLAMA_HOST', 'http://localhost:11434')
    preferred_model = config.get('OLLAMA_MODEL', 'llama3.1')
    
    # Vérification du serveur
    server_running = check_ollama_server(host)
    
    if not server_running and ollama_installed:
        suggest_server_start()
        return
    
    # Liste des modèles
    models = list_available_models(host) if server_running else []
    
    if not models and server_running:
        suggest_model_installation()
        return
    
    # Test du modèle préféré
    if models and server_running:
        model_names = [model["name"] for model in models]
        
        # Chercher le modèle préféré
        test_model = None
        for model_name in model_names:
            if preferred_model in model_name:
                test_model = model_name
                break
        
        # Si pas trouvé, utiliser le premier disponible
        if not test_model:
            test_model = model_names[0]
            print(f"⚠️ Modèle préféré '{preferred_model}' non trouvé, utilisation de '{test_model}'")
        
        # Test de génération
        generation_ok = test_model_generation(test_model, host)
        
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DE LA VÉRIFICATION")
        print("=" * 50)
        print(f"Ollama installé : {'✅' if ollama_installed else '❌'}")
        print(f"Serveur actif : {'✅' if server_running else '❌'}")
        print(f"Modèles disponibles : {'✅' if models else '❌'}")
        print(f"Génération de texte : {'✅' if generation_ok else '❌'}")
        
        if ollama_installed and server_running and models and generation_ok:
            print("\n🎉 Configuration Ollama parfaite ! Votre chatbot est prêt.")
        else:
            print("\n⚠️ Configuration incomplète. Consultez le guide OLLAMA_SETUP.md")

if __name__ == "__main__":
    main()
