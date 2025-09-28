# utils/database.py
from firebase_admin import firestore
from typing import List, Optional, Dict, Any
from models.pdf import PDFDocument, ProcessingStatus
from models.quiz import Quiz, QuizAttempt
from models.user import User
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import settings

# Test storage for when database is not available
test_storage = {
    'pdfs': {},
    'quizzes': {},
    'quiz_attempts': {},
    'users': {},
    'recommendations': {},
    'notes': {}
}

# Initialize Firestore with error handling
db = None
executor = ThreadPoolExecutor(max_workers=4)

if not settings.test_mode:
    try:
        db = firestore.client()
        print("✅ Firestore initialized successfully")
    except Exception as e:
        print(f"⚠️  Firestore initialization failed: {e}")
        print("📝 Using test mode storage instead")
        db = None
else:
    print("🧪 Using test mode - in-memory storage")

# PDF Document Operations
async def save_pdf_document(pdf_doc: PDFDocument) -> None:
    """Save PDF document to Firestore (create if not exists)"""
    def _save():
        doc_ref = db.collection('pdfs').document(pdf_doc.id)
        # Use set with merge=True to create if not exists, update if exists
        doc_ref.set(pdf_doc.dict(), merge=True)
        print(f"✅ Saved/Updated PDF document: {pdf_doc.id}")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _save)

async def get_pdf_document(pdf_id: str) -> PDFDocument:
    """Get PDF document from Firestore"""
    def _get():
        doc_ref = db.collection('pdfs').document(pdf_id)
        doc = doc_ref.get()
        if doc.exists:
            return PDFDocument(**doc.to_dict())
        raise Exception("PDF not found")
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def update_pdf_status(pdf_id: str, status: ProcessingStatus) -> None:
    """Update PDF processing status"""
    def _update():
        doc_ref = db.collection('pdfs').document(pdf_id)
        doc_ref.update({
            'status': status.value,
            'updated_at': datetime.now()
        })
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _update)

async def get_pdfs_by_user_id(user_id: str) -> List[PDFDocument]:
    """Get all PDFs for a user"""
    try:
        def _get():
            docs = db.collection('pdfs').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            pdf_list = []
            for doc in docs:
                try:
                    pdf_data = doc.to_dict()
                    pdf_list.append(PDFDocument(**pdf_data))
                except Exception as e:
                    print(f"⚠️  Error parsing PDF document {doc.id}: {e}")
                    continue
            return pdf_list
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _get)
        print(f"✅ Retrieved {len(result)} PDFs for user {user_id}")
        return result
        
    except Exception as e:
        print(f"❌ Error retrieving PDFs for user {user_id}: {e}")
        return []

async def delete_pdf_document(pdf_id: str) -> None:
    """Delete PDF document and all related data"""
    try:
        def _delete():
            print(f"🗑️  Starting deletion of PDF {pdf_id}")
            
            # Count and delete related data
            deleted_counts = {
                'quizzes': 0,
                'quiz_attempts': 0,
                'study_notes': 0
            }
            
            # Delete related quizzes and their attempts
            quizzes = db.collection('quizzes').where('pdf_id', '==', pdf_id).stream()
            for quiz in quizzes:
                quiz_id = quiz.id
                
                # Delete quiz attempts for this quiz
                attempts = db.collection('quiz_attempts').where('quiz_id', '==', quiz_id).stream()
                for attempt in attempts:
                    attempt.reference.delete()
                    deleted_counts['quiz_attempts'] += 1
                
                # Delete the quiz
                quiz.reference.delete()
                deleted_counts['quizzes'] += 1
            
            # Delete related study notes
            notes = db.collection('study_notes').where('pdf_id', '==', pdf_id).stream()
            for note in notes:
                note.reference.delete()
                deleted_counts['study_notes'] += 1
            
            # Delete the PDF document
            db.collection('pdfs').document(pdf_id).delete()
            
            print(f"✅ Deleted PDF {pdf_id} and related data:")
            print(f"   📄 PDF: 1")
            print(f"   🎯 Quizzes: {deleted_counts['quizzes']}")
            print(f"   📝 Quiz Attempts: {deleted_counts['quiz_attempts']}")
            print(f"   📚 Study Notes: {deleted_counts['study_notes']}")
            
            return deleted_counts
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _delete)
        return result
        
    except Exception as e:
        print(f"❌ Error deleting PDF {pdf_id}: {e}")
        raise Exception(f"Failed to delete PDF: {str(e)}")

# Quiz Operations
async def save_quiz(quiz: Quiz) -> None:
    """Save quiz to Firestore (create if not exists)"""
    def _save():
        doc_ref = db.collection('quizzes').document(quiz.id)
        quiz_data = quiz.dict()
        # Convert questions to dict format
        quiz_data['questions'] = [q.dict() for q in quiz.questions]
        # Use set with merge=True to create if not exists, update if exists
        doc_ref.set(quiz_data, merge=True)
        print(f"✅ Saved/Updated quiz: {quiz.id}")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _save)

async def get_quiz(quiz_id: str) -> Quiz:
    """Get quiz from Firestore"""
    def _get():
        doc_ref = db.collection('quizzes').document(quiz_id)
        doc = doc_ref.get()
        if doc.exists:
            quiz_data = doc.to_dict()
            return Quiz(**quiz_data)
        raise Exception("Quiz not found")
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def get_quizzes_by_user_id(user_id: str) -> List[Quiz]:
    """Get all quizzes created by a user"""
    if settings.test_mode or db is None:
        # Use in-memory storage for testing
        user_quizzes = []
        for quiz_data in test_storage.get('quizzes', {}).values():
            if quiz_data.get('user_id') == user_id:
                user_quizzes.append(Quiz(**quiz_data))
        return user_quizzes
    
    def _get():
        docs = db.collection('quizzes').where('user_id', '==', user_id).stream()
        return [Quiz(**doc.to_dict()) for doc in docs]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def get_quizzes_by_pdf_id(pdf_id: str) -> List[Quiz]:
    """Get all quizzes for a PDF"""
    def _get():
        docs = db.collection('quizzes').where('pdf_id', '==', pdf_id).stream()
        return [Quiz(**doc.to_dict()) for doc in docs]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

# Quiz Attempt Operations
async def save_quiz_attempt(attempt: QuizAttempt) -> None:
    """Save quiz attempt to Firestore (create if not exists)"""
    def _save():
        doc_ref = db.collection('quiz_attempts').document(attempt.id)
        # Use set with merge=True to create if not exists, update if exists
        doc_ref.set(attempt.dict(), merge=True)
        print(f"✅ Saved/Updated quiz attempt: {attempt.id}")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _save)

async def get_quiz_attempt(attempt_id: str) -> QuizAttempt:
    """Get quiz attempt from Firestore"""
    def _get():
        doc_ref = db.collection('quiz_attempts').document(attempt_id)
        doc = doc_ref.get()
        if doc.exists:
            return QuizAttempt(**doc.to_dict())
        raise Exception("Quiz attempt not found")
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def get_user_quiz_attempts(user_id: str, quiz_id: str) -> List[QuizAttempt]:
    """Get all attempts for a specific quiz by a user"""
    def _get():
        docs = (db.collection('quiz_attempts')
                .where('user_id', '==', user_id)
                .where('quiz_id', '==', quiz_id)
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .stream())
        return [QuizAttempt(**doc.to_dict()) for doc in docs]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def get_recent_quiz_attempts(user_id: str, limit: int = 10) -> List[QuizAttempt]:
    """Get recent quiz attempts for a user"""
    def _get():
        docs = (db.collection('quiz_attempts')
                .where('user_id', '==', user_id)
                .order_by('completed_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream())
        return [QuizAttempt(**doc.to_dict()) for doc in docs]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def get_all_quiz_attempts_by_user(user_id: str) -> List[QuizAttempt]:
    """Get all quiz attempts for a user"""
    def _get():
        docs = (db.collection('quiz_attempts')
                .where('user_id', '==', user_id)
                .order_by('completed_at', direction=firestore.Query.ASCENDING)
                .stream())
        return [QuizAttempt(**doc.to_dict()) for doc in docs]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

# User Operations
async def save_user(user: User) -> None:
    """Save user to Firestore (create if not exists)"""
    def _save():
        doc_ref = db.collection('users').document(user.uid)
        # Use set with merge=True to create if not exists, update if exists
        doc_ref.set(user.dict(), merge=True)
        print(f"✅ Saved/Updated user: {user.uid}")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _save)

async def get_user(user_id: str) -> Optional[User]:
    """Get user from Firestore"""
    def _get():
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return User(**doc.to_dict())
        return None
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

# Analytics and Recommendations
async def save_user_recommendation(user_id: str, recommendations: List[str]) -> None:
    """Save user recommendations"""
    def _save():
        doc_ref = db.collection('recommendations').document(user_id)
        doc_ref.set({
            'user_id': user_id,
            'recommendations': recommendations,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _save)

async def get_user_recommendations(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user recommendations"""
    def _get():
        doc_ref = db.collection('recommendations').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

# Study Notes Operations
async def save_user_notes(notes) -> None:
    """Save study notes to Firebase Firestore"""
    try:
        # Always try to save to Firebase first
        def _save():
            doc_ref = db.collection('study_notes').document(notes.id)
            notes_data = notes.dict()
            
            # Convert datetime objects to strings for Firestore
            if 'generated_at' in notes_data and hasattr(notes_data['generated_at'], 'isoformat'):
                notes_data['generated_at'] = notes_data['generated_at'].isoformat()
            if 'created_at' in notes_data and hasattr(notes_data['created_at'], 'isoformat'):
                notes_data['created_at'] = notes_data['created_at'].isoformat()
            if 'updated_at' in notes_data and hasattr(notes_data['updated_at'], 'isoformat'):
                notes_data['updated_at'] = notes_data['updated_at'].isoformat()
            
            doc_ref.set(notes_data)
            print(f"✅ Saved study notes {notes.id} to Firebase Firestore")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, _save)
        
    except Exception as e:
        print(f"❌ Error saving to Firebase: {e}")
        # Fallback to test storage
        test_storage['notes'] = test_storage.get('notes', {})
        test_storage['notes'][notes.id] = notes.dict()
        print(f"📝 Saved study notes {notes.id} to test storage (fallback)")
        raise e

async def get_user_notes(notes_id: str):
    """Get study notes by ID from Firebase Firestore"""
    try:
        def _get():
            doc_ref = db.collection('study_notes').document(notes_id)
            doc = doc_ref.get()
            if doc.exists:
                from models.notes import StudyNotes
                notes_data = doc.to_dict()
                
                # Convert string dates back to datetime objects
                if 'generated_at' in notes_data and isinstance(notes_data['generated_at'], str):
                    from datetime import datetime
                    notes_data['generated_at'] = datetime.fromisoformat(notes_data['generated_at'])
                if 'created_at' in notes_data and isinstance(notes_data['created_at'], str):
                    from datetime import datetime
                    notes_data['created_at'] = datetime.fromisoformat(notes_data['created_at'])
                if 'updated_at' in notes_data and isinstance(notes_data['updated_at'], str):
                    from datetime import datetime
                    notes_data['updated_at'] = datetime.fromisoformat(notes_data['updated_at'])
                
                return StudyNotes(**notes_data)
            return None
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _get)
        if result:
            print(f"✅ Retrieved study notes {notes_id} from Firebase")
        return result
        
    except Exception as e:
        print(f"❌ Error retrieving from Firebase: {e}")
        # Fallback to test storage
        notes_data = test_storage.get('notes', {}).get(notes_id)
        if notes_data:
            from models.notes import StudyNotes
            return StudyNotes(**notes_data)
        return None

async def get_notes_by_pdf_id(pdf_id: str, user_id: str) -> List:
    """Get all notes for a specific PDF from Firebase Firestore"""
    try:
        def _get():
            docs = (db.collection('study_notes')
                    .where('pdf_id', '==', pdf_id)
                    .where('user_id', '==', user_id)
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .stream())
            
            from models.notes import StudyNotes
            notes_list = []
            
            for doc in docs:
                notes_data = doc.to_dict()
                
                # Convert string dates back to datetime objects
                if 'generated_at' in notes_data and isinstance(notes_data['generated_at'], str):
                    from datetime import datetime
                    notes_data['generated_at'] = datetime.fromisoformat(notes_data['generated_at'])
                if 'created_at' in notes_data and isinstance(notes_data['created_at'], str):
                    from datetime import datetime
                    notes_data['created_at'] = datetime.fromisoformat(notes_data['created_at'])
                if 'updated_at' in notes_data and isinstance(notes_data['updated_at'], str):
                    from datetime import datetime
                    notes_data['updated_at'] = datetime.fromisoformat(notes_data['updated_at'])
                
                notes_list.append(StudyNotes(**notes_data))
            
            return notes_list
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _get)
        print(f"✅ Retrieved {len(result)} notes for PDF {pdf_id} from Firebase")
        return result
        
    except Exception as e:
        print(f"❌ Error retrieving notes by PDF ID from Firebase: {e}")
        # Fallback to test storage
        notes_list = []
        for notes_data in test_storage.get('notes', {}).values():
            if notes_data.get('pdf_id') == pdf_id and notes_data.get('user_id') == user_id:
                from models.notes import StudyNotes
                notes_list.append(StudyNotes(**notes_data))
        return notes_list

async def get_all_user_notes_from_db(user_id: str) -> List:
    """Get all study notes for a user from Firebase Firestore"""
    try:
        def _get():
            docs = (db.collection('study_notes')
                    .where('user_id', '==', user_id)
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .stream())
            
            from models.notes import StudyNotes
            notes_list = []
            
            for doc in docs:
                notes_data = doc.to_dict()
                
                # Convert string dates back to datetime objects
                if 'generated_at' in notes_data and isinstance(notes_data['generated_at'], str):
                    from datetime import datetime
                    notes_data['generated_at'] = datetime.fromisoformat(notes_data['generated_at'])
                if 'created_at' in notes_data and isinstance(notes_data['created_at'], str):
                    from datetime import datetime
                    notes_data['created_at'] = datetime.fromisoformat(notes_data['created_at'])
                if 'updated_at' in notes_data and isinstance(notes_data['updated_at'], str):
                    from datetime import datetime
                    notes_data['updated_at'] = datetime.fromisoformat(notes_data['updated_at'])
                
                notes_list.append(StudyNotes(**notes_data))
            
            return notes_list
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _get)
        print(f"✅ Retrieved {len(result)} total notes for user {user_id} from Firebase")
        return result
        
    except Exception as e:
        print(f"❌ Error retrieving all user notes from Firebase: {e}")
        # Fallback to test storage
        notes_list = []
        for notes_data in test_storage.get('notes', {}).values():
            if notes_data.get('user_id') == user_id:
                from models.notes import StudyNotes
                notes_list.append(StudyNotes(**notes_data))
        # Sort by created_at
        notes_list.sort(key=lambda x: x.created_at, reverse=True)
        return notes_list
async  def update_user_notes(notes) -> None:
    """Update existing study notes in Firebase Firestore"""
    try:
        def _update():
            doc_ref = db.collection('study_notes').document(notes.id)
            notes_data = notes.dict()
            
            # Convert datetime objects to strings for Firestore
            if 'generated_at' in notes_data and hasattr(notes_data['generated_at'], 'isoformat'):
                notes_data['generated_at'] = notes_data['generated_at'].isoformat()
            if 'created_at' in notes_data and hasattr(notes_data['created_at'], 'isoformat'):
                notes_data['created_at'] = notes_data['created_at'].isoformat()
            if 'updated_at' in notes_data and hasattr(notes_data['updated_at'], 'isoformat'):
                notes_data['updated_at'] = notes_data['updated_at'].isoformat()
            
            # Update the updated_at timestamp
            from datetime import datetime
            notes_data['updated_at'] = datetime.now().isoformat()
            
            doc_ref.update(notes_data)
            print(f"✅ Updated study notes {notes.id} in Firebase Firestore")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, _update)
        
    except Exception as e:
        print(f"❌ Error updating notes in Firebase: {e}")
        # Fallback to test storage
        test_storage['notes'] = test_storage.get('notes', {})
        test_storage['notes'][notes.id] = notes.dict()
        print(f"📝 Updated study notes {notes.id} in test storage (fallback)")
        raise e

async def delete_user_notes(notes_id: str) -> None:
    """Delete study notes from Firebase Firestore"""
    try:
        def _delete():
            doc_ref = db.collection('study_notes').document(notes_id)
            doc_ref.delete()
            print(f"✅ Deleted study notes {notes_id} from Firebase Firestore")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, _delete)
        
    except Exception as e:
        print(f"❌ Error deleting notes from Firebase: {e}")
        # Fallback to test storage
        if notes_id in test_storage.get('notes', {}):
            del test_storage['notes'][notes_id]
            print(f"📝 Deleted study notes {notes_id} from test storage (fallback)")
        raise e

async def get_notes_analytics(user_id: str) -> Dict[str, Any]:
    """Get analytics data for user's study notes from Firebase"""
    try:
        def _get_analytics():
            docs = (db.collection('study_notes')
                    .where('user_id', '==', user_id)
                    .stream())
            
            total_notes = 0
            total_score = 0
            topics_frequency = {}
            study_priorities = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
            
            for doc in docs:
                notes_data = doc.to_dict()
                total_notes += 1
                
                # Aggregate performance data
                performance = notes_data.get('performance_summary', {})
                score = performance.get('score', 0)
                total_score += score
                
                # Count topic frequency
                topics = notes_data.get('topics_covered', [])
                for topic in topics:
                    topics_frequency[topic] = topics_frequency.get(topic, 0) + 1
                
                # Count study priorities
                priority = notes_data.get('study_priority', 'medium')
                if priority in study_priorities:
                    study_priorities[priority] += 1
            
            # Calculate averages and insights
            avg_score = total_score / total_notes if total_notes > 0 else 0
            most_common_topics = sorted(topics_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_notes": total_notes,
                "average_score": round(avg_score, 1),
                "most_common_weak_topics": [{"topic": topic, "frequency": freq} for topic, freq in most_common_topics],
                "study_priority_distribution": study_priorities,
                "total_topics_covered": len(topics_frequency)
            }
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _get_analytics)
        print(f"✅ Retrieved analytics for user {user_id} from Firebase")
        return result
        
    except Exception as e:
        print(f"❌ Error getting analytics from Firebase: {e}")
        return {
            "total_notes": 0,
            "average_score": 0,
            "most_common_weak_topics": [],
            "study_priority_distribution": {"low": 0, "medium": 0, "high": 0, "urgent": 0},
            "total_topics_covered": 0,
            "error": str(e)
        }