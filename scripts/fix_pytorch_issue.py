#!/usr/bin/env python3
"""
Diagnostic et solution pour le problème PyTorch/sentence-transformers.
Ce script identifie la cause et propose des solutions.
"""

import sys
import os
from pathlib import Path

def diagnose_pytorch_issue():
    """Diagnostic du problème PyTorch."""
    print("🔍 Diagnostic du problème PyTorch/sentence-transformers")
    print("=" * 60)
    
    try:
        import torch
        print(f"✅ PyTorch installé: {torch.__version__}")
        
        # Vérifier CUDA
        if torch.cuda.is_available():
            print(f"✅ CUDA disponible: {torch.version.cuda}")
        else:
            print("⚠️ CUDA non disponible (CPU seulement)")
        
        # Vérifier MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ MPS (Apple Silicon) disponible")
        else:
            print("⚠️ MPS non disponible")
            
        # Test simple de tensor
        x = torch.rand(2, 3)
        print(f"✅ Test tensor basique réussi: {x.shape}")
        
    except Exception as e:
        print(f"❌ Erreur PyTorch: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers importé")
        
        # Test avec un modèle très léger
        print("🧪 Test de chargement d'un modèle léger...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Modèle sentence-transformers chargé")
        
        # Test d'encoding simple
        sentences = ["Test simple"]
        embeddings = model.encode(sentences)
        print(f"✅ Encoding réussi: {embeddings.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur sentence-transformers: {e}")
        return False

def create_alternative_embedding():
    """Créer une alternative d'embedding sans sentence-transformers."""
    print("\n🔧 Création d'une solution alternative...")
    
    alternative_code = '''"""
Alternative d'embedding sans sentence-transformers.
Utilise des méthodes plus simples et robustes.
"""

import numpy as np
import re
from typing import List
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimpleEmbeddingGenerator:
    """Générateur d'embeddings simple sans dépendances lourdes."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=384,  # Dimension compatible avec sentence-transformers
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.is_fitted = False
    
    def preprocess_text(self, text: str) -> str:
        """Préprocessing simple du texte."""
        # Nettoyer le texte
        text = re.sub(r'[^a-zA-ZÀ-ÿ0-9\\s]', ' ', text)
        text = re.sub(r'\\s+', ' ', text).strip()
        return text.lower()
    
    def fit_texts(self, texts: List[str]):
        """Entraîner le vectoriseur sur un corpus de textes."""
        processed_texts = [self.preprocess_text(text) for text in texts]
        self.vectorizer.fit(processed_texts)
        self.is_fitted = True
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Générer des embeddings pour une liste de textes."""
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        if not self.is_fitted:
            # Auto-fit si pas encore fait
            self.fit_texts(processed_texts)
        
        # Générer les vecteurs TF-IDF
        embeddings = self.vectorizer.transform(processed_texts).toarray()
        
        # Normaliser les vecteurs
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Éviter la division par zéro
        normalized_embeddings = embeddings / norms
        
        return normalized_embeddings
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Interface compatible avec sentence-transformers."""
        return self.generate_embeddings(texts)

class FallbackEmbedding:
    """Embedding de fallback ultra-simple."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Génère des embeddings déterministes basés sur le hash du texte."""
        embeddings = []
        
        for text in texts:
            # Utiliser le hash du texte pour générer un vecteur reproductible
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Convertir le hash en vecteur de dimension fixe
            vector = []
            for i in range(0, min(len(text_hash), self.dimension // 16)):
                chunk = text_hash[i*2:(i+1)*2]
                vector.extend([int(chunk, 16) / 255.0] * 16)
            
            # Compléter ou tronquer à la bonne dimension
            if len(vector) < self.dimension:
                vector.extend([0.0] * (self.dimension - len(vector)))
            else:
                vector = vector[:self.dimension]
            
            # Normaliser le vecteur
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = np.array(vector) / norm
            else:
                vector = np.random.randn(self.dimension)
                vector = vector / np.linalg.norm(vector)
            
            embeddings.append(vector)
        
        return np.array(embeddings)
'''
    
    # Écrire le code alternatif
    alternative_path = Path(__file__).parent.parent / "src" / "alternative_embedding.py"
    with open(alternative_path, 'w', encoding='utf-8') as f:
        f.write(alternative_code)
    
    print(f"✅ Solution alternative créée: {alternative_path}")
    return alternative_path

def main():
    success = diagnose_pytorch_issue()
    
    if not success:
        print("\n🛠️ Création d'une solution de contournement...")
        alternative_path = create_alternative_embedding()
        
        print(f"""
⚠️ PyTorch/sentence-transformers a des problèmes sur votre système.

✅ SOLUTION CRÉÉE: {alternative_path}

📝 Pour utiliser la solution alternative:

1. Modifiez src/vector_database.py pour utiliser SimpleEmbeddingGenerator
2. Ou installez des versions compatibles:
   
   pip uninstall torch sentence-transformers
   pip install torch==2.0.1 sentence-transformers==2.2.2
   
3. Ou utilisez ChromaDB avec son embedding par défaut (recommandé)

🎯 La solution la plus simple: utiliser ChromaDB sans embedding personnalisé.
""")
    else:
        print("\n🎉 PyTorch et sentence-transformers fonctionnent correctement!")

if __name__ == "__main__":
    main()
