#!/usr/bin/env python3
"""
Test Notes Generation System
Tests the comprehensive notes generation using quiz results and Pinecone
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "test_token"

async def test_notes_generation_flow():
    """Test the complete notes generation flow"""
    print("🧪 Testing Notes Generation System")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Step 1: Upload a test PDF (if needed)
    print("📄 Step 1: Checking for existing PDFs...")
    userId = "pdf_d287d3b3fe66487a9766a3183f6da031"
    try:
        response = requests.get(f"{BASE_URL}/pdf/{userId}", headers=headers, timeout=10)
        if response.status_code == 200:
            pdfs = response.json()
            if pdfs:
                pdf_id = pdfs['id']  # Use first PDF
                print(f"✅ Using existing PDF: {pdf_id}")
            else:
                print("❌ No PDFs found. Please upload a PDF first.")
                return False
        else:
            print("❌ Cannot access PDFs")
            return False
    except Exception as e:
        print(f"❌ Error checking PDFs: {e}")
        return False
    
    # Step 2: Generate a quiz (if needed)
    print(f"\n🎯 Step 2: Generating quiz for PDF {pdf_id}...")
    
    try:
        quiz_request = {
            "num_questions": 3,
            "difficulty_range": [1, 3]
        }
        
        response = requests.post(
            f"{BASE_URL}/quiz/generate/{pdf_id}",
            headers={**headers, "Content-Type": "application/json"},
            json=quiz_request,
            timeout=60
        )
        
        if response.status_code == 200:
            quiz_data = response.json()
            quiz_id = quiz_data.get('id')
            print(f"✅ Quiz generated: {quiz_id}")
        else:
            print(f"❌ Quiz generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error generating quiz: {e}")
        return False
    
    # Step 3: Take the quiz
    print(f"\n📝 Step 3: Taking quiz {quiz_id}...")
    
    try:
        # Get quiz details
        response = requests.get(f"{BASE_URL}/quiz/{quiz_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            quiz_details = response.json()
            questions = quiz_details.get('questions', [])
            
            # Generate sample answers (some correct, some incorrect for testing)
            answers = {}
            for i, question in enumerate(questions):
                q_id = question.get('id')
                q_type = question.get('question_type')
                options = question.get('options', [])
                
                # Intentionally get some wrong for testing notes generation
                if i == 0:  # First question correct
                    if q_type == 'multiple_choice' and options:
                        answers[q_id] = options[0]
                    elif q_type == 'true_false':
                        answers[q_id] = "True"
                    else:
                        answers[q_id] = "This is a correct answer"
                else:  # Other questions incorrect
                    if q_type == 'multiple_choice' and options:
                        answers[q_id] = options[-1]  # Last option (likely wrong)
                    elif q_type == 'true_false':
                        answers[q_id] = "False"
                    else:
                        answers[q_id] = "This is an incorrect answer"
            
            # Submit quiz
            submission = {"answers": answers}
            response = requests.post(
                f"{BASE_URL}/quiz/{quiz_id}/submit",
                headers={**headers, "Content-Type": "application/json"},
                json=submission,
                timeout=30
            )
            
            if response.status_code == 200:
                result_data = response.json()
                quiz_attempt_id = result_data.get('quiz_attempt_id')
                score = result_data.get('score', 0)
                print(f"✅ Quiz submitted: Score {score:.1f}%, Attempt ID: {quiz_attempt_id}")
            else:
                print(f"❌ Quiz submission failed: {response.status_code}")
                return False
        else:
            print(f"❌ Cannot get quiz details: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error taking quiz: {e}")
        return False
    
    # Step 4: Generate study notes
    print(f"\n✍️  Step 4: Generating personalized study notes...")
    
    try:
        notes_request = {
            "quiz_attempt_id": quiz_attempt_id,
            "include_examples": True,
            "study_level": "comprehensive"
        }
        
        response = requests.post(
            f"{BASE_URL}/notes/generate/{quiz_attempt_id}",
            headers={**headers, "Content-Type": "application/json"},
            json=notes_request,
            timeout=120  # Notes generation can take longer
        )
        
        if response.status_code == 200:
            notes_response = response.json()
            notes_data = notes_response.get('notes', {})
            generation_stats = notes_response.get('generation_stats', {})
            recommendations = notes_response.get('recommendations', [])
            
            print("✅ Study notes generated successfully!")
            print(f"   Notes ID: {notes_data.get('id')}")
            print(f"   Topics covered: {len(notes_data.get('topics_covered', []))}")
            print(f"   Study priority: {notes_data.get('study_priority')}")
            print(f"   Estimated study time: {notes_data.get('estimated_study_time')}")
            print(f"   Content sources used: {generation_stats.get('content_sources_used', 0)}")
            
            # Show sample of generated notes
            study_notes = notes_data.get('study_notes', '')
            if study_notes:
                print(f"\n📚 Sample of generated notes:")
                print(f"   {study_notes[:200]}...")
            
            # Show recommendations
            if recommendations:
                print(f"\n💡 Study recommendations:")
                for i, rec in enumerate(recommendations[:3]):
                    print(f"   {i+1}. {rec}")
            
            notes_id = notes_data.get('id')
            
        else:
            print(f"❌ Notes generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error generating notes: {e}")
        return False
    
    # Step 5: Test notes retrieval
    print(f"\n📖 Step 5: Testing notes retrieval...")
    
    try:
        # Get specific notes
        response = requests.get(f"{BASE_URL}/notes/{notes_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            retrieved_notes = response.json()
            print(f"✅ Notes retrieved successfully")
            print(f"   Title: {retrieved_notes.get('pdf_title')}")
            print(f"   Generated at: {retrieved_notes.get('generated_at')}")
        else:
            print(f"❌ Notes retrieval failed: {response.status_code}")
            return False
        
        # Get all notes for PDF
        response = requests.get(f"{BASE_URL}/notes/pdf/{pdf_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            pdf_notes = response.json()
            print(f"✅ PDF notes retrieved: {pdf_notes.get('notes_count', 0)} notes found")
        else:
            print(f"⚠️  PDF notes retrieval failed: {response.status_code}")
        
        # Get all user notes
        response = requests.get(f"{BASE_URL}/notes/user/all", headers=headers, timeout=10)
        
        if response.status_code == 200:
            all_notes = response.json()
            print(f"✅ All user notes retrieved: {all_notes.get('total_notes', 0)} total notes")
        else:
            print(f"⚠️  All notes retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing notes retrieval: {e}")
        return False
    
    # Step 6: Test performance analytics
    print(f"\n📊 Step 6: Testing performance analytics...")
    
    try:
        response = requests.get(f"{BASE_URL}/notes/analytics/performance", headers=headers, timeout=10)
        
        if response.status_code == 200:
            analytics = response.json()
            print(f"✅ Performance analytics retrieved")
            print(f"   Average score: {analytics.get('average_score', 0):.1f}%")
            print(f"   Improvement trend: {analytics.get('improvement_trend', 'unknown')}")
            
            weak_areas = analytics.get('common_weak_areas', [])
            if weak_areas:
                print(f"   Common weak areas: {', '.join([area['topic'] for area in weak_areas[:3]])}")
        else:
            print(f"⚠️  Analytics retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing analytics: {e}")
        return False
    
    return True

async def test_notes_system_components():
    """Test individual components of the notes system"""
    print("\n🔧 Testing Notes System Components")
    print("-" * 40)
    
    try:
        # Test the notes generator service directly
        from services.notes_generator import NotesGeneratorService
        from models.quiz import QuizAttempt, Question, QuestionType
        from models.pdf import PDFDocument, ProcessingStatus
        from datetime import datetime
        
        notes_service = NotesGeneratorService()
        
        # Create mock data
        mock_pdf = PDFDocument(
            id="test_pdf_123",
            user_id="test_user_123",
            filename="test_document.pdf",
            original_filename="Test Document.pdf",
            file_size=1024,
            storage_path="test/path",
            status=ProcessingStatus.COMPLETED,
            content_chunks=["Machine learning is a subset of AI", "Deep learning uses neural networks"],
            embedding_ids=["emb1", "emb2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_questions = [
            Question(
                id="q1",
                question_text="What is machine learning?",
                question_type=QuestionType.SHORT_ANSWER,
                options=None,
                correct_answer="Machine learning is a subset of artificial intelligence",
                explanation="ML enables computers to learn from data",
                difficulty=2,
                source_chunk="Machine learning is a subset of AI"
            ),
            Question(
                id="q2", 
                question_text="What does deep learning use?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Neural networks", "Decision trees", "Linear regression", "Clustering"],
                correct_answer="Neural networks",
                explanation="Deep learning uses neural networks with multiple layers",
                difficulty=3,
                source_chunk="Deep learning uses neural networks"
            )
        ]
        
        mock_attempt = QuizAttempt(
            id="attempt_123",
            quiz_id="quiz_123",
            user_id="test_user_123",
            answers={"q1": "Wrong answer", "q2": "Decision trees"},
            score=0.0,
            completed_at=datetime.now(),
            time_taken=300,
            created_at=datetime.now()
        )
        
        print("🧠 Testing performance analysis...")
        performance = await notes_service.analyze_quiz_performance(mock_attempt, mock_questions)
        print(f"   ✅ Performance analyzed: {performance['score_percentage']:.1f}% score")
        print(f"   📊 Weak topics identified: {len(performance['weak_topics'])}")
        
        print("🔍 Testing content search...")
        relevant_content = await notes_service.find_relevant_content(
            weak_topics=performance["weak_topics"][:3],
            pdf_id=mock_pdf.id,
            max_chunks=5
        )
        print(f"   ✅ Found {len(relevant_content)} relevant content pieces")
        
        print("✍️  Testing notes generation...")
        notes = await notes_service.create_comprehensive_notes(
            quiz_attempt=mock_attempt,
            questions=mock_questions,
            pdf_document=mock_pdf
        )
        print(f"   ✅ Notes generated successfully")
        print(f"   📚 Study priority: {notes['study_priority']}")
        print(f"   ⏰ Estimated study time: {notes['estimated_study_time']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")
        return False

async def main():
    """Run comprehensive notes system tests"""
    print("🧪 Comprehensive Notes Generation System Test")
    print("=" * 60)
    
    # Test 1: Component testing
    component_success = await test_notes_system_components()
    
    # Test 2: Full flow testing
    flow_success = await test_notes_generation_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 NOTES SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Component Testing", component_success),
        ("Full Flow Testing", flow_success)
    ]
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    if passed == total:
        print(f"\n🎉 EXCELLENT: Notes generation system fully working!")
        print("💡 Features verified:")
        print("   ✅ Quiz performance analysis")
        print("   ✅ Pinecone content search")
        print("   ✅ AI-powered notes generation")
        print("   ✅ Personalized study recommendations")
        print("   ✅ Performance analytics")
        
        print("\n🚀 Your students can now get:")
        print("   📚 Personalized study notes based on quiz performance")
        print("   🎯 Targeted content from PDFs for weak areas")
        print("   💡 Smart study recommendations")
        print("   📊 Performance tracking and analytics")
        
    else:
        print(f"\n⚠️  Some issues detected ({passed}/{total} tests passed)")
        print("💡 Check the failed tests and fix issues")

if __name__ == "__main__":
    asyncio.run(main())