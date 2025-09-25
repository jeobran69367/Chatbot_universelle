# Configuration d'Ollama pour le Chatbot

Ce guide vous explique comment installer et configurer Ollama pour utiliser votre chatbot avec des modèles IA locaux.

## Qu'est-ce qu'Ollama ?

Ollama est un outil qui permet d'exécuter facilement des modèles de langage (LLM) en local sur votre machine. Contrairement à OpenAI qui nécessite une clé API et une connexion internet, Ollama fonctionne entièrement hors ligne.

## 1. Installation d'Ollama

### Sur macOS

```bash
# Téléchargez et installez Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

Ou téléchargez directement depuis le site officiel : https://ollama.ai

### Sur Windows

1. Téléchargez l'installateur depuis https://ollama.ai
2. Exécutez le fichier `.exe` téléchargé
3. Suivez l'assistant d'installation

### Sur Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 2. Vérification de l'installation

```bash
# Vérifiez qu'Ollama est installé
ollama --version

# Démarrez le service Ollama
ollama serve
```

Le serveur Ollama sera accessible sur `http://localhost:11434`

## 3. Installation des modèles

### Modèles recommandés pour ce chatbot

#### Llama 3.1 (Recommandé - 4.7GB)
```bash
ollama pull llama3.1
```

#### Alternatives selon vos ressources

**Pour machines puissantes (RAM > 16GB) :**
```bash
# Llama 3.1 8B (plus performant - 4.7GB)
ollama pull llama3.1:8b

# Llama 3.1 13B (excellent - 7.3GB)
ollama pull llama3.1:13b
```

**Pour machines plus modestes (RAM < 8GB) :**
```bash
# Phi-3 Mini (très léger - 2.3GB)
ollama pull phi3:mini

# Gemma 2B (léger - 1.4GB)
ollama pull gemma:2b
```

**Pour le code et l'analyse technique :**
```bash
# CodeLlama (spécialisé code - 3.8GB)
ollama pull codellama
```

### Vérifier les modèles installés

```bash
ollama list
```

## 4. Configuration du chatbot

### Fichier `.env`

Assurez-vous que votre fichier `.env` contient :

```env
# Configuration Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Ces anciennes variables OpenAI ne sont plus nécessaires
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-3.5-turbo
```

### Fichier `config/settings.py`

Vérifiez que la configuration utilise bien Ollama :

```python
# Configuration Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
```

## 5. Test de fonctionnement

### Test direct d'Ollama

```bash
# Testez directement Ollama
ollama run llama3.1 "Bonjour, peux-tu te présenter ?"
```

### Test via l'API REST

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Pourquoi utiliser Ollama ?",
  "stream": false
}'
```

### Test avec votre chatbot

```bash
# Lancez l'application
python app.py
```

## 6. Gestion des modèles

### Lister les modèles disponibles
```bash
ollama list
```

### Supprimer un modèle
```bash
ollama rm nom_du_modele
```

### Mettre à jour un modèle
```bash
ollama pull nom_du_modele
```

## 7. Résolution de problèmes

### Ollama ne démarre pas

```bash
# Arrêtez Ollama
pkill ollama

# Redémarrez le service
ollama serve
```

### Port 11434 déjà utilisé

```bash
# Changez le port dans votre .env
OLLAMA_HOST=http://localhost:11435

# Démarrez Ollama sur un autre port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

### Modèle non trouvé

```bash
# Vérifiez les modèles installés
ollama list

# Installez le modèle manquant
ollama pull llama3.1
```

### Erreur de mémoire

Si vous avez des erreurs de mémoire :

1. **Utilisez un modèle plus petit :**
   ```bash
   ollama pull phi3:mini
   ```
   
   Puis modifiez votre `.env` :
   ```env
   OLLAMA_MODEL=phi3:mini
   ```

2. **Fermez d'autres applications** consommatrices de mémoire

3. **Augmentez la mémoire virtuelle** de votre système

## 8. Comparaison des modèles

| Modèle | Taille | RAM requise | Performance | Usage recommandé |
|--------|--------|-------------|-------------|------------------|
| `phi3:mini` | 2.3GB | 4GB+ | Correcte | Machines modestes |
| `gemma:2b` | 1.4GB | 3GB+ | Basique | Tests rapides |
| `llama3.1` | 4.7GB | 8GB+ | Excellente | Usage général |
| `llama3.1:13b` | 7.3GB | 16GB+ | Supérieure | Machines puissantes |
| `codellama` | 3.8GB | 6GB+ | Spécialisée | Analyse de code |

## 9. Avantages d'Ollama vs OpenAI

### ✅ Avantages d'Ollama
- **Gratuit** - Aucun coût d'API
- **Privé** - Vos données restent locales
- **Hors ligne** - Fonctionne sans internet
- **Rapide** - Pas de latence réseau
- **Contrôle total** - Choisissez votre modèle

### ⚠️ Limitations
- Nécessite plus de ressources locales
- Qualité peut être inférieure aux modèles les plus récents
- Installation et configuration plus complexe

## 10. Commandes utiles

```bash
# Voir les modèles disponibles au téléchargement
ollama search

# Informations détaillées sur un modèle
ollama show llama3.1

# Arrêter Ollama
ollama stop

# Logs d'Ollama (sur macOS)
tail -f ~/.ollama/logs/server.log
```

## Configuration terminée !

Une fois Ollama installé et configuré, votre chatbot utilisera les modèles locaux pour générer des réponses intelligentes sans dépendre d'APIs externes.
