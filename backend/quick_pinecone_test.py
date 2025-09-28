#!/usr/bin/env python3
"""
Quick Pinecone Connection Test
Simple script to quickly test if Pinecone is working
"""

import socket
import sys

def quick_test():
    print("🚀 Quick Pinecone Connection Test")
    print("-" * 40)
    
    # Test 1: DNS Resolution
    print("1️⃣  Testing DNS resolution...")
    try:
        ip = socket.gethostbyname('api.pinecone.io')
        print(f"   ✅ DNS OK: api.pinecone.io → {ip}")
        dns_ok = True
    except socket.gaierror as e:
        print(f"   ❌ DNS FAILED: {e}")
        dns_ok = False
    
    if not dns_ok:
        print("\n💡 DNS Issue Solutions:")
        print("   - Check internet connection")
        print("   - Try different DNS: sudo networksetup -setdnsservers Wi-Fi 8.8.8.8")
        print("   - Disable VPN temporarily")
        print("   - Try from different network")
        return False
    
    # Test 2: Pinecone API
    print("\n2️⃣  Testing Pinecone API...")
    try:
        from config import settings
        api_key = settings.pinecone_api_key
        environment = settings.pinecone_environment
        index_name = settings.pinecone_index_name
        
        print(f"   📋 API Key: {api_key[:8]}...{api_key[-4:]}")
        print(f"   📋 Environment: {environment}")
        print(f"   📋 Index: {index_name}")
        
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False
    
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)
        
        # List indexes
        indexes = [idx.name for idx in pc.list_indexes()]
        print(f"   ✅ API OK: Found indexes: {indexes}")
        
        if index_name in indexes:
            print(f"   ✅ Index '{index_name}' exists")
            
            # Test index connection
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"   ✅ Index stats: {stats.total_vector_count} vectors, {stats.dimension}D")
            
        else:
            print(f"   ⚠️  Index '{index_name}' not found")
            print("   💡 Run the full test script to create it")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API FAILED: {e}")
        return False

def test_embeddings():
    print("\n3️⃣  Testing Embeddings...")
    try:
        import asyncio
        from services.embeddings import EmbeddingService
        
        async def test():
            service = EmbeddingService()
            
            # Test embedding generation
            embeddings = await service.generate_embeddings(["test text"])
            print(f"   ✅ Generated embedding: {len(embeddings[0])}D")
            
            # Check Pinecone connection
            if service.index:
                print("   ✅ Pinecone connected")
                return "pinecone"
            else:
                print("   📝 Using test mode")
                return "test_mode"
        
        result = asyncio.run(test())
        return result
        
    except Exception as e:
        print(f"   ❌ Embedding test failed: {e}")
        return False

if __name__ == "__main__":
    print()
    
    # Quick connectivity test
    pinecone_ok = quick_test()
    
    # Embedding test
    embedding_result = test_embeddings()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 40)
    
    if pinecone_ok and embedding_result == "pinecone":
        print("🎉 SUCCESS: Pinecone is fully working!")
        print("💡 You can set TEST_MODE=false in .env")
        
    elif embedding_result == "test_mode":
        print("📝 PARTIAL: Embeddings work in test mode")
        print("💡 Keep TEST_MODE=true for now")
        
    else:
        print("❌ ISSUES: Some problems detected")
        print("💡 Run 'python test_pinecone_connection.py' for detailed diagnosis")
    
    print("\n🚀 Ready to test your APIs!")
    print("   - Start server: python main.py")
    print("   - Test endpoint: GET /test/embeddings/status")
    print("   - Use Postman collection for full testing")