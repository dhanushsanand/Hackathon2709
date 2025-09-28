from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class Question(BaseModel):
    id: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: int = 1  # 1-5 scale
    source_chunk: Optional[str] = None

class Quiz(BaseModel):
    id: str
    pdf_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    questions: List[Question]
    total_questions: int
    estimated_time: int  # in minutes
    created_at: datetime

class QuizAttempt(BaseModel):
    id: str
    quiz_id: str
    user_id: str
    answers: Dict[str, Any]  # question_id -> answer
    score: Optional[float] = None
    completed_at: Optional[datetime] = None
    time_taken: Optional[int] = None  # in seconds
    created_at: datetime