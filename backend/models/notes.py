from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class StudyNotes(BaseModel):
    id: str
    pdf_id: str
    quiz_attempt_id: str
    user_id: str
    pdf_title: str
    generated_at: datetime
    
    # Performance analysis
    performance_summary: Dict[str, Any]
    
    # Generated content
    study_notes: str
    topics_covered: List[str]
    relevant_content_sources: int
    
    # Study recommendations
    study_priority: str  # "low", "medium", "high", "urgent"
    estimated_study_time: str
    next_review_date: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime

class NotesGenerationRequest(BaseModel):
    quiz_attempt_id: str
    include_examples: bool = True
    focus_areas: Optional[List[str]] = None
    study_level: str = "comprehensive"  # "basic", "comprehensive", "advanced"

class NotesResponse(BaseModel):
    notes: StudyNotes
    generation_stats: Dict[str, Any]
    recommendations: List[str]