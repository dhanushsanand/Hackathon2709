#!/usr/bin/env python3
"""
Test Pinecone Only (No Gemini API calls)
Simple test to verify Pinecone connectivity without using quota
"""

def test_pinecone_only():
    print("🔧 Testing Pinecone Only (No Gemini API)")
    print("-" * 50)
    
    try:
        from config import settings
        from pinecone import Pinecone, ServerlessSpec
        
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        print("✅ Pinecone client initialized")
        
        # List indexes
        indexes = [idx.name for idx in pc.list_indexes()]
        print(f"✅ Available indexes: {indexes}")
        
        index_name = settings.pinecone_index_name
        
        if index_name in indexes:
            print(f"✅ Target index '{index_name}' exists")
            
            # Connect to index
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"✅ Index stats: {stats.total_vector_count} vectors, {stats.dimension}D")
            
            # Test with dummy vector (same dimension as Gemini)
            test_vector = [0.1] * 768  # 768-dimensional dummy vector
            
            # Upsert test vector
            index.upsert(vectors=[{
                "id": "test_vector_123",
                "values": test_vector,
                "metadata": {"test": "true", "source": "pinecone_test"}
            }])
            print("✅ Test vector uploaded successfully")
            
            # Query test vector
            results = index.query(
                vector=test_vector,
                top_k=1,
                include_metadata=True
            )
            print(f"✅ Query successful: {len(results.matches)} results")
            
            # Clean up test vector
            index.delete(ids=["test_vector_123"])
            print("✅ Test vector cleaned up")
            
            return True
            
        else:
            print(f"⚠️  Index '{index_name}' not found")
            print("🔨 Creating index...")
            
            pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Index '{index_name}' created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Pinecone test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pinecone_only()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Pinecone is working perfectly!")
        print("💡 Your vector database is ready for production")
        print("📝 You can now set TEST_MODE=false in .env")
    else:
        print("❌ Pinecone issues detected")
        print("📝 Keep TEST_MODE=true for now")
    
    print("\n🚀 Next steps:")
    print("   - Wait for Gemini quota to reset (24 hours)")
    print("   - Or upgrade Gemini API plan")
    print("   - Test your full PDF quiz system")