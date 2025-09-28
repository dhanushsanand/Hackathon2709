#!/usr/bin/env python3
"""
Test Ollama Integration
Comprehensive test for local embedding generation using Ollama
"""

import requests
import asyncio
import json

def test_ollama_service():
    """Test if Ollama service is running"""
    print("🔍 Testing Ollama Service...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "").split(":")[0] for model in models]
            print(f"✅ Ollama is running. Available models: {model_names}")
            return True, model_names
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False, []
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        print("💡 Start Ollama with: ollama serve")
        return False, []
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False, []

def test_embedding_model():
    """Test embedding generation with Ollama"""
    print("\n🧠 Testing Embedding Generation...")
    
    test_text = "This is a test sentence for embedding generation."
    
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": test_text
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            
            if embedding:
                print(f"✅ Embedding generated successfully!")
                print(f"📏 Dimension: {len(embedding)}")
                print(f"📊 Sample values: {embedding[:5]}...")
                return True, len(embedding)
            else:
                print("❌ No embedding in response")
                return False, 0
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return False, 0

async def test_embedding_service():
    """Test the EmbeddingService with Ollama"""
    print("\n🔧 Testing EmbeddingService Integration...")
    
    try:
        from services.embeddings import EmbeddingService
        
        # Initialize service
        service = EmbeddingService()
        print(f"✅ EmbeddingService initialized with provider: {service.provider}")
        
        # Test embedding generation
        test_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing helps computers understand text."
        ]
        
        embeddings = await service.generate_embeddings(test_texts)
        
        if embeddings and len(embeddings) == len(test_texts):
            print(f"✅ Generated {len(embeddings)} embeddings")
            print(f"📏 Embedding dimension: {len(embeddings[0])}")
            
            # Test storage (will use Pinecone if available, test mode otherwise)
            test_pdf_id = "test_ollama_pdf"
            storage_ids = await service.store_embeddings(test_texts, test_pdf_id)
            print(f"✅ Stored embeddings with IDs: {storage_ids}")
            
            # Test similarity search
            search_results = await service.similarity_search("machine learning", test_pdf_id, top_k=2)
            print(f"✅ Similarity search returned {len(search_results)} results")
            
            return True
        else:
            print("❌ Embedding generation failed")
            return False
            
    except Exception as e:
        print(f"❌ EmbeddingService test failed: {e}")
        return False

def test_model_pull():
    """Test pulling the embedding model if not available"""
    print("\n📥 Checking/Pulling Embedding Model...")
    
    # Check if model is available
    ollama_running, models = test_ollama_service()
    if not ollama_running:
        return False
    
    if "nomic-embed-text" not in models:
        print("📥 nomic-embed-text model not found. Attempting to pull...")
        print("💡 This may take a few minutes for the first time...")
        
        try:
            # Note: This is a simplified check. In practice, you'd use subprocess
            # to run `ollama pull nomic-embed-text`
            print("🔧 Please run manually: ollama pull nomic-embed-text")
            return False
        except Exception as e:
            print(f"❌ Error pulling model: {e}")
            return False
    else:
        print("✅ nomic-embed-text model is available")
        return True

async def main():
    """Run all Ollama tests"""
    print("🧪 Ollama Integration Testing")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Ollama service
    ollama_running, models = test_ollama_service()
    results["ollama_service"] = ollama_running
    
    if not ollama_running:
        print("\n💡 SETUP REQUIRED:")
        print("1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("2. Start Ollama: ollama serve")
        print("3. Pull model: ollama pull nomic-embed-text")
        return
    
    # Test 2: Model availability
    model_available = test_model_pull()
    results["model_available"] = model_available
    
    if not model_available:
        print("\n💡 MODEL SETUP REQUIRED:")
        print("Run: ollama pull nomic-embed-text")
        return
    
    # Test 3: Direct embedding test
    embedding_works, dimension = test_embedding_model()
    results["embedding_generation"] = embedding_works
    
    # Test 4: Service integration
    service_works = await test_embedding_service()
    results["service_integration"] = service_works
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 SUCCESS: Ollama is fully working!")
        print("💡 Your system now has unlimited, free embeddings!")
        print("\n🚀 Next steps:")
        print("   - Set EMBEDDING_PROVIDER=ollama in .env")
        print("   - Restart your server: python main.py")
        print("   - Test your PDF quiz system!")
    else:
        print("\n⚠️  ISSUES DETECTED")
        print("💡 Follow the setup instructions above")
        print("📖 See OLLAMA_SETUP.md for detailed guide")

if __name__ == "__main__":
    asyncio.run(main())