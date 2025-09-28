#!/usr/bin/env python3
"""
Master Test Runner
Runs all tests in sequence and provides comprehensive system analysis
"""

import asyncio
import subprocess
import sys
import time
from typing import Dict, Any, List

class TestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
    
    def run_sync_test(self, test_name: str, script_path: str) -> bool:
        """Run a synchronous test script"""
        print(f"\n🧪 Running {test_name}...")
        print("=" * 60)
        
        try:
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=False, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            success = result.returncode == 0
            self.test_results[test_name] = {
                "success": success,
                "return_code": result.returncode,
                "type": "sync"
            }
            
            if success:
                print(f"\n✅ {test_name} completed successfully")
            else:
                print(f"\n❌ {test_name} failed with return code {result.returncode}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"\n⏰ {test_name} timed out after 5 minutes")
            self.test_results[test_name] = {
                "success": False,
                "error": "timeout",
                "type": "sync"
            }
            return False
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {e}")
            self.test_results[test_name] = {
                "success": False,
                "error": str(e),
                "type": "sync"
            }
            return False
    
    async def run_async_test(self, test_name: str, test_function) -> bool:
        """Run an asynchronous test function"""
        print(f"\n🧪 Running {test_name}...")
        print("=" * 60)
        
        try:
            success = await test_function()
            self.test_results[test_name] = {
                "success": success,
                "type": "async"
            }
            
            if success:
                print(f"\n✅ {test_name} completed successfully")
            else:
                print(f"\n❌ {test_name} failed")
            
            return success
            
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {e}")
            self.test_results[test_name] = {
                "success": False,
                "error": str(e),
                "type": "async"
            }
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST SUITE SUMMARY")
        print("=" * 80)
        
        # Test results
        passed_tests = []
        failed_tests = []
        
        for test_name, result in self.test_results.items():
            if result["success"]:
                passed_tests.append(test_name)
            else:
                failed_tests.append(test_name)
        
        print(f"\n📊 Test Results:")
        print(f"   ✅ Passed: {len(passed_tests)}")
        print(f"   ❌ Failed: {len(failed_tests)}")
        print(f"   📈 Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print(f"   ⏱️  Total Time: {total_time:.1f} seconds")
        
        # Detailed results
        if passed_tests:
            print(f"\n✅ Passed Tests:")
            for test in passed_tests:
                print(f"   • {test}")
        
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                error = self.test_results[test].get("error", "Unknown error")
                print(f"   • {test}: {error}")
        
        # System assessment
        print(f"\n🎯 SYSTEM ASSESSMENT:")
        
        critical_tests = [
            "Ollama Integration Test",
            "Pinecone + Ollama Integration", 
            "End-to-End System Test"
        ]
        
        critical_passed = sum(1 for test in critical_tests if test in passed_tests)
        
        if critical_passed == len(critical_tests):
            print("   🎉 PRODUCTION READY: All critical systems working!")
            print("   💡 Your PDF Quiz System is fully functional")
            
        elif critical_passed >= len(critical_tests) * 0.8:
            print("   ✅ MOSTLY READY: Core functionality working with minor issues")
            print("   💡 Address failed tests before production deployment")
            
        else:
            print("   ⚠️  NEEDS WORK: Critical systems have issues")
            print("   💡 Fix failed tests before using the system")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if "Ollama Integration Test" in failed_tests:
            print("   🔧 Install and configure Ollama for unlimited embeddings")
            print("      - Run: curl -fsSL https://ollama.com/install.sh | sh")
            print("      - Start: ollama serve")
            print("      - Pull model: ollama pull nomic-embed-text")
        
        if "Pinecone + Ollama Integration" in failed_tests:
            print("   🔧 Check Pinecone configuration and network connectivity")
            print("      - Verify API key in .env file")
            print("      - Test network: ping api.pinecone.io")
        
        if "End-to-End System Test" in failed_tests:
            print("   🔧 Check server configuration and dependencies")
            print("      - Ensure server is running: python main.py")
            print("      - Check all environment variables in .env")
        
        if "Load Performance Test" in failed_tests:
            print("   🔧 Performance optimization may be needed")
            print("      - Monitor system resources during operation")
            print("      - Consider scaling if handling high loads")
        
        # Next steps
        print(f"\n🚀 NEXT STEPS:")
        
        if len(passed_tests) == len(self.test_results):
            print("   1. Deploy to production environment")
            print("   2. Set up monitoring and logging")
            print("   3. Configure backup and disaster recovery")
            print("   4. Train users on the system")
            
        else:
            print("   1. Fix failed tests identified above")
            print("   2. Re-run tests to verify fixes")
            print("   3. Proceed with deployment once all tests pass")
        
        print(f"\n📚 DOCUMENTATION:")
        print("   • API Testing: Use postman_collection_updated.json")
        print("   • Ollama Setup: See OLLAMA_SETUP.md")
        print("   • Pinecone Setup: See PINECONE_SETUP.md")
        print("   • Embedding Guide: See EMBEDDING_TESTING_GUIDE.md")

async def main():
    """Run all tests in sequence"""
    print("🧪 COMPREHENSIVE PDF QUIZ SYSTEM TEST SUITE")
    print("=" * 80)
    print("This will run all available tests to verify system functionality")
    print("Estimated time: 5-10 minutes depending on system performance")
    
    runner = TestRunner()
    
    # Define test sequence
    tests = [
        ("Quick Pinecone Test", "quick_pinecone_test.py"),
        ("Ollama Integration Test", "test_ollama.py"),
        ("Pinecone + Ollama Integration", "test_pinecone_ollama.py"),
        ("End-to-End System Test", "test_full_system.py"),
        ("Load Performance Test", "test_load_performance.py")
    ]
    
    # Run all tests
    for test_name, script_path in tests:
        try:
            runner.run_sync_test(test_name, script_path)
            
            # Brief pause between tests
            await asyncio.sleep(2)
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Test suite interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error running {test_name}: {e}")
            runner.test_results[test_name] = {
                "success": False,
                "error": str(e),
                "type": "error"
            }
    
    # Print comprehensive summary
    runner.print_summary()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
        print("💡 Run individual tests if needed:")
        print("   python test_ollama.py")
        print("   python test_pinecone_ollama.py")
        print("   python test_full_system.py")