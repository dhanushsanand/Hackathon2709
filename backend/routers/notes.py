from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import uuid

from middleware.auth import get_current_user_id
from models.notes import StudyNotes, NotesGenerationRequest, NotesResponse
from models.quiz import QuizAttempt, Question
from models.pdf import PDFDocument
from services.notes_generator import NotesGeneratorService
from utils.database import (
    get_quiz_attempt, get_quiz, get_pdf_document,
    save_user_notes, get_user_notes, get_notes_by_pdf_id,
    get_all_user_notes_from_db
)

router = APIRouter()
notes_service = NotesGeneratorService()

@router.post("/generate/{quiz_attempt_id}")
async def generate_study_notes(
    quiz_attempt_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Generate personalized study notes based on quiz performance"""
    
    try:
        # Get quiz attempt
        quiz_attempt = await get_quiz_attempt(quiz_attempt_id)
        
        # Verify ownership
        if quiz_attempt.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get quiz details
        quiz = await get_quiz(quiz_attempt.quiz_id)
        
        # Get PDF document
        pdf_document = await get_pdf_document(quiz.pdf_id)
        
        # Verify PDF ownership
        if pdf_document.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate comprehensive notes
        notes_data = await notes_service.create_comprehensive_notes(
            quiz_attempt=quiz_attempt,
            questions=quiz.questions,
            pdf_document=pdf_document
        )
        
        # Create StudyNotes object
        study_notes = StudyNotes(
            id=notes_data["id"],
            pdf_id=pdf_document.id,
            quiz_attempt_id=quiz_attempt_id,
            user_id=user_id,
            pdf_title=notes_data["pdf_title"],
            generated_at=notes_data["generated_at"],
            performance_summary=notes_data["performance_summary"],
            study_notes=notes_data["study_notes"],
            topics_covered=notes_data["topics_covered"],
            relevant_content_sources=notes_data["relevant_content_sources"],
            study_priority=notes_data["study_priority"],
            estimated_study_time=notes_data["estimated_study_time"],
            next_review_date=notes_data.get("next_review_date"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save notes to database
        await save_user_notes(study_notes)
        
        # Generate recommendations
        recommendations = generate_study_recommendations(notes_data)
        
        # Prepare generation stats
        generation_stats = {
            "topics_analyzed": len(notes_data["topics_covered"]),
            "content_sources_used": notes_data["relevant_content_sources"],
            "performance_score": notes_data["performance_summary"]["score"],
            "weak_areas_identified": len(notes_data["performance_summary"].get("weak_topics", [])),
            "generation_time": "completed",
            "ai_provider": "gemini"
        }
        
        return NotesResponse(
            notes=study_notes,
            generation_stats=generation_stats,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate notes: {str(e)}")

@router.get("/{notes_id}")
async def get_study_notes(
    notes_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get specific study notes by ID"""
    
    try:
        notes = await get_user_notes(notes_id)
        
        if not notes:
            raise HTTPException(status_code=404, detail="Notes not found")
        
        # Verify ownership
        if notes.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return notes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf/{pdf_id}")
async def get_notes_for_pdf(
    pdf_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get all study notes for a specific PDF"""
    
    try:
        # Verify PDF ownership
        pdf_document = await get_pdf_document(pdf_id)
        if pdf_document.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all notes for this PDF
        notes_list = await get_notes_by_pdf_id(pdf_id, user_id)
        
        return {
            "pdf_id": pdf_id,
            "pdf_title": pdf_document.original_filename,
            "notes_count": len(notes_list),
            "notes": notes_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/all")
async def get_all_user_notes(user_id: str = Depends(get_current_user_id)):
    """Get all study notes for the current user"""
    
    try:
        notes_list = await get_all_user_notes_from_db(user_id)
        
        # Group by PDF
        notes_by_pdf = {}
        for notes in notes_list:
            pdf_id = notes.pdf_id
            if pdf_id not in notes_by_pdf:
                notes_by_pdf[pdf_id] = {
                    "pdf_id": pdf_id,
                    "pdf_title": notes.pdf_title,
                    "notes": []
                }
            notes_by_pdf[pdf_id]["notes"].append(notes)
        
        # Sort by creation date
        for pdf_data in notes_by_pdf.values():
            pdf_data["notes"].sort(key=lambda x: x.created_at, reverse=True)
        
        return {
            "total_notes": len(notes_list),
            "pdfs_with_notes": len(notes_by_pdf),
            "notes_by_pdf": list(notes_by_pdf.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{notes_id}/regenerate")
async def regenerate_study_notes(
    notes_id: str,
    request: NotesGenerationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Regenerate study notes with updated parameters"""
    
    try:
        # Get existing notes
        existing_notes = await get_user_notes(notes_id)
        
        if not existing_notes or existing_notes.user_id != user_id:
            raise HTTPException(status_code=404, detail="Notes not found")
        
        # Use the same quiz attempt ID to regenerate
        return await generate_study_notes(
            quiz_attempt_id=existing_notes.quiz_attempt_id,
            request=request,
            user_id=user_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate notes: {str(e)}")

@router.get("/analytics/performance")
async def get_performance_analytics(user_id: str = Depends(get_current_user_id)):
    """Get performance analytics across all study notes"""
    
    try:
        notes_list = await get_all_user_notes_from_db(user_id)
        
        if not notes_list:
            return {
                "total_notes": 0,
                "average_score": 0,
                "improvement_trend": "no_data",
                "common_weak_areas": [],
                "study_time_total": "0 hours"
            }
        
        # Analyze performance trends
        scores = [notes.performance_summary.get("score", 0) for notes in notes_list]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Find common weak areas
        all_weak_topics = []
        for notes in notes_list:
            weak_topics = notes.performance_summary.get("weak_topics", [])
            all_weak_topics.extend(weak_topics)
        
        # Count topic frequency
        topic_frequency = {}
        for topic in all_weak_topics:
            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        common_weak_areas = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate improvement trend
        if len(scores) >= 2:
            recent_scores = scores[-3:]  # Last 3 scores
            older_scores = scores[:-3] if len(scores) > 3 else scores[:1]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "total_notes": len(notes_list),
            "average_score": round(average_score, 1),
            "improvement_trend": trend,
            "common_weak_areas": [{"topic": topic, "frequency": freq} for topic, freq in common_weak_areas],
            "study_recommendations": generate_overall_recommendations(notes_list),
            "last_study_session": notes_list[-1].created_at if notes_list else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_study_recommendations(notes_data: Dict[str, Any]) -> List[str]:
    """Generate study recommendations based on notes"""
    
    recommendations = []
    
    performance_level = notes_data["performance_summary"].get("level", "satisfactory")
    score = notes_data["performance_summary"].get("score", 0)
    weak_topics = notes_data["performance_summary"].get("weak_topics", [])
    
    # Performance-based recommendations
    if performance_level == "requires_significant_study":
        recommendations.extend([
            "Schedule daily 30-45 minute study sessions",
            "Focus on fundamental concepts before advanced topics",
            "Consider seeking additional help or tutoring"
        ])
    elif performance_level == "needs_improvement":
        recommendations.extend([
            "Review weak areas identified in the analysis",
            "Practice with additional questions on difficult topics",
            "Create flashcards for key concepts"
        ])
    elif performance_level == "satisfactory":
        recommendations.extend([
            "Strengthen understanding in identified weak areas",
            "Practice application of concepts with examples"
        ])
    else:
        recommendations.extend([
            "Maintain current study habits",
            "Challenge yourself with advanced practice questions"
        ])
    
    # Topic-specific recommendations
    if weak_topics:
        recommendations.append(f"Pay special attention to: {', '.join(weak_topics[:3])}")
    
    # Study method recommendations
    recommendations.extend([
        "Use active recall techniques while studying",
        "Test yourself regularly on the material",
        "Connect new concepts to previously learned material"
    ])
    
    return recommendations

def generate_overall_recommendations(notes_list: List[StudyNotes]) -> List[str]:
    """Generate overall study recommendations based on all notes"""
    
    if not notes_list:
        return ["Start taking quizzes to get personalized study recommendations"]
    
    recommendations = []
    
    # Analyze overall performance
    avg_score = sum(notes.performance_summary.get("score", 0) for notes in notes_list) / len(notes_list)
    
    if avg_score < 70:
        recommendations.append("Focus on building stronger foundational knowledge")
    elif avg_score < 85:
        recommendations.append("Work on consistency across different topics")
    else:
        recommendations.append("Excellent progress! Continue with advanced practice")
    
    # Find most common weak areas
    all_weak_topics = []
    for notes in notes_list:
        all_weak_topics.extend(notes.performance_summary.get("weak_topics", []))
    
    if all_weak_topics:
        topic_counts = {}
        for topic in all_weak_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        most_common = max(topic_counts.items(), key=lambda x: x[1])
        recommendations.append(f"Consider additional study on '{most_common[0]}' - appears frequently in weak areas")
    
    return recommendations