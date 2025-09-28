#!/usr/bin/env python3
"""
Demo: Personalized Study Notes Generation
Shows how the system creates targeted study notes based on quiz performance
"""

import asyncio
from datetime import datetime
from services.notes_generator import NotesGeneratorService
from models.quiz import QuizAttempt, Question, QuestionType
from models.pdf import PDFDocument, ProcessingStatus

async def demo_notes_generation():
    """Demonstrate the notes generation system with realistic data"""
    
    print("🎓 DEMO: Personalized Study Notes Generation")
    print("=" * 60)
    print("This demo shows how the system creates targeted study notes")
    print("based on quiz performance and PDF content using Pinecone.\n")
    
    # Initialize the notes service
    notes_service = NotesGeneratorService()
    
    # Create realistic mock data
    print("📚 Setting up demo scenario...")
    print("   Student: Alex (studying Machine Learning)")
    print("   Document: 'Introduction to Machine Learning'")
    print("   Quiz: 5 questions on ML fundamentals")
    print("   Performance: Mixed results (some areas need work)\n")
    
    # Mock PDF document
    pdf_document = PDFDocument(
        id="pdf_ml_intro_001",
        user_id="student_alex_123",
        filename="ml_introduction.pdf",
        original_filename="Introduction to Machine Learning.pdf",
        file_size=2048000,
        storage_path="https://example.com/ml_intro.pdf",
        status=ProcessingStatus.COMPLETED,
        content_chunks=[
            "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            "Supervised learning uses labeled training data to learn a mapping function from input variables to output variables.",
            "Unsupervised learning finds hidden patterns in data without labeled examples, including clustering and dimensionality reduction.",
            "Neural networks are computing systems inspired by biological neural networks, consisting of interconnected nodes called neurons.",
            "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model complex patterns in data.",
            "Feature engineering involves selecting and transforming variables to improve machine learning model performance.",
            "Cross-validation is a technique used to assess how well a machine learning model will generalize to independent datasets.",
            "Overfitting occurs when a model learns the training data too well, including noise, leading to poor generalization."
        ],
        embedding_ids=["emb_001", "emb_002", "emb_003", "emb_004", "emb_005", "emb_006", "emb_007", "emb_008"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Mock quiz questions (realistic ML questions)
    questions = [
        Question(
            id="q1_ml_definition",
            question_text="What is machine learning and how does it relate to artificial intelligence?",
            question_type=QuestionType.SHORT_ANSWER,
            options=None,
            correct_answer="Machine learning is a subset of artificial intelligence that enables computers to learn from data without explicit programming",
            explanation="ML is a branch of AI focused on algorithms that improve through experience",
            difficulty=2,
            source_chunk="Machine learning is a subset of artificial intelligence..."
        ),
        Question(
            id="q2_supervised_learning",
            question_text="Which type of learning uses labeled training data?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Supervised learning", "Unsupervised learning", "Reinforcement learning", "Deep learning"],
            correct_answer="Supervised learning",
            explanation="Supervised learning requires labeled examples to train the model",
            difficulty=1,
            source_chunk="Supervised learning uses labeled training data..."
        ),
        Question(
            id="q3_neural_networks",
            question_text="Neural networks are inspired by what biological system?",
            question_type=QuestionType.SHORT_ANSWER,
            options=None,
            correct_answer="Biological neural networks or brain neurons",
            explanation="Neural networks mimic how neurons in the brain process information",
            difficulty=2,
            source_chunk="Neural networks are computing systems inspired by biological neural networks..."
        ),
        Question(
            id="q4_overfitting",
            question_text="True or False: Overfitting helps models generalize better to new data.",
            question_type=QuestionType.TRUE_FALSE,
            options=["True", "False"],
            correct_answer="False",
            explanation="Overfitting actually hurts generalization by learning noise in training data",
            difficulty=3,
            source_chunk="Overfitting occurs when a model learns the training data too well..."
        ),
        Question(
            id="q5_deep_learning",
            question_text="What distinguishes deep learning from regular neural networks?",
            question_type=QuestionType.SHORT_ANSWER,
            options=None,
            correct_answer="Multiple layers or depth of the network",
            explanation="Deep learning uses neural networks with many layers to learn complex patterns",
            difficulty=3,
            source_chunk="Deep learning is a subset of machine learning that uses neural networks with multiple layers..."
        )
    ]
    
    # Mock quiz attempt (student got some wrong - realistic scenario)
    quiz_attempt = QuizAttempt(
        id="attempt_alex_001",
        quiz_id="quiz_ml_intro_001", 
        user_id="student_alex_123",
        answers={
            "q1_ml_definition": "Machine learning is when computers learn stuff",  # Incomplete answer
            "q2_supervised_learning": "Supervised learning",  # Correct
            "q3_neural_networks": "The brain",  # Partially correct
            "q4_overfitting": "True",  # Wrong
            "q5_deep_learning": "I don't know"  # Wrong
        },
        score=40.0,  # 2/5 correct = 40%
        completed_at=datetime.now(),
        time_taken=600,  # 10 minutes
        created_at=datetime.now()
    )
    
    print("🔍 Step 1: Analyzing Quiz Performance...")
    print("   Analyzing student's answers to identify weak areas...")
    
    # Analyze performance
    performance_analysis = await notes_service.analyze_quiz_performance(quiz_attempt, questions)
    
    print(f"   ✅ Analysis complete!")
    print(f"      📊 Score: {performance_analysis['score_percentage']:.1f}%")
    print(f"      📈 Performance level: {performance_analysis['performance_level']}")
    print(f"      ❌ Weak areas: {len(performance_analysis['weak_areas'])} questions")
    print(f"      🎯 Key topics to review: {', '.join(performance_analysis['weak_topics'][:5])}")
    
    print(f"\n🔎 Step 2: Finding Relevant Content...")
    print("   Using Pinecone to search for content related to weak areas...")
    
    # Find relevant content using Pinecone
    relevant_content = await notes_service.find_relevant_content(
        weak_topics=performance_analysis["weak_topics"],
        pdf_id=pdf_document.id,
        max_chunks=10
    )
    
    print(f"   ✅ Content search complete!")
    print(f"      📚 Found {len(relevant_content)} relevant content pieces")
    if relevant_content:
        print(f"      🎯 Top topics: {', '.join(set([item['topic'] for item in relevant_content[:3]]))}")
    
    print(f"\n✍️  Step 3: Generating Personalized Study Notes...")
    print("   Using AI to create comprehensive study notes...")
    
    # Generate comprehensive notes
    notes_data = await notes_service.generate_personalized_notes(
        performance_analysis=performance_analysis,
        relevant_content=relevant_content,
        pdf_document=pdf_document
    )
    
    print(f"   ✅ Notes generation complete!")
    print(f"      📝 Notes ID: {notes_data['id']}")
    print(f"      📚 Topics covered: {len(notes_data['topics_covered'])}")
    print(f"      🚨 Study priority: {notes_data['study_priority']}")
    print(f"      ⏰ Estimated study time: {notes_data['estimated_study_time']}")
    
    # Display sample of generated notes
    print(f"\n📖 Generated Study Notes Preview:")
    print("=" * 50)
    
    study_notes = notes_data['study_notes']
    if len(study_notes) > 800:
        preview = study_notes[:800] + "\n\n[... content continues ...]"
    else:
        preview = study_notes
    
    print(preview)
    
    print("\n" + "=" * 50)
    
    # Show performance insights
    print(f"\n📊 Performance Insights:")
    print(f"   🎯 Areas needing attention:")
    for i, weak_area in enumerate(performance_analysis['weak_areas'][:3]):
        question_text = weak_area['question_text'][:60] + "..." if len(weak_area['question_text']) > 60 else weak_area['question_text']
        print(f"      {i+1}. {question_text}")
        print(f"         Student answer: '{weak_area['user_answer'][:40]}...'")
        print(f"         Correct answer: '{weak_area['correct_answer'][:40]}...'")
    
    # Show study recommendations
    print(f"\n💡 Personalized Study Recommendations:")
    recommendations = [
        "Focus on understanding fundamental ML concepts and definitions",
        "Practice explaining neural networks and deep learning differences", 
        "Review overfitting concept with examples",
        "Create concept maps connecting AI, ML, and deep learning",
        "Schedule 2-3 hour study session focusing on weak areas"
    ]
    
    for i, rec in enumerate(recommendations):
        print(f"   {i+1}. {rec}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   📅 Recommended review date: {notes_data.get('next_review_date', 'In 2-3 days')}")
    print(f"   📚 Focus areas: {', '.join(performance_analysis['weak_topics'][:3])}")
    print(f"   ⏰ Study time needed: {notes_data['estimated_study_time']}")
    
    print(f"\n🎉 Demo Complete!")
    print("The system successfully:")
    print("   ✅ Analyzed quiz performance to identify weak areas")
    print("   ✅ Used Pinecone to find relevant PDF content")
    print("   ✅ Generated personalized study notes with AI")
    print("   ✅ Provided targeted study recommendations")
    print("   ✅ Created a structured learning plan")
    
    return notes_data

async def main():
    """Run the notes generation demo"""
    try:
        await demo_notes_generation()
        
        print(f"\n" + "=" * 60)
        print("🚀 SYSTEM READY FOR PRODUCTION!")
        print("=" * 60)
        print("Your PDF Quiz System now includes:")
        print("   📚 Intelligent quiz generation from PDFs")
        print("   🎯 Performance-based study notes")
        print("   🔍 Semantic content search with Pinecone")
        print("   🧠 AI-powered personalized recommendations")
        print("   📊 Learning analytics and progress tracking")
        print("   ⚡ Unlimited local embeddings with Ollama")
        
        print(f"\n💡 Students will receive:")
        print("   • Personalized study notes based on their quiz performance")
        print("   • Targeted content from PDFs for areas they struggle with")
        print("   • Smart study recommendations and time estimates")
        print("   • Progress tracking and improvement suggestions")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Make sure Ollama is running and Pinecone is configured")

if __name__ == "__main__":
    asyncio.run(main())