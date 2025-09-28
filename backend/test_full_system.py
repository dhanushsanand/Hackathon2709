#!/usr/bin/env python3
"""
End-to-End PDF Quiz System Test
Tests the complete workflow: PDF Upload → Processing → Quiz Generation → Quiz Taking
"""

import asyncio
import requests
import json
import time
import io
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "test_token"

def create_test_pdf():
    """Create a simple test PDF content"""
    # Simple PDF-like content for testing
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Machine Learning Fundamentals) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000074 00000 n 
0000000120 00000 n 
0000000179 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
273
%%EOF"""
    return pdf_content

def test_server_health():
    """Test if the server is running"""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure server is running: python main.py")
        return False

def test_authentication():
    """Test authentication with test token"""
    print("\n🔐 Testing Authentication...")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authentication successful")
            print(f"   User ID: {user_data.get('uid')}")
            print(f"   Email: {user_data.get('email')}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_embedding_status():
    """Test embedding service status"""
    print("\n🧠 Testing Embedding Service...")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/test/embeddings/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Embedding service status:")
            print(f"   Provider: {status_data.get('provider_info', {}).get('provider', 'unknown')}")
            print(f"   Service: {status_data.get('embedding_service', 'unknown')}")
            print(f"   Pinecone: {status_data.get('pinecone_vector_db', 'unknown')}")
            print(f"   Dimension: {status_data.get('embedding_dimension', 0)}")
            return True
        else:
            print(f"❌ Embedding status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Embedding status test failed: {e}")
        return False

def test_pdf_upload():
    """Test PDF upload"""
    print("\n📄 Testing PDF Upload...")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Create test PDF
        pdf_content = create_test_pdf()
        
        files = {
            'file': ('test_document.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        response = requests.post(
            f"{BASE_URL}/pdf/upload", 
            headers=headers, 
            files=files, 
            timeout=30
        )
        
        if response.status_code == 200:
            upload_data = response.json()
            pdf_id = upload_data.get('pdf_id')
            print(f"✅ PDF uploaded successfully")
            print(f"   PDF ID: {pdf_id}")
            print(f"   Status: {upload_data.get('status')}")
            return True, pdf_id
        else:
            print(f"❌ PDF upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ PDF upload test failed: {e}")
        return False, None

def test_pdf_processing(pdf_id: str, max_wait: int = 60):
    """Test PDF processing completion"""
    print(f"\n⚙️  Testing PDF Processing (PDF ID: {pdf_id})...")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = requests.get(f"{BASE_URL}/pdf/{pdf_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                pdf_data = response.json()
                status = pdf_data.get('status', 'unknown')
                
                print(f"   📊 Processing status: {status}")
                
                if status == 'completed':
                    print("✅ PDF processing completed")
                    print(f"   Content chunks: {len(pdf_data.get('content_chunks', []))}")
                    print(f"   Embedding IDs: {len(pdf_data.get('embedding_ids', []))}")
                    return True, pdf_data
                elif status == 'failed':
                    print("❌ PDF processing failed")
                    return False, None
                else:
                    print(f"   ⏳ Still processing... ({int(time.time() - start_time)}s)")
                    time.sleep(3)
            else:
                print(f"❌ Error checking PDF status: {response.status_code}")
                return False, None
        
        print(f"⏰ PDF processing timed out after {max_wait}s")
        return False, None
        
    except Exception as e:
        print(f"❌ PDF processing test failed: {e}")
        return False, None

def test_quiz_generation(pdf_id: str):
    """Test quiz generation from PDF"""
    print(f"\n🎯 Testing Quiz Generation (PDF ID: {pdf_id})...")
    
    try:
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        
        quiz_request = {
            "num_questions": 3,
            "difficulty_range": [1, 3]
        }
        
        response = requests.post(
            f"{BASE_URL}/quiz/generate/{pdf_id}",
            headers=headers,
            json=quiz_request,
            timeout=60
        )
        
        if response.status_code == 200:
            quiz_data = response.json()
            quiz_id = quiz_data.get('id')
            questions = quiz_data.get('questions', [])
            
            print(f"✅ Quiz generated successfully")
            print(f"   Quiz ID: {quiz_id}")
            print(f"   Questions: {len(questions)}")
            
            # Show sample question
            if questions:
                sample_q = questions[0]
                print(f"   Sample question: {sample_q.get('question_text', '')[:100]}...")
                print(f"   Question type: {sample_q.get('question_type', 'unknown')}")
            
            return True, quiz_id, quiz_data
        else:
            print(f"❌ Quiz generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None, None
            
    except Exception as e:
        print(f"❌ Quiz generation test failed: {e}")
        return False, None, None

def test_quiz_taking(quiz_id: str, quiz_data: Dict[Any, Any]):
    """Test taking the quiz"""
    print(f"\n📝 Testing Quiz Taking (Quiz ID: {quiz_id})...")
    
    try:
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Get quiz details first
        response = requests.get(f"{BASE_URL}/quiz/{quiz_id}", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Cannot get quiz details: {response.status_code}")
            return False
        
        quiz_details = response.json()
        questions = quiz_details.get('questions', [])
        
        if not questions:
            print("❌ No questions found in quiz")
            return False
        
        # Generate sample answers
        answers = {}
        for question in questions:
            q_id = question.get('id')
            q_type = question.get('question_type')
            options = question.get('options', [])
            
            if q_type == 'multiple_choice' and options:
                answers[q_id] = options[0]  # Pick first option
            elif q_type == 'true_false':
                answers[q_id] = "True"
            else:
                answers[q_id] = "This is a sample answer"
        
        print(f"   📋 Submitting answers for {len(answers)} questions...")
        
        # Submit quiz
        submission = {"answers": answers}
        response = requests.post(
            f"{BASE_URL}/quiz/{quiz_id}/submit",
            headers=headers,
            json=submission,
            timeout=30
        )
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"✅ Quiz submitted successfully")
            print(f"   Score: {result_data.get('score', 0):.1f}")
            print(f"   Correct answers: {result_data.get('correct_answers', 0)}/{result_data.get('total_questions', 0)}")
            return True
        else:
            print(f"❌ Quiz submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Quiz taking test failed: {e}")
        return False

def test_user_dashboard():
    """Test user dashboard"""
    print("\n📊 Testing User Dashboard...")
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/user/dashboard", headers=headers, timeout=10)
        
        if response.status_code == 200:
            dashboard_data = response.json()
            print("✅ Dashboard loaded successfully")
            print(f"   Total PDFs: {dashboard_data.get('total_pdfs', 0)}")
            print(f"   Total quizzes: {dashboard_data.get('total_quizzes', 0)}")
            print(f"   Average score: {dashboard_data.get('average_score', 0):.1f}")
            return True
        else:
            print(f"❌ Dashboard test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

async def main():
    """Run complete end-to-end system test"""
    print("🧪 End-to-End PDF Quiz System Test")
    print("=" * 50)
    
    results = {}
    pdf_id = None
    quiz_id = None
    
    # Test 1: Server health
    results["server_health"] = test_server_health()
    if not results["server_health"]:
        print("\n❌ Server not available. Cannot continue tests.")
        return
    
    # Test 2: Authentication
    results["authentication"] = test_authentication()
    if not results["authentication"]:
        print("\n❌ Authentication failed. Cannot continue tests.")
        return
    
    # Test 3: Embedding service
    results["embedding_service"] = test_embedding_status()
    
    # Test 4: PDF upload
    upload_success, pdf_id = test_pdf_upload()
    results["pdf_upload"] = upload_success
    
    if upload_success and pdf_id:
        # Test 5: PDF processing
        processing_success, pdf_data = test_pdf_processing(pdf_id)
        results["pdf_processing"] = processing_success
        
        if processing_success:
            # Test 6: Quiz generation
            quiz_success, quiz_id, quiz_data = test_quiz_generation(pdf_id)
            results["quiz_generation"] = quiz_success
            
            if quiz_success and quiz_id:
                # Test 7: Quiz taking
                results["quiz_taking"] = test_quiz_taking(quiz_id, quiz_data)
    
    # Test 8: User dashboard
    results["user_dashboard"] = test_user_dashboard()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 END-TO-END TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 PERFECT: Complete PDF Quiz System working flawlessly!")
        print("💡 Your system is fully functional:")
        print("   ✅ PDF upload and processing")
        print("   ✅ AI-powered quiz generation")
        print("   ✅ Interactive quiz taking")
        print("   ✅ User dashboard and analytics")
        print("   ✅ Unlimited local embeddings")
        
        print("\n🚀 Ready for production deployment!")
        
    elif passed >= total * 0.8:
        print("\n✅ EXCELLENT: System mostly working with minor issues.")
        print("💡 Check failed tests and fix before production.")
        
    else:
        print("\n⚠️  ISSUES: Several components need attention.")
        print("💡 Fix failed tests before using the system.")
    
    # Cleanup info
    if pdf_id:
        print(f"\n🧹 Test artifacts created:")
        print(f"   PDF ID: {pdf_id}")
        if quiz_id:
            print(f"   Quiz ID: {quiz_id}")
        print("💡 These will be cleaned up automatically or can be deleted manually.")

if __name__ == "__main__":
    asyncio.run(main())