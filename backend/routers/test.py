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
@router.get("/dummy-data")
async def get_dummy_data():
    """Get information about dummy data for testing"""
    try:
        from utils.database import get_user, get_pdf_document, get_quiz, get_user_notes
        
        dummy_user_id = "test_user_123"
        dummy_pdf_id = "pdf_d287d3b3fe66487a9766a3183f6da031"
        dummy_quiz_id = "quiz_test_123"
        dummy_notes_id = "notes_test_123"
        
        # Check if dummy data exists
        user_exists = await get_user(dummy_user_id) is not None
        
        try:
            pdf_exists = await get_pdf_document(dummy_pdf_id) is not None
        except:
            pdf_exists = False
            
        try:
            quiz_exists = await get_quiz(dummy_quiz_id) is not None
        except:
            quiz_exists = False
            
        try:
            notes_exists = await get_user_notes(dummy_notes_id) is not None
        except:
            notes_exists = False
        
        return {
            "dummy_data_status": {
                "user": {
                    "id": dummy_user_id,
                    "exists": user_exists,
                    "email": "test@example.com"
                },
                "pdf": {
                    "id": dummy_pdf_id,
                    "exists": pdf_exists,
                    "title": "Machine Learning Basics.pdf"
                },
                "quiz": {
                    "id": dummy_quiz_id,
                    "exists": quiz_exists,
                    "title": "Machine Learning Basics Quiz"
                },
                "notes": {
                    "id": dummy_notes_id,
                    "exists": notes_exists,
                    "title": "Sample Study Notes"
                }
            },
            "instructions": {
                "initialize_db": "Run 'python init_db.py' to create dummy data",
                "test_endpoints": "Use the dummy IDs above to test API endpoints",
                "auth_token": "Use 'test_token' as Bearer token for testing"
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Could not check dummy data status",
            "suggestion": "Run 'python init_db.py' to initialize the database"
        }

@router.post("/init-dummy-data")
async def initialize_dummy_data():
    """Initialize dummy data for testing"""
    try:
        from utils.db_init import initialize_database
        await initialize_database()
        
        return {
            "message": "Dummy data initialized successfully",
            "dummy_user_id": "test_user_123",
            "dummy_pdf_id": "pdf_d287d3b3fe66487a9766a3183f6da031",
            "dummy_quiz_id": "quiz_test_123",
            "dummy_notes_id": "notes_test_123",
            "auth_token": "test_token"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to initialize dummy data",
            "suggestion": "Check Firebase configuration and permissions"
        }
@router.post("/create-user")
async def create_test_user():
    """Create only a dummy user for testing"""
    try:
        from datetime import datetime
        from models.user import User
        from utils.database import save_user, get_user
        
        dummy_user_id = "test_user_123"
        
        # Check if user already exists
        existing_user = await get_user(dummy_user_id)
        if existing_user:
            return {
                "message": "User already exists",
                "user_id": dummy_user_id,
                "email": "test@example.com",
                "name": "Test User"
            }
        
        # Create dummy user
        dummy_user = User(
            uid=dummy_user_id,
            email="test@example.com",
            name="Test User",
            created_at=datetime.now(),
            last_login=datetime.now(),
            preferences={
                "difficulty_preference": "medium",
                "study_reminders": True,
                "email_notifications": True
            }
        )
        
        await save_user(dummy_user)
        
        return {
            "message": "Dummy user created successfully",
            "user_id": dummy_user_id,
            "email": "test@example.com",
            "name": "Test User",
            "auth_token": "test_token"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to create dummy user"
        }
@router.post("/create-collections")
async def create_firestore_collections():
    """Create Firestore collections with placeholder documents"""
    try:
        from firebase_admin import firestore
        from datetime import datetime
        
        db = firestore.client()
        
        collections_to_create = [
            'users',
            'pdfs', 
            'quizzes',
            'quiz_attempts',
            'study_notes',
            'recommendations'
        ]
        
        created_collections = []
        existing_collections = []
        
        for collection_name in collections_to_create:
            try:
                # Check if collection exists
                collection_ref = db.collection(collection_name)
                docs = list(collection_ref.limit(1).get())
                
                if len(docs) == 0:
                    # Create placeholder document
                    placeholder_doc = collection_ref.document('_placeholder')
                    placeholder_doc.set({
                        'created_at': datetime.now(),
                        'purpose': 'Collection placeholder - keeps collection visible in Firebase Console',
                        'note': 'This document can be safely deleted once real data is added',
                        'collection_name': collection_name,
                        'is_placeholder': True
                    })
                    created_collections.append(collection_name)
                else:
                    existing_collections.append(collection_name)
                    
            except Exception as e:
                return {
                    "error": f"Error with collection {collection_name}: {str(e)}",
                    "collection": collection_name
                }
        
        return {
            "message": "Collections processed successfully",
            "created_collections": created_collections,
            "existing_collections": existing_collections,
            "total_collections": len(collections_to_create),
            "note": "Check Firebase Console - collections should now be visible",
            "console_url": "https://console.firebase.google.com"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to create collections"
        }