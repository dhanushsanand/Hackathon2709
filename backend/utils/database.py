# utils/database.py
from firebase_admin import firestore
from typing import List, Optional, Dict, Any
from models.pdf import PDFDocument, ProcessingStatus
from models.quiz import Quiz, QuizAttempt
from models.user import User
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Initialize Firestore
db = firestore.client()
executor = ThreadPoolExecutor(max_workers=4)

# PDF Document Operations
async def save_pdf_document(pdf_doc: PDFDocument) -> None:
    """Save PDF document to Firestore"""
    def _save():
        doc_ref = db.collection('pdfs').document(pdf_doc.id)
        doc_ref.set(pdf_doc.dict())
    
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
    def _get():
        docs = db.collection('pdfs').where('user_id', '==', user_id).stream()
        return [PDFDocument(**doc.to_dict()) for doc in docs]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get)

async def delete_pdf_document(pdf_id: str) -> None:
    """Delete PDF document"""
    def _delete():
        # Delete related quizzes first
        quizzes = db.collection('quizzes').where('pdf_id', '==', pdf_id).stream()
        for quiz in quizzes:
            quiz.reference.delete()
        
        # Delete the PDF document
        db.collection('pdfs').document(pdf_id).delete()
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _delete)

# Quiz Operations
async def save_quiz(quiz: Quiz) -> None:
    """Save quiz to Firestore"""
    def _save():
        doc_ref = db.collection('quizzes').document(quiz.id)
        quiz_data = quiz.dict()
        # Convert questions to dict format
        quiz_data['questions'] = [q.dict() for q in quiz.questions]
        doc_ref.set(quiz_data)
    
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
    """Save quiz attempt to Firestore"""
    def _save():
        doc_ref = db.collection('quiz_attempts').document(attempt.id)
        doc_ref.set(attempt.dict())
    
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
    """Save user to Firestore"""
    def _save():
        doc_ref = db.collection('users').document(user.uid)
        doc_ref.set(user.dict())
    
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
