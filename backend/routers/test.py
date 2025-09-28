from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from middleware.auth import get_current_user_id
from services.embeddings import EmbeddingService
from services.gemini import GeminiService

router = APIRouter()
embedding_service = EmbeddingService()
gemini_service = GeminiService()

class EmbeddingTestRequest(BaseModel):
    texts: List[str]
    test_query: str = "What is the main topic?"

class EmbeddingTestResponse(BaseModel):
    embeddings_generated: int
    embedding_dimension: int
    storage_ids: List[str]
    search_results: List[Dict[str, Any]]
    pinecone_status: str

@router.post("/embeddings", response_model=EmbeddingTestResponse)
async def test_embeddings(
    request: EmbeddingTestRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Test embedding generation and storage"""
    try:
        # Generate embeddings
        embeddings = await embedding_service.generate_embeddings(request.texts)
        
        # Store embeddings with test PDF ID
        test_pdf_id = f"test_pdf_{user_id}"
        storage_ids = await embedding_service.store_embeddings(request.texts, test_pdf_id)
        
        # Test similarity search
        search_results = await embedding_service.similarity_search(
            request.test_query, 
            test_pdf_id, 
            top_k=3
        )
        
        # Check Pinecone status
        pinecone_status = "connected" if embedding_service.index else "test_mode"
        
        return EmbeddingTestResponse(
            embeddings_generated=len(embeddings),
            embedding_dimension=len(embeddings[0]) if embeddings else 0,
            storage_ids=storage_ids,
            search_results=search_results,
            pinecone_status=pinecone_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding test failed: {str(e)}")

@router.get("/embeddings/status")
async def get_embedding_status():
    """Get embedding service status"""
    try:
        # Test embedding generation
        test_embeddings = await embedding_service.generate_embeddings(["test text"])
        embedding_status = "connected" if test_embeddings else "failed"
        
        # Check Pinecone status
        pinecone_status = "connected" if embedding_service.index else "test_mode"
        
        # Get provider-specific info
        provider_info = {
            "provider": embedding_service.provider,
            "dimension": embedding_service.embedding_dimension
        }
        
        if embedding_service.provider == "ollama":
            provider_info.update({
                "ollama_url": embedding_service.ollama_url,
                "ollama_model": embedding_service.ollama_model
            })
        
        return {
            "embedding_service": embedding_status,
            "pinecone_vector_db": pinecone_status,
            "embedding_dimension": len(test_embeddings[0]) if test_embeddings else 0,
            "provider_info": provider_info,
            "test_mode": not embedding_service._pinecone_initialized
        }
        
    except Exception as e:
        return {
            "embedding_service": "failed",
            "pinecone_vector_db": "failed", 
            "error": str(e),
            "provider": getattr(embedding_service, 'provider', 'unknown'),
            "test_mode": True
        }

@router.post("/embeddings/cleanup")
async def cleanup_test_embeddings(user_id: str = Depends(get_current_user_id)):
    """Clean up test embeddings"""
    try:
        test_pdf_id = f"test_pdf_{user_id}"
        
        if embedding_service.index:
            # Delete from Pinecone
            embedding_service.index.delete(filter={"pdf_id": test_pdf_id})
            return {"message": "Test embeddings cleaned up from Pinecone"}
        else:
            return {"message": "Test mode - no cleanup needed"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.get("/gemini/test")
async def test_gemini_api():
    """Test Gemini API connection"""
    try:
        # Test embedding generation
        test_texts = ["This is a test sentence.", "Another test sentence for embeddings."]
        embeddings = await embedding_service.generate_embeddings(test_texts)
        
        # Test quiz generation (simple)
        test_content = ["Machine learning is a subset of artificial intelligence that focuses on algorithms."]
        questions = await gemini_service.generate_quiz_questions(test_content, 1)
        
        return {
            "embedding_test": {
                "status": "success",
                "texts_processed": len(test_texts),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0
            },
            "quiz_generation_test": {
                "status": "success",
                "questions_generated": len(questions),
                "sample_question": questions[0].question_text if questions else None
            }
        }
        
    except Exception as e:
        return {
            "embedding_test": {"status": "failed", "error": str(e)},
            "quiz_generation_test": {"status": "failed", "error": str(e)}
        }

@router.get("/pinecone/info")
async def get_pinecone_info():
    """Get Pinecone index information"""
    try:
        if not embedding_service.index:
            return {
                "status": "test_mode",
                "message": "Pinecone not connected - using test storage",
                "setup_required": True
            }
        
        # Get index stats
        stats = embedding_service.index.describe_index_stats()
        
        return {
            "status": "connected",
            "index_name": embedding_service.index._index_name,
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": list(stats.namespaces.keys()) if stats.namespaces else []
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "setup_required": True
        }