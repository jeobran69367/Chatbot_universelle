"""
Vector database module for storing and retrieving embeddings.
This module handles the conversion of text to vectors and similarity search.
"""

import json
import logging
import pickle
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np
from dataclasses import dataclass
from datetime import datetime

# Import vector database libraries
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Import embedding libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import config with fallback
try:
    from config.settings import (
        EMBEDDINGS_DIR, CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_DB_TYPE
    )
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modèle par défaut disponible
except ImportError:
    # Fallback values if config import fails
    from pathlib import Path
    import os
    EMBEDDINGS_DIR = Path.cwd() / "data" / "embeddings"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    VECTOR_DB_TYPE = "chromadb"
    EMBEDDINGS_DIR = Path(__file__).parent.parent / "data" / "embeddings"
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = "text-embedding-ada-002"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    VECTOR_DB_TYPE = "chroma"

@dataclass
class DocumentChunk:
    """Data class for document chunks with metadata."""
    id: str
    content: str
    source_url: str
    title: str
    chunk_index: int
    embedding: Optional[np.ndarray] = None
    created_at: Optional[datetime] = None

class TextChunker:
    """Handles text chunking for better embedding performance."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger(__name__)
    
    def chunk_text(self, text: str, source_url: str = "", title: str = "") -> List[DocumentChunk]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            source_url: Source URL of the text
            title: Title of the document
            
        Returns:
            List of DocumentChunk objects
        """
        if len(text) <= self.chunk_size:
            return [DocumentChunk(
                id=f"{hash(source_url)}_{0}",
                content=text,
                source_url=source_url,
                title=title,
                chunk_index=0,
                created_at=datetime.now()
            )]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at word boundaries
            if end < len(text):
                while end > start + self.chunk_size * 0.8 and text[end] not in ' \n\t.!?;':
                    end -= 1
                if end <= start + self.chunk_size * 0.8:
                    end = start + self.chunk_size
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunks.append(DocumentChunk(
                    id=f"{hash(source_url)}_{chunk_index}",
                    content=chunk_content,
                    source_url=source_url,
                    title=title,
                    chunk_index=chunk_index,
                    created_at=datetime.now()
                ))
                chunk_index += 1
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        self.logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

class EmbeddingGenerator:
    """Generates embeddings using various models."""
    
    def __init__(self, model_type: str = "sentence-transformers"):
        """
        Initialize embedding generator.
        
        Args:
            model_type: Type of embedding model ('openai', 'sentence-transformers')
        """
        self.model_type = model_type
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        if model_type == "openai" and OPENAI_AVAILABLE:
            openai.api_key = OPENAI_API_KEY
            self.model = "openai"
        elif model_type == "sentence-transformers" and SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            raise ValueError(f"Model type {model_type} not available")
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.model_type == "openai":
            return self._generate_openai_embeddings(texts)
        else:
            return self._generate_sentence_transformer_embeddings(texts)
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using OpenAI API."""
        embeddings = []
        
        for text in texts:
            try:
                response = openai.Embedding.create(
                    model=EMBEDDING_MODEL,
                    input=text
                )
                embeddings.append(np.array(response['data'][0]['embedding']))
            except Exception as e:
                self.logger.error(f"Error generating OpenAI embedding: {e}")
                # Fallback to zero vector
                embeddings.append(np.zeros(1536))  # OpenAI embedding dimension
        
        return embeddings
    
    def _generate_sentence_transformer_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using Sentence Transformers."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb for emb in embeddings]
        except Exception as e:
            self.logger.error(f"Error generating Sentence Transformer embeddings: {e}")
            return [np.zeros(384) for _ in texts]  # MiniLM embedding dimension

class ChromaVectorDB:
    """ChromaDB implementation for vector storage."""
    
    def __init__(self, collection_name: str = "documents"):
        """Initialize ChromaDB client."""
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not available. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        try:
            # Créer le client avec l'embedding par défaut
            self.client = chromadb.PersistentClient(path=str(EMBEDDINGS_DIR / "chroma_db"))
            
            # Utiliser l'embedding par défaut de ChromaDB (all-MiniLM-L6-v2)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Utiliser la distance cosinus
            )
        except Exception as e:
            # Si ça échoue, essayer sans métadonnées
            self.client = chromadb.PersistentClient(path=str(EMBEDDINGS_DIR / "chroma_db"))
            self.collection = self.client.get_or_create_collection(name=collection_name)
        
        self.logger = logging.getLogger(__name__)
    
    def add_documents(self, chunks: List[DocumentChunk]):
        """Add document chunks to the vector database."""
        if not chunks:
            return
        
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [{
            'source_url': chunk.source_url,
            'title': chunk.title,
            'chunk_index': chunk.chunk_index,
            'created_at': chunk.created_at.isoformat() if chunk.created_at else None
        } for chunk in chunks]
        
        try:
            # ChromaDB génère automatiquement les embeddings
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            self.logger.info(f"Added {len(chunks)} documents to ChromaDB")
            
        except Exception as e:
            self.logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    }
                    formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error searching ChromaDB: {e}")
            return []

class FAISSVectorDB:
    """FAISS implementation for vector storage."""
    
    def __init__(self, dimension: int = 384):
        """Initialize FAISS index."""
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product similarity
        self.documents: List[DocumentChunk] = []
        self.logger = logging.getLogger(__name__)
        
        # Try to load existing index
        self.index_path = EMBEDDINGS_DIR / "faiss_index.bin"
        self.metadata_path = EMBEDDINGS_DIR / "faiss_metadata.pkl"
        self._load_index()
    
    def add_documents(self, chunks: List[DocumentChunk]):
        """Add document chunks to the FAISS index."""
        if not chunks:
            return
        
        embeddings = []
        for chunk in chunks:
            if chunk.embedding is not None:
                # Normalize embedding for cosine similarity
                embedding = chunk.embedding / np.linalg.norm(chunk.embedding)
                embeddings.append(embedding)
                self.documents.append(chunk)
        
        if embeddings:
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)
            self.logger.info(f"Added {len(embeddings)} documents to FAISS index")
            
            # Save index
            self._save_index()
    
    def search(self, query_embedding: np.ndarray, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using embedding.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        if self.index.ntotal == 0:
            return []
        
        # Normalize query embedding
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        distances, indices = self.index.search(query_embedding, min(n_results, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                chunk = self.documents[idx]
                result = {
                    'content': chunk.content,
                    'metadata': {
                        'source_url': chunk.source_url,
                        'title': chunk.title,
                        'chunk_index': chunk.chunk_index,
                        'created_at': chunk.created_at.isoformat() if chunk.created_at else None
                    },
                    'distance': float(distances[0][i])
                }
                results.append(result)
        
        return results
    
    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)
            self.logger.info("FAISS index saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving FAISS index: {e}")
    
    def _load_index(self):
        """Load FAISS index and metadata from disk."""
        try:
            if self.index_path.exists() and self.metadata_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'rb') as f:
                    self.documents = pickle.load(f)
                self.logger.info("FAISS index loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading FAISS index: {e}")

class VectorDatabase:
    """Main vector database interface."""
    
    def __init__(self, db_type: str = VECTOR_DB_TYPE):
        """
        Initialize vector database.
        
        Args:
            db_type: Type of vector database ('chroma', 'chromadb' or 'faiss')
        """
        self.db_type = db_type
        self.chunker = TextChunker()
        self.embedding_generator = EmbeddingGenerator("sentence-transformers")
        self.logger = logging.getLogger(__name__)
        
        # Initialize vector database
        if db_type in ["chroma", "chromadb"]:
            self.db = ChromaVectorDB()
        elif db_type == "faiss":
            self.db = FAISSVectorDB()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def add_documents_from_scraped_data(self, scraped_pages: List[Any]):
        """
        Add scraped web pages to the vector database.
        
        Args:
            scraped_pages: List of ScrapedPage objects
        """
        all_chunks = []
        
        for page in scraped_pages:
            # Chunk the text
            chunks = self.chunker.chunk_text(
                text=page.content,
                source_url=page.url,
                title=page.title
            )
            
            # Generate embeddings for chunks
            texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings(texts)
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
            
            all_chunks.extend(chunks)
        
        # Add to vector database
        self.db.add_documents(all_chunks)
        self.logger.info(f"Added {len(all_chunks)} chunks from {len(scraped_pages)} pages")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar content.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar documents with metadata
        """
        if self.db_type == "chroma":
            return self.db.search(query, n_results)
        elif self.db_type == "faiss":
            # Generate embedding for query
            query_embedding = self.embedding_generator.generate_embeddings([query])[0]
            return self.db.search(query_embedding, n_results)
        
        return []
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the vector database."""
        info = {
            'db_type': self.db_type,
            'embedding_model': self.embedding_generator.model_type,
            'chunk_size': self.chunker.chunk_size,
            'chunk_overlap': self.chunker.chunk_overlap
        }
        
        if self.db_type == "faiss" and hasattr(self.db, 'index'):
            info['total_vectors'] = self.db.index.ntotal
        
        return info

# Example usage
if __name__ == "__main__":
    # Create vector database
    vector_db = VectorDatabase("chroma")
    
    # Example: Add some test documents
    from web_scraper import ScrapedPage
    from datetime import datetime
    
    test_pages = [
        ScrapedPage(
            url="https://example.com/page1",
            title="Test Page 1",
            content="This is a test document about machine learning and artificial intelligence.",
            language="en",
            scraped_at=datetime.now(),
            links=[]
        )
    ]
    
    vector_db.add_documents_from_scraped_data(test_pages)
    
    # Search for similar content
    results = vector_db.search_similar("artificial intelligence", n_results=3)
    for result in results:
        print(f"Content: {result['content'][:100]}...")
        print(f"Source: {result['metadata'].get('source_url', 'Unknown')}")
        print(f"Distance: {result.get('distance', 'N/A')}")
        print("-" * 50)
