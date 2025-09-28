#!/usr/bin/env python3
"""
Load Testing and Performance Analysis
Tests system performance under various loads and concurrent users
"""

import asyncio
import aiohttp
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "test_token"

class PerformanceTest:
    def __init__(self):
        self.results = []
        self.errors = []
    
    async def single_embedding_test(self, session: aiohttp.ClientSession, test_id: int):
        """Single embedding generation test"""
        try:
            start_time = time.time()
            
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            data = {
                "texts": [
                    f"Test embedding generation number {test_id} for performance analysis.",
                    f"This is another test sentence {test_id} to measure embedding speed.",
                    f"Performance testing with concurrent requests {test_id}."
                ],
                "test_query": f"performance test {test_id}"
            }
            
            async with session.post(
                f"{BASE_URL}/test/embeddings",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                end_time = time.time()
                
                if response.status == 200:
                    result_data = await response.json()
                    duration = end_time - start_time
                    
                    self.results.append({
                        "test_id": test_id,
                        "duration": duration,
                        "embeddings_generated": result_data.get("embeddings_generated", 0),
                        "status": "success"
                    })
                    return True, duration
                else:
                    self.errors.append({
                        "test_id": test_id,
                        "status_code": response.status,
                        "error": "HTTP error"
                    })
                    return False, 0
                    
        except Exception as e:
            self.errors.append({
                "test_id": test_id,
                "error": str(e)
            })
            return False, 0

    async def concurrent_embedding_test(self, num_concurrent: int):
        """Test concurrent embedding requests"""
        print(f"🔄 Testing {num_concurrent} concurrent embedding requests...")
        
        connector = aiohttp.TCPConnector(limit=100)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            
            start_time = time.time()
            
            for i in range(num_concurrent):
                task = self.single_embedding_test(session, i)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            successful = sum(1 for result in results if isinstance(result, tuple) and result[0])
            failed = num_concurrent - successful
            
            if successful > 0:
                durations = [result[1] for result in results if isinstance(result, tuple) and result[0]]
                avg_duration = statistics.mean(durations)
                min_duration = min(durations)
                max_duration = max(durations)
                
                print(f"   ✅ {successful}/{num_concurrent} requests successful")
                print(f"   ⏱️  Total time: {total_time:.2f}s")
                print(f"   📊 Avg response time: {avg_duration:.2f}s")
                print(f"   📈 Min/Max response: {min_duration:.2f}s / {max_duration:.2f}s")
                print(f"   🚀 Throughput: {successful/total_time:.2f} req/s")
                
                return {
                    "concurrent_requests": num_concurrent,
                    "successful": successful,
                    "failed": failed,
                    "total_time": total_time,
                    "avg_response_time": avg_duration,
                    "min_response_time": min_duration,
                    "max_response_time": max_duration,
                    "throughput": successful/total_time
                }
            else:
                print(f"   ❌ All {num_concurrent} requests failed")
                return None

async def test_embedding_performance():
    """Test embedding generation performance"""
    print("⚡ Testing Embedding Performance...")
    print("-" * 40)
    
    test = PerformanceTest()
    
    # Test different concurrency levels
    concurrency_levels = [1, 3, 5, 10]
    performance_results = []
    
    for level in concurrency_levels:
        result = await test.concurrent_embedding_test(level)
        if result:
            performance_results.append(result)
        
        # Brief pause between tests
        await asyncio.sleep(2)
    
    return performance_results, test.errors

async def test_api_response_times():
    """Test various API endpoint response times"""
    print("\n🌐 Testing API Response Times...")
    print("-" * 40)
    
    endpoints = [
        ("Health Check", "GET", "/health", None),
        ("Auth Status", "GET", "/auth/me", {"Authorization": f"Bearer {AUTH_TOKEN}"}),
        ("Embedding Status", "GET", "/test/embeddings/status", {"Authorization": f"Bearer {AUTH_TOKEN}"}),
        ("Pinecone Info", "GET", "/test/pinecone/info", {"Authorization": f"Bearer {AUTH_TOKEN}"}),
        ("User Dashboard", "GET", "/user/dashboard", {"Authorization": f"Bearer {AUTH_TOKEN}"})
    ]
    
    results = []
    
    connector = aiohttp.TCPConnector(limit=10)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for name, method, endpoint, headers in endpoints:
            try:
                start_time = time.time()
                
                if method == "GET":
                    async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        print(f"   {name}: {duration:.3f}s (Status: {response.status})")
                        
                        results.append({
                            "endpoint": name,
                            "duration": duration,
                            "status": response.status,
                            "success": 200 <= response.status < 300
                        })
                        
            except Exception as e:
                print(f"   {name}: ERROR - {e}")
                results.append({
                    "endpoint": name,
                    "duration": 0,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                })
    
    return results

async def test_memory_usage():
    """Test memory usage during operations"""
    print("\n💾 Testing Memory Usage...")
    print("-" * 40)
    
    try:
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        
        # Initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"   📊 Initial memory usage: {initial_memory:.1f} MB")
        
        # Test embedding generation
        test = PerformanceTest()
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Generate multiple embeddings
            for i in range(5):
                await test.single_embedding_test(session, i)
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"   📈 After test {i+1}: {current_memory:.1f} MB (+{current_memory-initial_memory:.1f} MB)")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"   📊 Final memory usage: {final_memory:.1f} MB")
        print(f"   📈 Total increase: {memory_increase:.1f} MB")
        
        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase
        }
        
    except ImportError:
        print("   ⚠️  psutil not available, skipping memory test")
        print("   💡 Install with: pip install psutil")
        return None
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
        return None

async def main():
    """Run comprehensive performance tests"""
    print("🧪 Load Testing and Performance Analysis")
    print("=" * 50)
    
    # Test 1: Embedding performance
    embedding_results, embedding_errors = await test_embedding_performance()
    
    # Test 2: API response times
    api_results = await test_api_response_times()
    
    # Test 3: Memory usage
    memory_results = await test_memory_usage()
    
    # Analysis and Summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 50)
    
    # Embedding performance summary
    if embedding_results:
        print("\n🧠 Embedding Performance:")
        for result in embedding_results:
            concurrent = result["concurrent_requests"]
            throughput = result["throughput"]
            avg_time = result["avg_response_time"]
            success_rate = (result["successful"] / concurrent) * 100
            
            print(f"   {concurrent:2d} concurrent: {throughput:.1f} req/s, {avg_time:.2f}s avg, {success_rate:.0f}% success")
    
    # API performance summary
    if api_results:
        print("\n🌐 API Response Times:")
        successful_apis = [r for r in api_results if r["success"]]
        if successful_apis:
            avg_api_time = statistics.mean([r["duration"] for r in successful_apis])
            print(f"   Average API response: {avg_api_time:.3f}s")
            
            fastest = min(successful_apis, key=lambda x: x["duration"])
            slowest = max(successful_apis, key=lambda x: x["duration"])
            print(f"   Fastest: {fastest['endpoint']} ({fastest['duration']:.3f}s)")
            print(f"   Slowest: {slowest['endpoint']} ({slowest['duration']:.3f}s)")
    
    # Memory usage summary
    if memory_results:
        print(f"\n💾 Memory Usage:")
        print(f"   Memory increase: {memory_results['memory_increase_mb']:.1f} MB")
        if memory_results['memory_increase_mb'] < 50:
            print("   ✅ Memory usage is reasonable")
        elif memory_results['memory_increase_mb'] < 100:
            print("   ⚠️  Moderate memory usage")
        else:
            print("   ❌ High memory usage - consider optimization")
    
    # Error summary
    if embedding_errors:
        print(f"\n❌ Errors Detected: {len(embedding_errors)}")
        error_types = {}
        for error in embedding_errors:
            error_type = error.get("error", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"   {error_type}: {count} occurrences")
    
    # Recommendations
    print("\n💡 PERFORMANCE RECOMMENDATIONS:")
    
    if embedding_results:
        best_throughput = max(embedding_results, key=lambda x: x["throughput"])
        print(f"   🚀 Optimal concurrency: {best_throughput['concurrent_requests']} requests")
        print(f"   📈 Peak throughput: {best_throughput['throughput']:.1f} req/s")
    
    if api_results:
        failed_apis = [r for r in api_results if not r["success"]]
        if failed_apis:
            print(f"   ⚠️  {len(failed_apis)} API endpoints need attention")
        else:
            print("   ✅ All API endpoints responding well")
    
    print("\n🎯 PRODUCTION READINESS:")
    
    # Calculate overall score
    scores = []
    
    # Embedding performance score
    if embedding_results and embedding_results[-1]["throughput"] > 1.0:
        scores.append(1)
        print("   ✅ Embedding performance: Good")
    else:
        scores.append(0)
        print("   ⚠️  Embedding performance: Needs improvement")
    
    # API performance score
    if api_results:
        success_rate = sum(1 for r in api_results if r["success"]) / len(api_results)
        if success_rate > 0.8:
            scores.append(1)
            print("   ✅ API reliability: Good")
        else:
            scores.append(0)
            print("   ⚠️  API reliability: Needs improvement")
    
    # Memory usage score
    if memory_results and memory_results['memory_increase_mb'] < 100:
        scores.append(1)
        print("   ✅ Memory usage: Acceptable")
    elif memory_results:
        scores.append(0)
        print("   ⚠️  Memory usage: High")
    else:
        scores.append(0.5)  # Unknown
        print("   ❓ Memory usage: Unknown")
    
    overall_score = sum(scores) / len(scores) if scores else 0
    
    if overall_score >= 0.8:
        print(f"\n🎉 EXCELLENT: System ready for production! (Score: {overall_score:.1%})")
    elif overall_score >= 0.6:
        print(f"\n✅ GOOD: System mostly ready with minor optimizations needed (Score: {overall_score:.1%})")
    else:
        print(f"\n⚠️  NEEDS WORK: Significant performance improvements required (Score: {overall_score:.1%})")

if __name__ == "__main__":
    asyncio.run(main())