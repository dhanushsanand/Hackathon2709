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
        """Generate quiz questions from content chunks with retry logic"""
        
        # Validate input
        if not content_chunks or len(content_chunks) == 0:
            print("WARNING: No content chunks provided, creating fallback questions")
            return self._create_fallback_questions("No content available", num_questions)
        
        # Combine chunks for context (limit to avoid token limits)
        combined_content = "\n".join(content_chunks[:5])  # Use first 5 chunks
        if len(combined_content) > 8000:  # Reduced limit for safety
            combined_content = combined_content[:8000] + "..."
        
        # Retry logic for API calls
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔄 Quiz generation attempt {attempt + 1}/{max_retries}")
                
                prompt = f"""
                Generate exactly {num_questions} quiz questions from the content below.

                CRITICAL: Respond with ONLY a valid JSON array. No markdown, no explanations, no extra text.

                Format each question exactly like this:
                [
                  {{
                    "question_text": "What is the main topic discussed?",
                    "question_type": "multiple_choice",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Brief explanation of why this is correct",
                    "difficulty": 2
                  }}
                ]

                Rules:
                - question_type must be: "multiple_choice", "true_false", or "short_answer"
                - difficulty must be integer 1-5
                - For true_false: options must be ["True", "False"]
                - For short_answer: options must be null
                - Make questions relevant to the content provided

                Content:
                {combined_content}
                """
                
                response = self.model.generate_content(prompt)
                
                if not response or not response.text:
                    print(f"❌ Empty response from Gemini on attempt {attempt + 1}")
                    continue
                
                print(f"✅ Received response from Gemini (length: {len(response.text)})")
                
                # Clean the response text more aggressively
                response_text = response.text.strip()
                
                # Remove various markdown patterns
                patterns_to_remove = [
                    "```json\n", "```json", "```\n", "```",
                    "**JSON:**", "**Response:**", "Here is the JSON:",
                    "Here are the questions:", "The questions are:"
                ]
                
                for pattern in patterns_to_remove:
                    response_text = response_text.replace(pattern, "")
                
                response_text = response_text.strip()
                
                # Find JSON array in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx + 1]
                
                print(f"🧹 Cleaned response preview: {response_text[:200]}...")
                
                # Parse JSON
                questions_data = json.loads(response_text)
                
                if not isinstance(questions_data, list):
                    raise ValueError("Response is not a JSON array")
                
                if len(questions_data) == 0:
                    raise ValueError("No questions in response")
                
                # Create Question objects
                questions = []
                for i, q_data in enumerate(questions_data):
                    try:
                        # Validate required fields
                        if not all(key in q_data for key in ["question_text", "question_type", "correct_answer"]):
                            print(f"⚠️  Skipping invalid question {i}: missing required fields")
                            continue
                        
                        question = Question(
                            id=f"q_{i}_{hash(str(q_data['question_text'])) % 10000}",
                            question_text=q_data["question_text"],
                            question_type=QuestionType(q_data["question_type"]),
                            options=q_data.get("options"),
                            correct_answer=q_data["correct_answer"],
                            explanation=q_data.get("explanation", "No explanation provided"),
                            difficulty=int(q_data.get("difficulty", 2)),
                            source_chunk=combined_content[:200] + "..."
                        )
                        questions.append(question)
                        
                    except Exception as e:
                        print(f"⚠️  Error creating question {i}: {e}")
                        continue
                
                if len(questions) > 0:
                    print(f"✅ Successfully created {len(questions)} questions")
                    return questions
                else:
                    raise ValueError("No valid questions could be created")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error on attempt {attempt + 1}: {e}")
                print(f"Raw response: {response.text[:500]}...")
                if attempt == max_retries - 1:
                    print("🔄 All retries failed, using fallback questions")
                    return self._create_fallback_questions(combined_content, num_questions)
                continue
                
            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print("🔄 All retries failed, using fallback questions")
                    return self._create_fallback_questions(combined_content, num_questions)
                continue
        
        # If all retries failed, return fallback
        print("⚠️  All attempts failed, returning fallback questions")
        return self._create_fallback_questions(combined_content, num_questions)
    
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
    def _create_fallback_questions(self, content: str, num_questions: int) -> List[Question]:
        """Create fallback questions when Gemini API fails"""
        
        print(f"🔄 Creating {num_questions} fallback questions")
        
        # Extract some keywords from content for basic questions
        words = content.lower().split()
        keywords = [word for word in words if len(word) > 4][:10]
        
        fallback_questions = []
        
        for i in range(min(num_questions, 5)):  # Limit to 5 fallback questions
            if i == 0:
                question = Question(
                    id=f"fallback_q_{i}",
                    question_text="What is the main topic discussed in this document?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    options=["The provided content", "General information", "Technical details", "Other topics"],
                    correct_answer="The provided content",
                    explanation="This question is based on the document content.",
                    difficulty=2,
                    source_chunk=content[:200] + "..."
                )
            elif i == 1:
                question = Question(
                    id=f"fallback_q_{i}",
                    question_text="This document contains important information.",
                    question_type=QuestionType.TRUE_FALSE,
                    options=["True", "False"],
                    correct_answer="True",
                    explanation="Documents typically contain important information.",
                    difficulty=1,
                    source_chunk=content[:200] + "..."
                )
            elif i == 2 and keywords:
                question = Question(
                    id=f"fallback_q_{i}",
                    question_text=f"What concept is related to '{keywords[0]}'?",
                    question_type=QuestionType.SHORT_ANSWER,
                    options=None,
                    correct_answer=f"Concepts related to {keywords[0]}",
                    explanation="This is based on key terms found in the document.",
                    difficulty=3,
                    source_chunk=content[:200] + "..."
                )
            elif i == 3:
                question = Question(
                    id=f"fallback_q_{i}",
                    question_text="Which of the following best describes this content?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    options=["Educational material", "Entertainment", "Advertisement", "Personal diary"],
                    correct_answer="Educational material",
                    explanation="Most documents uploaded for quiz generation are educational.",
                    difficulty=2,
                    source_chunk=content[:200] + "..."
                )
            else:
                question = Question(
                    id=f"fallback_q_{i}",
                    question_text="The document provides detailed information on its subject matter.",
                    question_type=QuestionType.TRUE_FALSE,
                    options=["True", "False"],
                    correct_answer="True",
                    explanation="Documents typically provide detailed information.",
                    difficulty=1,
                    source_chunk=content[:200] + "..."
                )
            
            fallback_questions.append(question)
        
        print(f"✅ Created {len(fallback_questions)} fallback questions")
        return fallback_questions