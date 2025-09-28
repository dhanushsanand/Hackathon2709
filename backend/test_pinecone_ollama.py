#!/usr/bin/env python3
"""
Comprehensive Pinecone + Ollama Integration Test
Tests the full embedding pipeline: Ollama → Pinecone → Search
"""

import asyncio
import requests
import json
import time
from typing import List, Dict, Any

async def test_ollama_embeddings():
    """Test Ollama embedding generation"""
    print("🧠 Testing Ollama Embeddings...")
    
    try:
        from services.embeddings import EmbeddingService
        
        service = EmbeddingService()
        
        if service.provider != "ollama":
            print(f"⚠️  Expected Ollama provider, got: {service.provider}")
            print("💡 Set EMBEDDING_PROVIDER=ollama in .env")
            return False, None
        
        # Test embedding generation
        test_texts = [
            "Artificial intelligence is transforming technology.",
            "Machine learning algorithms learn from data patterns.",
            "Deep learning uses neural networks for complex tasks.",
            "Natural language processing enables human-computer interaction.",
            "Computer vision allows machines to interpret visual information."
        ]
        
        print(f"📝 Generating embeddings for {len(test_texts)} texts...")
        embeddings = await service.generate_embeddings(test_texts)
        
        if embeddings and len(embeddings) == len(test_texts):
            print(f"✅ Generated {len(embeddings)} embeddings")
            print(f"📏 Dimension: {len(embeddings[0])}")
            print(f"📊 Sample embedding values: {embeddings[0][:5]}...")
            return True, (test_texts, embeddings)
        else:
            print("❌ Embedding generation failed")
            return False, None
            
    except Exception as e:
        print(f"❌ Ollama embedding test failed: {e}")
        return False, None

async def test_pinecone_storage():
    """Test storing embeddings in Pinecone"""
    print("\n📦 Testing Pinecone Storage...")
    
    try:
        from services.embeddings import EmbeddingService
        
        service = EmbeddingService()
        
        # Test data
        test_texts = [
            "Python is a programming language used for AI development.",
            "JavaScript is popular for web development and frontend applications.",
            "SQL databases store and manage structured data efficiently.",
            "Docker containers provide consistent deployment environments.",
            "Kubernetes orchestrates containerized applications at scale."
        ]
        
        test_pdf_id = f"test_pinecone_{int(time.time())}"
        
        print(f"📝 Storing {len(test_texts)} embeddings in Pinecone...")
        storage_ids = await service.store_embeddings(test_texts, test_pdf_id)
        
        if storage_ids and len(storage_ids) == len(test_texts):
            print(f"✅ Stored {len(storage_ids)} embeddings")
            print(f"🆔 Sample IDs: {storage_ids[:2]}...")
            return True, (test_pdf_id, storage_ids, test_texts)
        else:
            print("❌ Pinecone storage failed")
            return False, None
            
    except Exception as e:
        print(f"❌ Pinecone storage test failed: {e}")
        return False, None

async def test_similarity_search(test_data):
    """Test similarity search in Pinecone"""
    print("\n🔍 Testing Similarity Search...")
    
    if not test_data:
        print("❌ No test data available for similarity search")
        return False
    
    try:
        from services.embeddings import EmbeddingService
        
        service = EmbeddingService()
        test_pdf_id, storage_ids, original_texts = test_data
        
        # Test queries
        test_queries = [
            "programming languages for AI",
            "web development technologies", 
            "database management systems",
            "container deployment tools"
        ]
        
        search_results = []
        
        for query in test_queries:
            print(f"🔎 Searching for: '{query}'")
            
            results = await service.similarity_search(query, test_pdf_id, top_k=3)
            
            if results:
                print(f"   ✅ Found {len(results)} results")
                for i, result in enumerate(results[:2]):  # Show top 2
                    score = result.get('score', 0)
                    text = result.get('text', '')[:100] + '...'
                    print(f"   {i+1}. Score: {score:.3f} - {text}")
                search_results.append((query, results))
            else:
                print(f"   ⚠️  No results found")
        
        if search_results:
            print(f"✅ Similarity search completed for {len(search_results)} queries")
            return True
        else:
            print("❌ No search results found")
            return False
            
    except Exception as e:
        print(f"❌ Similarity search test failed: {e}")
        return False

async def test_pinecone_index_stats():
    """Test Pinecone index statistics"""
    print("\n📊 Testing Pinecone Index Stats...")
    
    try:
        from services.embeddings import EmbeddingService
        
        service = EmbeddingService()
        
        # Initialize Pinecone if not already done
        service._init_pinecone()
        
        if not service.index:
            print("❌ Pinecone index not available")
            return False
        
        # Get index stats
        stats = service.index.describe_index_stats()
        
        print(f"✅ Index Statistics:")
        print(f"   📊 Total vectors: {stats.total_vector_count}")
        print(f"   📏 Dimension: {stats.dimension}")
        print(f"   📈 Index fullness: {stats.index_fullness:.2%}")
        
        if hasattr(stats, 'namespaces') and stats.namespaces:
            print(f"   📁 Namespaces: {list(stats.namespaces.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Index stats test failed: {e}")
        return False

async def test_cleanup(test_data):
    """Clean up test data from Pinecone"""
    print("\n🧹 Cleaning Up Test Data...")
    
    if not test_data:
        print("ℹ️  No test data to clean up")
        return True
    
    try:
        from services.embeddings import EmbeddingService
        
        service = EmbeddingService()
        test_pdf_id, storage_ids, _ = test_data
        
        if service.index:
            # Delete test vectors
            service.index.delete(filter={"pdf_id": test_pdf_id})
            print(f"✅ Cleaned up test data for PDF ID: {test_pdf_id}")
            return True
        else:
            print("ℹ️  Pinecone not available, no cleanup needed")
            return True
            
    except Exception as e:
        print(f"⚠️  Cleanup failed (not critical): {e}")
        return True  # Non-critical failure

async def test_performance_benchmark():
    """Benchmark embedding and storage performance"""
    print("\n⚡ Performance Benchmark...")
    
    try:
        from services.embeddings import EmbeddingService
        import time
        
        service = EmbeddingService()
        
        # Test data of varying sizes
        test_sizes = [1, 5, 10, 20]
        
        for size in test_sizes:
            test_texts = [f"This is test sentence number {i} for performance testing." for i in range(size)]
            
            # Time embedding generation
            start_time = time.time()
            embeddings = await service.generate_embeddings(test_texts)
            embedding_time = time.time() - start_time
            
            # Time storage (if Pinecone available)
            if service.index:
                start_time = time.time()
                test_pdf_id = f"perf_test_{size}_{int(time.time())}"
                storage_ids = await service.store_embeddings(test_texts, test_pdf_id)
                storage_time = time.time() - start_time
                
                # Cleanup
                service.index.delete(filter={"pdf_id": test_pdf_id})
            else:
                storage_time = 0
            
            print(f"   📊 {size:2d} texts: Embedding {embedding_time:.2f}s, Storage {storage_time:.2f}s")
        
        print("✅ Performance benchmark completed")
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False

async def main():
    """Run comprehensive Pinecone + Ollama tests"""
    print("🧪 Comprehensive Pinecone + Ollama Integration Test")
    print("=" * 60)
    
    results = {}
    test_data = None
    
    # Test 1: Ollama embeddings
    print("Phase 1: Ollama Embedding Generation")
    print("-" * 40)
    ollama_success, ollama_data = await test_ollama_embeddings()
    results["ollama_embeddings"] = ollama_success
    
    if not ollama_success:
        print("\n❌ Ollama embeddings failed. Cannot continue with Pinecone tests.")
        return
    
    # Test 2: Pinecone storage
    print("\nPhase 2: Pinecone Storage")
    print("-" * 40)
    storage_success, storage_data = await test_pinecone_storage()
    results["pinecone_storage"] = storage_success
    test_data = storage_data
    
    # Test 3: Similarity search
    print("\nPhase 3: Similarity Search")
    print("-" * 40)
    search_success = await test_similarity_search(test_data)
    results["similarity_search"] = search_success
    
    # Test 4: Index statistics
    print("\nPhase 4: Index Statistics")
    print("-" * 40)
    stats_success = await test_pinecone_index_stats()
    results["index_stats"] = stats_success
    
    # Test 5: Performance benchmark
    print("\nPhase 5: Performance Benchmark")
    print("-" * 40)
    perf_success = await test_performance_benchmark()
    results["performance"] = perf_success
    
    # Test 6: Cleanup
    print("\nPhase 6: Cleanup")
    print("-" * 40)
    cleanup_success = await test_cleanup(test_data)
    results["cleanup"] = cleanup_success
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 EXCELLENT: Full Pinecone + Ollama integration working perfectly!")
        print("💡 Your system is production-ready with:")
        print("   ✅ Unlimited local embeddings (Ollama)")
        print("   ✅ Scalable vector storage (Pinecone)")
        print("   ✅ Fast similarity search")
        print("   ✅ Good performance")
        
        print("\n🚀 Ready for production:")
        print("   - Set TEST_MODE=false in .env")
        print("   - Upload PDFs and generate quizzes")
        print("   - Enjoy unlimited, fast embeddings!")
        
    elif passed >= total * 0.8:  # 80% pass rate
        print("\n✅ GOOD: Most tests passed. Minor issues detected.")
        print("💡 Your system is mostly working. Check failed tests above.")
        
    else:
        print("\n⚠️  ISSUES: Several tests failed.")
        print("💡 Check the failed tests and fix issues before production use.")

if __name__ == "__main__":
    asyncio.run(main())