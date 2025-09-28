from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime

from middleware.auth import get_current_user_id
from models.quiz import Quiz, QuizAttempt, Question
from models.pdf import PDFDocument
from services.gemini import GeminiService
from services.embeddings import EmbeddingService
from utils.database import (
    get_pdf_document, save_quiz, get_quiz, save_quiz_attempt,
    get_user_quiz_attempts, get_quizzes_by_user_id
)

router = APIRouter()
gemini_service = GeminiService()
embedding_service = EmbeddingService()

class GenerateQuizRequest(BaseModel):
    num_questions: int = 5
    difficulty_range: List[int] = [1, 3]  # min, max difficulty

class QuizSubmission(BaseModel):
    answers: Dict[str, str]  # question_id -> answer

class QuizResult(BaseModel):
    quiz_attempt_id: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken: int
    question_results: List[Dict[str, Any]]

@router.post("/generate/{pdf_id}")
async def generate_quiz(
    pdf_id: str,
    request: GenerateQuizRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate a quiz from PDF content"""
    try:
        # Get PDF document
        pdf_doc = await get_pdf_document(pdf_id)
        
        # Verify ownership
        if pdf_doc.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if PDF is processed
        if pdf_doc.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail="PDF is still being processed or failed to process"
            )
        
        print(f"🎯 Generating quiz for PDF: {pdf_doc.original_filename}")
        print(f"📊 Content chunks available: {len(pdf_doc.content_chunks)}")
        
        # Validate content chunks
        if not pdf_doc.content_chunks or len(pdf_doc.content_chunks) == 0:
            raise HTTPException(
                status_code=400,
                detail="PDF has no content chunks. Please re-upload and process the PDF."
            )
        
        # Generate questions using Gemini with error handling
        try:
            questions = await gemini_service.generate_quiz_questions(
                pdf_doc.content_chunks,
                request.num_questions
            )
            
            if not questions or len(questions) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate any questions. Please try again."
                )
            
            print(f"✅ Generated {len(questions)} questions")
            
        except Exception as e:
            print(f"❌ Quiz generation error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Quiz generation failed: {str(e)}. Please try again in a moment."
            )
        
        # Filter by difficulty if specified
        if request.difficulty_range and len(request.difficulty_range) == 2:
            min_diff, max_diff = request.difficulty_range
            original_count = len(questions)
            questions = [
                q for q in questions 
                if min_diff <= q.difficulty <= max_diff
            ]
            print(f"🔍 Filtered questions by difficulty {min_diff}-{max_diff}: {original_count} → {len(questions)}")
        
        # Ensure we have at least one question
        if len(questions) == 0:
            raise HTTPException(
                status_code=400,
                detail="No questions match the specified difficulty range. Try a broader range."
            )
        
        # Create quiz
        quiz_id = f"quiz_{uuid.uuid4().hex}"
        quiz = Quiz(
            id=quiz_id,
            pdf_id=pdf_id,
            user_id=user_id,
            title=f"Quiz for {pdf_doc.original_filename}",
            description=f"Auto-generated quiz with {len(questions)} questions",
            questions=questions,
            total_questions=len(questions),
            estimated_time=len(questions) * 2,  # 2 minutes per question
            created_at=datetime.now()
        )
        
        # Save quiz with error handling
        try:
            await save_quiz(quiz)
            print(f"✅ Quiz saved successfully: {quiz_id}")
        except Exception as e:
            print(f"❌ Failed to save quiz: {e}")
            raise HTTPException(
                status_code=500,
                detail="Quiz generated but failed to save. Please try again."
            )
        
        return quiz
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"❌ Unexpected error in quiz generation: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}. Please try again."
        )

@router.get("/{quiz_id}")
async def get_quiz_details(
    quiz_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get quiz details"""
    try:
        quiz = await get_quiz(quiz_id)
        
        # Verify access (quiz owner or PDF owner)
        if quiz.user_id != user_id:
            pdf_doc = await get_pdf_document(quiz.pdf_id)
            if pdf_doc.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove correct answers for security
        quiz_copy = quiz.copy()
        for question in quiz_copy.questions:
            question.correct_answer = ""
            question.explanation = ""
        
        return quiz_copy
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Quiz not found")

@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    user_id: str = Depends(get_current_user_id)
):
    """Submit quiz answers and get results"""
    try:
        quiz = await get_quiz(quiz_id)
        
        # Verify access
        if quiz.user_id != user_id:
            pdf_doc = await get_pdf_document(quiz.pdf_id)
            if pdf_doc.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Evaluate answers
        question_results = []
        total_score = 0
        correct_count = 0
        
        for question in quiz.questions:
            user_answer = submission.answers.get(question.id, "")
            
            # Evaluate answer
            evaluation = await gemini_service.evaluate_answer(question, user_answer)
            
            result = {
                "question_id": question.id,
                "question_text": question.question_text,
                "user_answer": user_answer,
                "correct_answer": evaluation["correct_answer"],
                "is_correct": evaluation["is_correct"],
                "score": evaluation["score"],
                "explanation": evaluation["explanation"]
            }
            
            question_results.append(result)
            total_score += evaluation["score"]
            
            if evaluation["is_correct"]:
                correct_count += 1
        
        # Calculate final score
        final_score = total_score / len(quiz.questions) if quiz.questions else 0
        
        # Create quiz attempt
        attempt_id = f"attempt_{uuid.uuid4().hex}"
        quiz_attempt = QuizAttempt(
            id=attempt_id,
            quiz_id=quiz_id,
            user_id=user_id,
            answers=submission.answers,
            score=final_score,
            completed_at=datetime.now(),
            time_taken=0,  # Would be calculated from frontend
            created_at=datetime.now()
        )
        
        # Save attempt
        await save_quiz_attempt(quiz_attempt)
        
        # Return results
        return QuizResult(
            quiz_attempt_id=attempt_id,
            score=final_score,
            total_questions=len(quiz.questions),
            correct_answers=correct_count,
            time_taken=0,
            question_results=question_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit quiz: {str(e)}")

@router.get("/{quiz_id}/attempts")
async def get_quiz_attempts(
    quiz_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get all attempts for a quiz by current user"""
    try:
        attempts = await get_user_quiz_attempts(user_id, quiz_id)
        return attempts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/all")
async def get_user_quizzes(user_id: str = Depends(get_current_user_id)):
    """Get all quizzes created by current user with completion status"""
    try:
        # Get all quizzes for the user
        quizzes = await get_quizzes_by_user_id(user_id)
        
        # Enhance each quiz with status information
        enhanced_quizzes = []
        
        for quiz in quizzes:
            # Get attempts for this quiz by the current user
            attempts = await get_user_quiz_attempts(user_id, quiz.id)
            
            # Determine quiz status
            if attempts and len(attempts) > 0:
                # Quiz has been attempted
                quiz_status = "completed"
                latest_attempt = max(attempts, key=lambda x: x.completed_at)
                best_attempt = max(attempts, key=lambda x: x.score)
                
                quiz_info = {
                    **quiz.dict(),
                    "quiz_status": quiz_status,
                    "attempts_count": len(attempts),
                    "latest_score": round(latest_attempt.score * 100, 1) if latest_attempt.score else 0,
                    "best_score": round(best_attempt.score * 100, 1) if best_attempt.score else 0,
                    "last_attempted": latest_attempt.completed_at.isoformat(),
                    "first_attempted": min(attempts, key=lambda x: x.completed_at).completed_at.isoformat()
                }
            else:
                # Quiz has not been attempted yet
                quiz_status = "pending"
                
                quiz_info = {
                    **quiz.dict(),
                    "quiz_status": quiz_status,
                    "attempts_count": 0,
                    "latest_score": None,
                    "best_score": None,
                    "last_attempted": None,
                    "first_attempted": None
                }
            
            enhanced_quizzes.append(quiz_info)
        
        # Sort by creation date (most recent first)
        enhanced_quizzes.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        # Add summary statistics
        total_quizzes = len(enhanced_quizzes)
        completed_quizzes = len([q for q in enhanced_quizzes if q['quiz_status'] == 'completed'])
        pending_quizzes = len([q for q in enhanced_quizzes if q['quiz_status'] == 'pending'])
        
        # Calculate average score for completed quizzes
        completed_quiz_scores = [q['best_score'] for q in enhanced_quizzes if q['quiz_status'] == 'completed' and q['best_score'] is not None]
        average_score = sum(completed_quiz_scores) / len(completed_quiz_scores) if completed_quiz_scores else 0
        
        return {
            "summary": {
                "total_quizzes": total_quizzes,
                "completed_quizzes": completed_quizzes,
                "pending_quizzes": pending_quizzes,
                "average_score": round(average_score, 1),
                "completion_rate": round((completed_quizzes / total_quizzes) * 100, 1) if total_quizzes > 0 else 0
            },
            "quizzes": enhanced_quizzes
        }
        
    except Exception as e:
        print(f"❌ Error in get_user_quizzes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
