#!/usr/bin/env python3
"""
Comprehensive Pinecone Connection Testing Script
Tests network connectivity, DNS resolution, API access, and index operations
"""

import socket
import requests
import time
import sys
import os
from typing import Dict, Any

def test_basic_connectivity() -> Dict[str, Any]:
    """Test basic internet connectivity"""
    print("🌐 Testing Basic Internet Connectivity...")
    
    test_sites = [
        ("Google DNS", "8.8.8.8", 53),
        ("Cloudflare DNS", "1.1.1.1", 53),
        ("Google", "google.com", 80),
        ("GitHub", "github.com", 443)
    ]
    
    results = {}
    for name, host, port in test_sites:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"  ✅ {name} ({host}:{port}) - Connected")
                results[name] = "connected"
            else:
                print(f"  ❌ {name} ({host}:{port}) - Failed")
                results[name] = "failed"
        except Exception as e:
            print(f"  ❌ {name} ({host}:{port}) - Error: {e}")
            results[name] = f"error: {e}"
    
    return results

def test_dns_resolution() -> Dict[str, Any]:
    """Test DNS resolution for Pinecone domains"""
    print("\n🔍 Testing DNS Resolution...")
    
    pinecone_domains = [
        "controller.us-east-1.pinecone.io",
        "api.pinecone.io",
        "pinecone.io"
    ]
    
    results = {}
    for domain in pinecone_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"  ✅ {domain} → {ip}")
            results[domain] = ip
        except socket.gaierror as e:
            print(f"  ❌ {domain} → DNS Error: {e}")
            results[domain] = f"dns_error: {e}"
        except Exception as e:
            print(f"  ❌ {domain} → Error: {e}")
            results[domain] = f"error: {e}"
    
    return results

def test_http_connectivity() -> Dict[str, Any]:
    """Test HTTP connectivity to Pinecone"""
    print("\n🌍 Testing HTTP Connectivity...")
    
    test_urls = [
        "https://api.pinecone.io/",
        "https://pinecone.io/",
        "https://httpbin.org/get"  # Control test
    ]
    
    results = {}
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"  ✅ {url} → Status: {response.status_code}")
            results[url] = {"status": response.status_code, "success": True}
        except requests.exceptions.Timeout:
            print(f"  ⏰ {url} → Timeout")
            results[url] = {"error": "timeout", "success": False}
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ {url} → Connection Error: {e}")
            results[url] = {"error": f"connection: {e}", "success": False}
        except Exception as e:
            print(f"  ❌ {url} → Error: {e}")
            results[url] = {"error": str(e), "success": False}
    
    return results

def test_pinecone_api() -> Dict[str, Any]:
    """Test Pinecone API with actual credentials"""
    print("\n🔑 Testing Pinecone API...")
    
    # Try to load config
    try:
        from config import settings
        api_key = settings.pinecone_api_key
        environment = settings.pinecone_environment
        index_name = settings.pinecone_index_name
        
        print(f"  📋 API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'short'}")
        print(f"  📋 Environment: {environment}")
        print(f"  📋 Index Name: {index_name}")
        
    except Exception as e:
        print(f"  ❌ Could not load config: {e}")
        return {"config_error": str(e)}
    
    # Test Pinecone import
    try:
        from pinecone import Pinecone, ServerlessSpec
        print("  ✅ Pinecone library imported successfully")
    except ImportError as e:
        print(f"  ❌ Could not import pinecone: {e}")
        return {"import_error": str(e)}
    
    # Test Pinecone initialization
    try:
        pc = Pinecone(api_key=api_key)
        print("  ✅ Pinecone initialized successfully")
    except Exception as e:
        print(f"  ❌ Pinecone initialization failed: {e}")
        return {"init_error": str(e)}
    
    # Test list indexes
    try:
        indexes = [idx.name for idx in pc.list_indexes()]
        print(f"  ✅ Available indexes: {indexes}")
        
        if index_name in indexes:
            print(f"  ✅ Target index '{index_name}' exists")
            index_exists = True
        else:
            print(f"  ⚠️  Target index '{index_name}' does not exist")
            index_exists = False
            
    except Exception as e:
        print(f"  ❌ Could not list indexes: {e}")
        return {"list_error": str(e)}
    
    # Test index connection if it exists
    if index_exists:
        try:
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"  ✅ Index stats: {stats}")
            return {
                "success": True,
                "indexes": indexes,
                "index_exists": True,
                "stats": stats
            }
        except Exception as e:
            print(f"  ❌ Could not connect to index: {e}")
            return {"index_error": str(e)}
    else:
        return {
            "success": True,
            "indexes": indexes,
            "index_exists": False,
            "message": f"Index '{index_name}' needs to be created"
        }

def test_create_index() -> Dict[str, Any]:
    """Test creating a Pinecone index"""
    print("\n🏗️  Testing Index Creation...")
    
    try:
        from config import settings
        from pinecone import Pinecone, ServerlessSpec
        
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        
        # Check if index already exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        if settings.pinecone_index_name in existing_indexes:
            print(f"  ℹ️  Index '{settings.pinecone_index_name}' already exists")
            return {"already_exists": True}
        
        # Create index
        print(f"  🔨 Creating index '{settings.pinecone_index_name}'...")
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=768,  # Gemini embedding dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        # Wait for index to be ready
        print("  ⏳ Waiting for index to be ready...")
        max_wait = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                index = pc.Index(settings.pinecone_index_name)
                stats = index.describe_index_stats()
                print(f"  ✅ Index created successfully! Stats: {stats}")
                return {"created": True, "stats": stats}
            except Exception:
                time.sleep(5)
                wait_time += 5
                print(f"  ⏳ Still waiting... ({wait_time}s)")
        
        print(f"  ⚠️  Index creation timed out after {max_wait}s")
        return {"timeout": True}
        
    except Exception as e:
        print(f"  ❌ Index creation failed: {e}")
        return {"error": str(e)}

def test_embedding_operations() -> Dict[str, Any]:
    """Test actual embedding operations"""
    print("\n🧠 Testing Embedding Operations...")
    
    try:
        from services.embeddings import EmbeddingService
        
        # Initialize service
        service = EmbeddingService()
        print("  ✅ EmbeddingService initialized")
        
        # Test embedding generation
        import asyncio
        
        async def test_embeddings():
            # Test Gemini embeddings
            test_texts = ["This is a test sentence.", "Another test for embeddings."]
            embeddings = await service.generate_embeddings(test_texts)
            
            print(f"  ✅ Generated {len(embeddings)} embeddings")
            print(f"  📏 Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
            
            # Test storage (will use Pinecone if available, test mode otherwise)
            test_pdf_id = "test_connection_pdf"
            storage_ids = await service.store_embeddings(test_texts, test_pdf_id)
            
            print(f"  ✅ Stored embeddings with IDs: {storage_ids}")
            
            # Test similarity search
            search_results = await service.similarity_search("test", test_pdf_id, top_k=2)
            
            print(f"  ✅ Similarity search returned {len(search_results)} results")
            
            return {
                "embeddings_generated": len(embeddings),
                "dimension": len(embeddings[0]) if embeddings else 0,
                "storage_ids": storage_ids,
                "search_results": len(search_results),
                "pinecone_connected": service.index is not None
            }
        
        return asyncio.run(test_embeddings())
        
    except Exception as e:
        print(f"  ❌ Embedding operations failed: {e}")
        return {"error": str(e)}

def main():
    """Run all tests"""
    print("🧪 Pinecone Connection Testing Script")
    print("=" * 50)
    
    all_results = {}
    
    # Test 1: Basic connectivity
    all_results["basic_connectivity"] = test_basic_connectivity()
    
    # Test 2: DNS resolution
    all_results["dns_resolution"] = test_dns_resolution()
    
    # Test 3: HTTP connectivity
    all_results["http_connectivity"] = test_http_connectivity()
    
    # Test 4: Pinecone API
    all_results["pinecone_api"] = test_pinecone_api()
    
    # Test 5: Create index if needed
    if all_results["pinecone_api"].get("success") and not all_results["pinecone_api"].get("index_exists"):
        print("\n🤔 Index doesn't exist. Would you like to create it? (y/n)")
        response = input().lower().strip()
        if response in ['y', 'yes']:
            all_results["index_creation"] = test_create_index()
    
    # Test 6: Embedding operations
    all_results["embedding_operations"] = test_embedding_operations()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, results in all_results.items():
        if isinstance(results, dict):
            if results.get("success") or any(k in results for k in ["connected", "created"]):
                print(f"✅ {test_name.replace('_', ' ').title()}: PASS")
            else:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAIL")
        else:
            print(f"ℹ️  {test_name.replace('_', ' ').title()}: {results}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    dns_issues = any("dns_error" in str(v) for v in all_results.get("dns_resolution", {}).values())
    if dns_issues:
        print("  🔧 DNS Issues detected:")
        print("     - Try changing DNS to 8.8.8.8 or 1.1.1.1")
        print("     - Check if you're behind a corporate firewall")
        print("     - Try from a different network (mobile hotspot)")
    
    if not all_results.get("pinecone_api", {}).get("success"):
        print("  🔧 Pinecone API Issues:")
        print("     - Verify your API key in .env file")
        print("     - Check if your Pinecone account is active")
        print("     - Ensure you're using the correct environment")
    
    if all_results.get("embedding_operations", {}).get("pinecone_connected"):
        print("  🎉 Pinecone is working! You can use production mode.")
        print("     - Set TEST_MODE=false in .env")
        print("     - Restart your server")
    else:
        print("  📝 Using test mode for now.")
        print("     - Keep TEST_MODE=true in .env")
        print("     - Embeddings will work but won't persist")

if __name__ == "__main__":
    main()