from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
from typing import List, Dict, Any
import hashlib
import uuid
import socket
from config import settings

class EmbeddingService:
    def __init__(self):
        # Initialize Gemini (this doesn't require network connection)
        genai.configure(api_key=settings.gemini_api_key)
        
        # Pinecone will be initialized lazily
        self._pinecone_initialized = False
        self.pc = None
        self.index = None
    
    def _init_pinecone(self):
        """Initialize Pinecone connection lazily with modern API"""
        if self._pinecone_initialized:
            return
            
        try:
            # Test network connectivity first
            try:
                socket.gethostbyname('api.pinecone.io')
                print("✅ Network connectivity to Pinecone confirmed")
            except socket.gaierror as e:
                print(f"❌ Network connectivity issue: {e}")
                print("💡 Cannot resolve Pinecone hostname. Check your internet connection or DNS settings.")
                print("📝 Continuing in test mode - embeddings will work but won't be stored in vector database")
                return
            
            # Initialize Pinecone with modern API
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            print("✅ Pinecone client initialized")
            
            # Check if index exists
            index_name = settings.pinecone_index_name
            
            # List existing indexes
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if index_name not in existing_indexes:
                print(f"📝 Creating new index: {index_name}")
                
                # Create index with serverless spec (modern approach)
                self.pc.create_index(
                    name=index_name,
                    dimension=768,  # Gemini embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"✅ Index created: {index_name}")
            else:
                print(f"✅ Index '{index_name}' already exists")
            
            # Connect to index
            self.index = self.pc.Index(index_name)
            self._pinecone_initialized = True
            
            # Test index connection
            stats = self.index.describe_index_stats()
            print(f"✅ Pinecone initialized successfully with index: {index_name}")
            print(f"📊 Index stats: {stats.total_vector_count} vectors, {stats.dimension}D")
            
        except Exception as e:
            print(f"⚠️  Could not initialize Pinecone: {e}")
            print("📝 Continuing in test mode - embeddings will work but won't be stored in vector database")
            print("💡 To fix: Check network connection, API key, and Pinecone setup")

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
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️  Gemini API quota exceeded: {e}")
                print("💡 Using fallback embeddings. Consider upgrading your Gemini API plan.")
            else:
                print(f"❌ Error generating embeddings: {e}")
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
                print(f"✅ Stored {len(vectors)} embeddings in Pinecone")
            except Exception as e:
                print(f"❌ Error storing embeddings in Pinecone: {e}")
        else:
            print(f"📝 Pinecone not available, generated {len(vectors)} embeddings but not stored")
            
        return embedding_ids

    async def similarity_search(self, query: str, pdf_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in the PDF"""
        # Try to initialize Pinecone if not already done
        self._init_pinecone()
        
        if not self.index:
            print("📝 Pinecone not available, returning empty results")
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
            print(f"❌ Error during similarity search: {e}")
            return []