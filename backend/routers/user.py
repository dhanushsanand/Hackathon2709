from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.user import User
from middleware.auth import get_current_user_id
from services.gemini import GeminiService
from utils.database import (
    get_user_quiz_attempts, get_pdf_document, save_user, get_user,
    get_recent_quiz_attempts, get_pdfs_by_user_id, get_quiz, 
    get_all_quiz_attempts_by_user
)
from utils.cloudinary import CloudinaryService

router = APIRouter()
gemini_service = GeminiService()
cloudinary_service = CloudinaryService()

@router.get("/dashboard")
async def get_user_dashboard(user_id: str = Depends(get_current_user_id)):
    """Get user dashboard data"""
    try:
        # Get recent quiz attempts
        recent_attempts = await get_recent_quiz_attempts(user_id, limit=10)
        
        # Calculate statistics
        total_quizzes = len(recent_attempts)
        if total_quizzes > 0:
            avg_score = sum(attempt.score for attempt in recent_attempts) / total_quizzes
            recent_performance = [attempt.score for attempt in recent_attempts[-5:]]
        else:
            avg_score = 0
            recent_performance = []
        
        # Get PDFs count
        user_pdfs = await get_pdfs_by_user_id(user_id)
        
        dashboard_data = {
            "user_id": user_id,
            "total_pdfs": len(user_pdfs),
            "total_quizzes_taken": total_quizzes,
            "average_score": round(avg_score * 100, 1) if avg_score else 0,
            "recent_performance": [round(score * 100, 1) for score in recent_performance],
            "recent_attempts": [
                {
                    "id": attempt.id,
                    "quiz_id": attempt.quiz_id,
                    "score": round(attempt.score * 100, 1),
                    "completed_at": attempt.completed_at.isoformat(),
                    "time_taken": attempt.time_taken
                }
                for attempt in recent_attempts[:5]
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(user_id: str = Depends(get_current_user_id)):
    """Get personalized learning recommendations"""
    try:
        # Get recent quiz performance
        recent_attempts = await get_recent_quiz_attempts(user_id, limit=5)
        
        if not recent_attempts:
            return {"recommendations": ["Start by uploading a PDF and taking your first quiz!"]}
        
        # Analyze performance patterns
        weak_areas = []
        strong_areas = []
        
        for attempt in recent_attempts:
            if attempt.score < 0.7:
                # Get quiz details to understand weak areas
                quiz = await get_quiz(attempt.quiz_id)
                pdf_doc = await get_pdf_document(quiz.pdf_id)
                weak_areas.append(pdf_doc.original_filename)
            elif attempt.score > 0.9:
                quiz = await get_quiz(attempt.quiz_id)
                pdf_doc = await get_pdf_document(quiz.pdf_id)
                strong_areas.append(pdf_doc.original_filename)
        
        # Generate AI recommendations
        quiz_results = {
            "weak_areas": list(set(weak_areas)),
            "strong_areas": list(set(strong_areas)),
            "average_score": sum(a.score for a in recent_attempts) / len(recent_attempts),
            "trend": "improving" if len(recent_attempts) > 2 and 
                    recent_attempts[-1].score > recent_attempts[0].score else "stable"
        }
        
        # Get sample content for context
        sample_content = ""
        if recent_attempts:
            latest_quiz = await get_quiz(recent_attempts[0].quiz_id)
            pdf_doc = await get_pdf_document(latest_quiz.pdf_id)
            if pdf_doc.content_chunks:
                sample_content = " ".join(pdf_doc.content_chunks[:2])
        
        recommendations = await gemini_service.generate_recommendations(
            quiz_results, sample_content
        )
        
        return {
            "recommendations": recommendations,
            "performance_summary": {
                "weak_areas": weak_areas,
                "strong_areas": strong_areas,
                "recent_trend": quiz_results["trend"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_user_analytics(user_id: str = Depends(get_current_user_id)):
    """Get detailed user analytics"""
    try:
        # Get all quiz attempts
        all_attempts = await get_all_quiz_attempts_by_user(user_id)
        
        if not all_attempts:
            return {"message": "No quiz data available"}
        
        # Calculate various analytics
        analytics = {
            "total_attempts": len(all_attempts),
            "average_score": sum(a.score for a in all_attempts) / len(all_attempts),
            "best_score": max(a.score for a in all_attempts),
            "worst_score": min(a.score for a in all_attempts),
            "total_time_spent": sum(a.time_taken or 0 for a in all_attempts),
            "score_trend": [a.score for a in all_attempts[-10:]],  # Last 10 attempts
            "weekly_activity": calculate_weekly_activity(all_attempts),
            "difficulty_performance": calculate_difficulty_performance(all_attempts),
            "subject_performance": await calculate_subject_performance(all_attempts)
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def get_user_files(
    user_id: str = Depends(get_current_user_id),
    max_results: int = Query(100, ge=1, le=500)
):
    """Get all files uploaded by the current user from Cloudinary"""
    try:
        # Get files from Cloudinary using both methods
        files_by_tag = await cloudinary_service.get_files_by_user_id(user_id, max_results)
        files_by_folder = await cloudinary_service.get_files_by_user_id_in_folder(user_id, max_results)
        
        # Combine and deduplicate files
        all_files = files_by_tag + files_by_folder
        unique_files = {}
        
        for file_info in all_files:
            public_id = file_info['public_id']
            if public_id not in unique_files:
                unique_files[public_id] = file_info
        
        # Format response
        formatted_files = []
        for file_info in unique_files.values():
            formatted_file = {
                "public_id": file_info['public_id'],
                "original_filename": file_info.get('original_filename', 'Unknown'),
                "secure_url": file_info['secure_url'],
                "file_size": file_info.get('bytes', 0),
                "format": file_info.get('format', 'pdf'),
                "upload_date": file_info.get('created_at', ''),
                "context": file_info.get('context', {}),
                "tags": file_info.get('tags', [])
            }
            formatted_files.append(formatted_file)
        
        # Sort by upload date (most recent first)
        formatted_files.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        
        return {
            "user_id": user_id,
            "total_files": len(formatted_files),
            "files": formatted_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user files: {str(e)}")

@router.get("/files/{public_id}/info")
async def get_file_info(
    public_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed information about a specific file"""
    try:
        # Verify the file belongs to the user by checking if it's in their files
        user_files = await cloudinary_service.get_files_by_user_id(user_id)
        file_belongs_to_user = any(f['public_id'] == public_id for f in user_files)
        
        if not file_belongs_to_user:
            # Also check folder-based files
            folder_files = await cloudinary_service.get_files_by_user_id_in_folder(user_id)
            file_belongs_to_user = any(f['public_id'] == public_id for f in folder_files)
        
        if not file_belongs_to_user:
            raise HTTPException(status_code=403, detail="Access denied: File does not belong to user")
        
        # Get detailed file information
        file_info = await cloudinary_service.get_file_info(public_id)
        
        return {
            "file_info": file_info,
            "download_url": await cloudinary_service.get_file_url(public_id, expires_in=3600)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

def calculate_weekly_activity(attempts: List[Any]) -> Dict[str, int]:
    """Calculate weekly activity pattern"""
    weekly_counts = {}
    for attempt in attempts:
        week_key = attempt.completed_at.strftime("%Y-W%U")
        weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1
    return weekly_counts

def calculate_difficulty_performance(attempts: List[Any]) -> Dict[str, float]:
    """Calculate performance by difficulty level"""
    # This would need to be implemented based on your quiz difficulty tracking
    return {"easy": 0.85, "medium": 0.75, "hard": 0.65}

async def calculate_subject_performance(attempts: List[Any]) -> Dict[str, float]:
    """Calculate performance by subject/PDF"""
    subject_scores = {}
    for attempt in attempts:
        quiz = await get_quiz(attempt.quiz_id)
        pdf = await get_pdf_document(quiz.pdf_id)
        subject = pdf.original_filename
        
        if subject not in subject_scores:
            subject_scores[subject] = []
        subject_scores[subject].append(attempt.score)
    
    # Calculate averages
    return {
        subject: sum(scores) / len(scores)
        for subject, scores in subject_scores.items()
    }

@router.post("", response_model=User)
async def add_user(payload: User, _user_id: str = Depends(get_current_user_id)):
    """
    Manually add a user (e.g., admin tool). You can gate this by role if needed.
    """
    try:
        user = await save_user(
            uid=payload.uid,
            email=payload.email,
            display_name=payload.display_name,
            photo_url=payload.photo_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return user.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[User])
async def get_all_users(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _user_id: str = Depends(get_current_user_id),
):
    """Return a paginated list of users. Gate by role if necessary."""
    try:
        users = await get_user(limit=limit, offset=offset)
        return [User.model_validate(u) for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))