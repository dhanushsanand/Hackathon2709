import hashlib
import uuid
from typing import List, Dict, Any
from datetime import datetime
import re

def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    return f"{prefix}_{uuid.uuid4().hex}" if prefix else uuid.uuid4().hex

def hash_content(content: str) -> str:
    """Generate MD5 hash of content"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename[:255]  # Limit length

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    return max(1, word_count // words_per_minute)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def format_score(score: float) -> str:
    """Format score as percentage string"""
    return f"{score * 100:.1f}%"

def time_ago(dt: datetime) -> str:
    """Get human-readable time difference"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words]
    
    # Count frequencies
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]

class ContentAnalyzer:
    """Utility class for content analysis"""
    
    @staticmethod
    def get_difficulty_level(text: str) -> int:
        """Estimate content difficulty level (1-5)"""
        # Simple heuristic based on sentence length and word complexity
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Count complex words (>6 characters)
        words = text.split()
        complex_words = sum(1 for word in words if len(word) > 6)
        complexity_ratio = complex_words / len(words) if words else 0
        
        # Calculate difficulty score
        if avg_sentence_length < 10 and complexity_ratio < 0.1:
            return 1  # Easy
        elif avg_sentence_length < 15 and complexity_ratio < 0.2:
            return 2  # Beginner
        elif avg_sentence_length < 20 and complexity_ratio < 0.3:
            return 3  # Intermediate
        elif avg_sentence_length < 25 and complexity_ratio < 0.4:
            return 4  # Advanced
        else:
            return 5  # Expert
    
    @staticmethod
    def extract_topics(text: str) -> List[str]:
        """Extract main topics from text"""
        # This is a simplified implementation
        # In production, you might use NLP libraries like spaCy or NLTK
        keywords = extract_keywords(text, max_keywords=15)
        
        # Group related keywords (very basic clustering)
        topics = []
        used_words = set()
        
        for keyword in keywords:
            if keyword not in used_words:
                topic = [keyword]
                used_words.add(keyword)
                
                # Look for related words (simple substring matching)
                for other_keyword in keywords:
                    if (other_keyword not in used_words and 
                        (keyword in other_keyword or other_keyword in keyword)):
                        topic.append(other_keyword)
                        used_words.add(other_keyword)
                
                topics.append(' '.join(topic))
        
        return topics[:5]  # Return top 5 topics

# Performance monitoring utilities
class PerformanceTracker:
    """Track and analyze user performance"""
    
    @staticmethod
    def calculate_learning_velocity(attempts: List[Dict[str, Any]]) -> float:
        """Calculate how quickly user is improving"""
        if len(attempts) < 2:
            return 0.0
        
        scores = [attempt.get('score', 0) for attempt in attempts]
        
        # Simple linear trend calculation
        n = len(scores)
        sum_x = sum(range(n))
        sum_y = sum(scores)
        sum_xy = sum(i * score for i, score in enumerate(scores))
        sum_x2 = sum(i * i for i in range(n))
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    @staticmethod
    def identify_knowledge_gaps(quiz_results: List[Dict[str, Any]]) -> List[str]:
        """Identify areas where user consistently performs poorly"""
        topic_scores = {}
        
        for result in quiz_results:
            topics = result.get('topics', [])
            score = result.get('score', 0)
            
            for topic in topics:
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)
        
        # Find topics with consistently low scores
        gaps = []
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.6 and len(scores) >= 2:  # Consistent poor performance
                gaps.append(topic)
        
        return gaps
    
    @staticmethod
    def recommend_study_plan(user_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized study plan"""
        weak_areas = user_performance.get('weak_areas', [])
        strong_areas = user_performance.get('strong_areas', [])
        learning_velocity = user_performance.get('learning_velocity', 0)
        
        plan = {
            'focus_areas': weak_areas[:3],  # Top 3 areas to focus on
            'review_areas': strong_areas[:2],  # Areas to review occasionally
            'recommended_frequency': 'daily' if learning_velocity > 0 else 'every 2-3 days',
            'session_duration': 30 if len(weak_areas) > 2 else 20,  # minutes
            'difficulty_adjustment': 'easier' if learning_velocity < 0 else 'current'
        }
        
        return plan