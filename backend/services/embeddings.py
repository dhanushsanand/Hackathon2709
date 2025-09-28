import pinecone
import google.generativeai as genai
from typing import List, Dict, Any
import hashlib
import uuid
from config import settings

class EmbeddingService:
    def __init__(self):
        # Initialize Gemini (this doesn't require network connection)
        genai.configure(api_key=settings.gemini_api_key)
        
        # Pinecone will be initialized lazily
        self._pinecone_initialized = False
        self.index = None
    
    def _init_pinecone(self):
        """Initialize Pinecone connection lazily"""
        if self._pinecone_initialized:
            return
            
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            
            # Create or connect to index
            if settings.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.pinecone_index_name,
                    dimension=768,  # Gemini embedding dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(settings.pinecone_index_name)
            self._pinecone_initialized = True
            print("Pinecone initialized successfully")
            
        except Exception as e:
            print(f"Warning: Could not initialize Pinecone: {e}")
            print("Embeddings will work but won't be stored in vector database")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Gemini"""
        try:
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Fallback to simple text hashing if Gemini fails
            return self._fallback_embeddings(texts)
    
    def _fallback_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Simple fallback embedding using text hashing"""
        embeddings = []
        for text in texts:
            # Create a simple hash-based embedding
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to float values between -1 and 1
            embedding = [(b - 128) / 128.0 for b in hash_bytes[:100]]
            # Pad to match expected dimension (768 for Gemini)
            while len(embedding) < 768:
                embedding.extend(embedding[:min(len(embedding), 768 - len(embedding))])
            embeddings.append(embedding[:768])
        return embeddings
    
    async def store_embeddings(self, texts: List[str], pdf_id: str) -> List[str]:
        """Store embeddings in Pinecone and return IDs"""
        embeddings = await self.generate_embeddings(texts)
        
        # Try to initialize Pinecone if not already done
        self._init_pinecone()
        
        vectors = []
        embedding_ids = []
        
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            # Generate unique ID for each embedding
            embedding_id = f"{pdf_id}_{i}_{uuid.uuid4().hex[:8]}"
            embedding_ids.append(embedding_id)
            
            vectors.append({
                "id": embedding_id,
                "values": embedding,
                "metadata": {
                    "pdf_id": pdf_id,
                    "chunk_index": i,
                    "text": text[:500],  # Store first 500 chars as metadata
                    "full_text_hash": hashlib.md5(text.encode()).hexdigest()
                }
            })
        
        # Upsert vectors to Pinecone if available
        if self.index:
            try:
                self.index.upsert(vectors=vectors)
                print(f"Stored {len(vectors)} embeddings in Pinecone")
            except Exception as e:
                print(f"Error storing embeddings in Pinecone: {e}")
        else:
            print("Pinecone not available, embeddings generated but not stored")
            
        return embedding_ids
    
    async def similarity_search(self, query: str, pdf_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in the PDF"""
        # Try to initialize Pinecone if not already done
        self._init_pinecone()
        
        if not self.index:
            print("Pinecone not available, returning empty results")
            return []
        
        try:
            query_embedding = await self.generate_embeddings([query])
            
            results = self.index.query(
                vector=query_embedding[0],
                filter={"pdf_id": pdf_id},
                top_k=top_k,
                include_metadata=True
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata["text"],
                    "chunk_index": match.metadata["chunk_index"]
                }
                for match in results.matches
            ]
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []