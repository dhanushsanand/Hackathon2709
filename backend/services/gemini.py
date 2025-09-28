import google.generativeai as genai
from typing import List, Dict, Any
import json
from config import settings
from models.quiz import QuestionType, Question

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate_quiz_questions(self, content_chunks: List[str], num_questions: int = 5) -> List[Question]:
        """Generate quiz questions from content chunks"""
        
        # Combine chunks for context (limit to avoid token limits)
        combined_content = "\n".join(content_chunks[:5])  # Use first 5 chunks
        if len(combined_content) > 10000:
            combined_content = combined_content[:10000] + "..."
        
        prompt = f"""
        Generate {num_questions} quiz questions from the content below.

        IMPORTANT: Respond with ONLY a valid JSON array. No markdown, no explanations, just the JSON.

        Format each question exactly like this:
        [
          {{
            "question_text": "What is the main topic?",
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Brief explanation",
            "difficulty": 2
          }}
        ]

        Question types: "multiple_choice", "true_false", "short_answer"
        Difficulty: 1-5 (integer)
        For true_false: options should be ["True", "False"]
        For short_answer: options should be null

        Content:
        {combined_content}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            print(f"DEBUG: Gemini response type: {type(response)}")
            print(f"DEBUG: Gemini response text: {response.text[:500]}...")
            
            # Clean the response text - sometimes it has markdown formatting
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            print(f"DEBUG: Cleaned response: {response_text[:200]}...")
            
            questions_data = json.loads(response_text)
            
            questions = []
            for i, q_data in enumerate(questions_data):
                question = Question(
                    id=f"q_{i}_{hash(q_data['question_text']) % 10000}",
                    question_text=q_data["question_text"],
                    question_type=QuestionType(q_data["question_type"]),
                    options=q_data.get("options"),
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data.get("explanation"),
                    difficulty=q_data.get("difficulty", 1),
                    source_chunk=combined_content[:200] + "..."
                )
                questions.append(question)
            
            return questions
        
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            print(f"DEBUG: Raw response: {response.text}")
            # Fallback to creating sample questions
            return self._create_fallback_questions(combined_content, num_questions)
        except Exception as e:
            print(f"DEBUG: General error: {e}")
            raise Exception(f"Failed to generate quiz questions: {str(e)}")
    
    async def evaluate_answer(self, question: Question, user_answer: str) -> Dict[str, Any]:
        """Evaluate a user's answer to a question"""
        
        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]:
            # Exact match for structured questions
            is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
            score = 1.0 if is_correct else 0.0
        else:
            # Use AI to evaluate short answer questions
            prompt = f"""
            Question: {question.question_text}
            Correct Answer: {question.correct_answer}
            User Answer: {user_answer}
            
            Evaluate the user's answer on a scale of 0.0 to 1.0 where:
            - 1.0 = Completely correct
            - 0.5 = Partially correct
            - 0.0 = Incorrect
            
            Return only a JSON object with:
            {{
                "score": 0.0-1.0,
                "is_correct": true/false,
                "feedback": "Brief feedback explaining the evaluation"
            }}
            """
            
            try:
                response = self.model.generate_content(prompt)
                evaluation = json.loads(response.text)
                score = evaluation["score"]
                is_correct = evaluation["is_correct"]
            except:
                # Fallback to simple comparison
                is_correct = user_answer.lower() in question.correct_answer.lower()
                score = 1.0 if is_correct else 0.0
        
        return {
            "score": score,
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation
        }
    
    async def generate_recommendations(self, quiz_results: Dict[str, Any], pdf_content: str) -> List[str]:
        """Generate learning recommendations based on quiz performance"""
        
        weak_areas = [
            area for area, score in quiz_results.get("topic_scores", {}).items() 
            if score < 0.7
        ]
        
        if not weak_areas:
            return ["Great job! You have a strong understanding of the material."]
        
        prompt = f"""
        Based on the quiz performance, the user struggled with these areas: {', '.join(weak_areas)}
        
        From the following content, suggest 3-5 specific study recommendations to help improve understanding:
        
        Content excerpt: {pdf_content[:2000]}
        
        Return recommendations as a JSON array of strings, each being a specific, actionable study suggestion.
        """
        
        try:
            response = self.model.generate_content(prompt)
            recommendations = json.loads(response.text)
            return recommendations
        except:
            return [
                f"Review the sections covering: {', '.join(weak_areas)}",
                "Practice with additional examples in the weak areas",
                "Create summary notes for better retention"
            ]
    
    def _create_fallback_questions(self, content: str, num_questions: int) -> List[Question]:
        """Create fallback questions when AI generation fails"""
        questions = []
        
        # Extract some key sentences from content for questions
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20][:num_questions]
        
        for i, sentence in enumerate(sentences):
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."
            
            question = Question(
                id=f"fallback_q_{i}",
                question_text=f"What is the main concept discussed in: '{sentence}'?",
                question_type=QuestionType.SHORT_ANSWER,
                options=None,
                correct_answer="Please refer to the document content for the answer.",
                explanation="This is a fallback question generated when AI processing failed.",
                difficulty=2,
                source_chunk=sentence
            )
            questions.append(question)
        
        # If no sentences found, create a generic question
        if not questions:
            questions.append(Question(
                id="fallback_generic",
                question_text="What are the main topics covered in this document?",
                question_type=QuestionType.SHORT_ANSWER,
                options=None,
                correct_answer="Please summarize the key points from the document.",
                explanation="Generic question created when content processing failed.",
                difficulty=2,
                source_chunk=content[:200] + "..."
            ))
        
        return questions[:num_questions]