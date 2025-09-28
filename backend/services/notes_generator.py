from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from services.embeddings import EmbeddingService
from services.gemini import GeminiService
from models.quiz import QuizAttempt, Question
from models.pdf import PDFDocument

class NotesGeneratorService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.gemini_service = GeminiService()
    
    async def analyze_quiz_performance(self, quiz_attempt: QuizAttempt, questions: List[Question]) -> Dict[str, Any]:
        """Analyze quiz performance to identify weak areas"""
        
        # Categorize questions by performance
        weak_areas = []
        strong_areas = []
        needs_review = []
        
        # Parse quiz results (assuming answers format includes scores)
        for question in questions:
            question_id = question.id
            user_answer = quiz_attempt.answers.get(question_id, "")
            
            # For this example, we'll simulate scoring based on answer quality
            # In practice, this would come from the actual quiz evaluation
            is_correct = self._evaluate_answer_quality(question, user_answer)
            
            topic_keywords = self._extract_topic_keywords(question.question_text)
            
            performance_data = {
                "question_id": question_id,
                "question_text": question.question_text,
                "topic_keywords": topic_keywords,
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "difficulty": question.difficulty,
                "explanation": question.explanation
            }
            
            if not is_correct:
                if question.difficulty >= 3:
                    weak_areas.append(performance_data)
                else:
                    needs_review.append(performance_data)
            else:
                strong_areas.append(performance_data)
        
        # Calculate performance metrics
        total_questions = len(questions)
        correct_answers = len(strong_areas)
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Identify knowledge gaps
        weak_topics = self._identify_weak_topics(weak_areas + needs_review)
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": score_percentage,
            "weak_areas": weak_areas,
            "needs_review": needs_review,
            "strong_areas": strong_areas,
            "weak_topics": weak_topics,
            "performance_level": self._determine_performance_level(score_percentage)
        }
    
    def _evaluate_answer_quality(self, question: Question, user_answer: str) -> bool:
        """Simple answer evaluation (in practice, use the actual quiz scoring)"""
        if question.question_type == "multiple_choice":
            return user_answer.lower().strip() == question.correct_answer.lower().strip()
        elif question.question_type == "true_false":
            return user_answer.lower().strip() == question.correct_answer.lower().strip()
        else:
            # For short answer, do basic keyword matching
            correct_keywords = question.correct_answer.lower().split()
            user_keywords = user_answer.lower().split()
            overlap = len(set(correct_keywords) & set(user_keywords))
            return overlap >= len(correct_keywords) * 0.5  # 50% keyword overlap
    
    def _extract_topic_keywords(self, question_text: str) -> List[str]:
        """Extract key topics from question text with enhanced analysis"""
        import re
        
        # Remove question words and extract meaningful terms
        question_words = {
            "what", "how", "why", "when", "where", "which", "who", "is", "are", "the", "a", "an",
            "does", "do", "can", "will", "would", "should", "could", "might", "may", "must",
            "this", "that", "these", "those", "and", "or", "but", "for", "with", "from", "to"
        }
        
        # Extract words and clean them
        words = re.findall(r'\b\w+\b', question_text.lower())
        keywords = []
        
        for word in words:
            if len(word) > 3 and word not in question_words:
                # Add both singular and potential compound terms
                keywords.append(word)
                
        # Also look for compound terms (two words together that might be important)
        word_pairs = []
        for i in range(len(words) - 1):
            if (len(words[i]) > 3 and len(words[i+1]) > 3 and 
                words[i] not in question_words and words[i+1] not in question_words):
                compound = f"{words[i]}_{words[i+1]}"
                word_pairs.append(compound)
        
        # Combine single words and pairs, prioritize longer/compound terms
        all_keywords = word_pairs + keywords
        
        return all_keywords[:8]  # Return top 8 keywords including compounds
    
    def _identify_weak_topics(self, weak_questions: List[Dict]) -> List[str]:
        """Identify common topics in weak performance areas"""
        topic_frequency = {}
        
        for question_data in weak_questions:
            for keyword in question_data["topic_keywords"]:
                topic_frequency[keyword] = topic_frequency.get(keyword, 0) + 1
        
        # Sort by frequency and return top topics
        sorted_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, freq in sorted_topics[:10]]  # Top 10 weak topics
    
    def _determine_performance_level(self, score_percentage: float) -> str:
        """Determine overall performance level"""
        if score_percentage >= 90:
            return "excellent"
        elif score_percentage >= 80:
            return "good"
        elif score_percentage >= 70:
            return "satisfactory"
        elif score_percentage >= 60:
            return "needs_improvement"
        else:
            return "requires_significant_study"    

    async def find_relevant_content(self, weak_topics: List[str], pdf_id: str, max_chunks: int = 15) -> List[Dict[str, Any]]:
        """Use Pinecone to find comprehensive relevant content for weak topics"""
        
        relevant_content = []
        
        for topic in weak_topics:
            # Create comprehensive search queries for each weak topic
            search_queries = [
                f"What is {topic}? Definition and explanation",
                f"Explain {topic} in detail with examples",
                f"How does {topic} work? Process and mechanism", 
                f"{topic} definition examples applications",
                f"Key concepts related to {topic}",
                f"Important aspects of {topic}",
                f"Understanding {topic} fundamentals",
                f"{topic} principles and theory"
            ]
            
            for query in search_queries:
                try:
                    # Use Pinecone similarity search to find relevant content
                    search_results = await self.embedding_service.similarity_search(
                        query=query,
                        pdf_id=pdf_id,
                        top_k=5  # Get more results per query
                    )
                    
                    for result in search_results:
                        if result["score"] > 0.6:  # Lower threshold to get more content
                            relevant_content.append({
                                "topic": topic,
                                "query": query,
                                "content": result["text"],
                                "relevance_score": result["score"],
                                "chunk_index": result["chunk_index"],
                                "source": "pdf_content"
                            })
                
                except Exception as e:
                    print(f"Error searching for topic '{topic}': {e}")
        
        # If no content found via search, try to get general content from the PDF
        if not relevant_content:
            print("No specific content found, getting general PDF content...")
            try:
                # Get some general content chunks from the PDF
                general_results = await self.embedding_service.similarity_search(
                    query="main concepts key information important topics",
                    pdf_id=pdf_id,
                    top_k=10
                )
                
                for result in general_results:
                    relevant_content.append({
                        "topic": "general_content",
                        "query": "general_search",
                        "content": result["text"],
                        "relevance_score": result["score"],
                        "chunk_index": result["chunk_index"],
                        "source": "pdf_content"
                    })
            except Exception as e:
                print(f"Error getting general content: {e}")
        
        # Remove duplicates and sort by relevance
        unique_content = {}
        for item in relevant_content:
            key = f"{item['topic']}_{item['chunk_index']}"
            if key not in unique_content or item['relevance_score'] > unique_content[key]['relevance_score']:
                unique_content[key] = item
        
        # Sort by relevance score and limit results
        sorted_content = sorted(unique_content.values(), key=lambda x: x['relevance_score'], reverse=True)
        return sorted_content[:max_chunks]
    
    async def generate_personalized_notes(self, 
                                        performance_analysis: Dict[str, Any], 
                                        relevant_content: List[Dict[str, Any]],
                                        pdf_document: PDFDocument) -> Dict[str, Any]:
        """Generate comprehensive personalized study notes using Gemini"""
        
        # Prepare context for note generation
        weak_topics = performance_analysis["weak_topics"]
        performance_level = performance_analysis["performance_level"]
        score_percentage = performance_analysis["score_percentage"]
        
        # Organize content by topic
        content_by_topic = {}
        for item in relevant_content:
            topic = item["topic"]
            if topic not in content_by_topic:
                content_by_topic[topic] = []
            content_by_topic[topic].append(item["content"])
        
        # Create comprehensive prompt for note generation
        prompt = f"""
        You are an expert educational content creator. Create comprehensive, detailed study notes based on the student's quiz performance analysis.
        
        STUDENT PERFORMANCE ANALYSIS:
        - Overall Quiz Score: {score_percentage:.1f}%
        - Performance Level: {performance_level}
        - Document Source: {pdf_document.original_filename}
        - Primary Areas Needing Improvement: {', '.join(weak_topics[:5])}
        
        RELEVANT CONTENT FROM DOCUMENT:
        """
        
        for topic, contents in content_by_topic.items():
            prompt += f"\n\n=== TOPIC: {topic.upper()} ===\n"
            for i, content in enumerate(contents[:3]):  # Limit to 3 pieces per topic
                prompt += f"Content {i+1}: {content[:400]}...\n\n"
        
        prompt += f"""
        
        INSTRUCTIONS FOR COMPREHENSIVE NOTES:
        Create detailed, structured study notes that are personalized for this student's performance level ({performance_level}). 
        
        REQUIRED STRUCTURE:
        
        # 📚 Personalized Study Notes: [Document Title]
        
        ## 🎯 Executive Summary
        - Brief overview of quiz performance
        - Key areas requiring immediate attention
        - Learning objectives for this study session
        
        ## 📊 Performance Analysis
        - Detailed breakdown of quiz results
        - Strengths and weaknesses identified
        - Learning gaps to address
        
        ## 🔍 Priority Topics for Review
        
        For EACH weak topic identified, create a comprehensive section with:
        
        ### [Topic Name]
        
        #### 📖 Core Concepts
        - Fundamental definitions and principles
        - Key terminology with clear explanations
        - Important relationships and connections
        
        #### 🔬 Detailed Explanation
        - In-depth explanation using content from the document
        - Step-by-step breakdowns where applicable
        - Real-world applications and examples
        - Common misconceptions to avoid
        
        #### 💡 Key Points to Remember
        - Bullet points of essential information
        - Memory aids and mnemonics
        - Critical facts and figures
        
        #### 🎯 Practice Focus Areas
        - Specific aspects to practice
        - Types of questions to expect
        - Problem-solving approaches
        
        ## 📝 Additional Study Materials
        
        ### 🧠 Self-Assessment Questions
        Create 3-5 practice questions for each weak topic to test understanding
        
        ### 🔄 Review Schedule
        - Immediate review priorities (next 24 hours)
        - Short-term goals (next week)
        - Long-term retention strategies
        
        ### 📚 Supplementary Learning
        - Suggested additional reading areas
        - Concepts to explore further
        - Connections to other topics
        
        ## 🎯 Personalized Study Strategy
        Based on {performance_level} performance level:
        - Specific study techniques recommended
        - Time allocation suggestions
        - Learning style adaptations
        - Progress tracking methods
        
        ## ✅ Success Metrics
        - How to measure improvement
        - Milestones to achieve
        - Signs of mastery
        
        IMPORTANT GUIDELINES:
        1. Make content detailed and comprehensive - avoid just headlines
        2. Use the actual content from the document extensively
        3. Explain concepts thoroughly with examples
        4. Tailor difficulty and depth to the student's performance level
        5. Include specific, actionable study advice
        6. Make it engaging and easy to follow
        7. Focus heavily on the identified weak areas
        8. Provide clear structure with proper headings and subheadings
        
        Generate comprehensive, detailed notes that will genuinely help this student improve their understanding and performance.
        """
        
        try:
            # Generate notes using Gemini
            response = self.gemini_service.model.generate_content(prompt)
            generated_notes = response.text
            
            # Structure the final notes
            notes_data = {
                "id": f"notes_{pdf_document.id}_{int(datetime.now().timestamp())}",
                "pdf_id": pdf_document.id,
                "pdf_title": pdf_document.original_filename,
                "generated_at": datetime.now(),
                "performance_summary": {
                    "score": score_percentage,
                    "level": performance_level,
                    "weak_topics": weak_topics,
                    "total_questions": performance_analysis["total_questions"],
                    "correct_answers": performance_analysis["correct_answers"]
                },
                "study_notes": generated_notes,
                "relevant_content_sources": len(relevant_content),
                "topics_covered": list(content_by_topic.keys()),
                "study_priority": self._determine_study_priority(performance_level),
                "estimated_study_time": self._estimate_study_time(performance_analysis),
                "next_review_date": self._suggest_review_date(performance_level)
            }
            
            return notes_data
            
        except Exception as e:
            print(f"Error generating notes with Gemini: {e}")
            
            # Fallback: Create basic notes from content
            return self._create_fallback_notes(performance_analysis, relevant_content, pdf_document)    
  
    def _create_fallback_notes(self, performance_analysis: Dict[str, Any], 
                                relevant_content: List[Dict[str, Any]], 
                                pdf_document: PDFDocument) -> Dict[str, Any]:
            """Create comprehensive fallback notes when AI generation fails"""
            
            weak_topics = performance_analysis["weak_topics"]
            score_percentage = performance_analysis["score_percentage"]
            performance_level = performance_analysis["performance_level"]
            
            # Create comprehensive structured notes
            notes_content = f"""
    # 📚 Comprehensive Study Notes: {pdf_document.original_filename}

    ## 🎯 Executive Summary
    Based on your quiz performance of {score_percentage:.1f}%, this study guide focuses on strengthening your understanding in key areas where improvement is needed.

    **Performance Level:** {performance_level.replace('_', ' ').title()}
    **Primary Focus Areas:** {', '.join(weak_topics[:5])}

    ## 📊 Performance Analysis
    - **Total Questions:** {performance_analysis['total_questions']}
    - **Correct Answers:** {performance_analysis['correct_answers']}
    - **Score:** {score_percentage:.1f}%
    - **Areas Requiring Attention:** {len(weak_topics)} topics identified

    ## 🔍 Priority Topics for Detailed Review

    """
            
            # Add comprehensive content for each weak topic
            content_by_topic = {}
            for item in relevant_content:
                topic = item["topic"]
                if topic not in content_by_topic:
                    content_by_topic[topic] = []
                content_by_topic[topic].append(item["content"])
            
            for i, (topic, contents) in enumerate(content_by_topic.items(), 1):
                notes_content += f"""
    ### {i}. {topic.title().replace('_', ' ')}

    #### 📖 Core Concepts
    This topic appeared in your quiz and requires focused attention based on your performance.

    #### 🔬 Key Information from Document
    """
                for j, content in enumerate(contents[:3], 1):  # Up to 3 pieces per topic
                    notes_content += f"""
    **Content {j}:**
    {content[:500]}...

    **Key Takeaways:**
    - Review the fundamental concepts presented above
    - Pay attention to definitions and key terminology
    - Understand the relationships between different elements

    """
                
                notes_content += f"""
    #### 💡 Study Focus for {topic.title()}
    - **Immediate Priority:** Review the content above thoroughly
    - **Practice Needed:** Create your own examples and explanations
    - **Common Mistakes:** Pay attention to details that might have caused quiz errors
    - **Mastery Check:** Can you explain this concept to someone else?

    """
            
            notes_content += f"""
    ## 📝 Comprehensive Study Strategy

    ### 🧠 Self-Assessment Questions
    For each topic above, ask yourself:
    1. Can I define the key terms without looking?
    2. Do I understand how this concept applies in practice?
    3. What examples can I think of for this topic?
    4. How does this relate to other concepts in the document?

    ### 🔄 Recommended Study Schedule
    **Based on your {performance_level.replace('_', ' ')} performance:**

    **Immediate (Next 24 hours):**
    - Review all highlighted content above
    - Create summary notes for each weak topic
    - Test your understanding with the self-assessment questions

    **Short-term (Next week):**
    - Practice applying concepts in different contexts
    - Seek additional examples and explanations
    - Review and reinforce your understanding

    **Long-term:**
    - Regular review sessions to maintain knowledge
    - Connect these concepts to new learning
    - Monitor your progress with practice questions

    ### 📚 Additional Learning Strategies
    1. **Active Reading:** Don't just read - summarize and explain concepts aloud
    2. **Concept Mapping:** Draw connections between different topics
    3. **Practice Application:** Use concepts in different scenarios
    4. **Peer Discussion:** Explain concepts to others or discuss with classmates
    5. **Regular Testing:** Quiz yourself frequently on the material

    ## 🎯 Success Metrics
    **You'll know you're improving when you can:**
    - Explain each weak topic clearly and confidently
    - Apply concepts to new situations or examples
    - Answer similar quiz questions correctly
    - Connect these topics to broader themes in the subject

    ## ✅ Next Steps
    1. **Start with the highest priority topic** (first one listed above)
    2. **Spend focused time** on each section - don't rush
    3. **Test yourself regularly** using the self-assessment approach
    4. **Track your progress** and celebrate improvements
    5. **Seek help** if any concepts remain unclear after focused study

    **Estimated Study Time:** {self._estimate_study_time(performance_analysis)}
    **Recommended Review Date:** {self._suggest_review_date(performance_level)}

    ---
    *These notes are personalized based on your quiz performance. Focus on the areas highlighted above for maximum improvement.*
    """
            
            return {
                "id": f"notes_{pdf_document.id}_{int(datetime.now().timestamp())}",
                "pdf_id": pdf_document.id,
                "pdf_title": pdf_document.original_filename,
                "generated_at": datetime.now(),
                "performance_summary": {
                    "score": score_percentage,
                    "weak_topics": weak_topics,
                    "total_questions": performance_analysis["total_questions"]
                },
                "study_notes": notes_content,
                "relevant_content_sources": len(relevant_content),
                "topics_covered": list(content_by_topic.keys()),
                "study_priority": self._determine_study_priority(performance_level),
                "estimated_study_time": self._estimate_study_time(performance_analysis)
            }
        
    def _determine_study_priority(self, performance_level: str) -> str:
        """Determine study priority based on performance"""
        priority_map = {
            "excellent": "low",
            "good": "low", 
            "satisfactory": "medium",
            "needs_improvement": "high",
            "requires_significant_study": "urgent"
        }
        return priority_map.get(performance_level, "medium")
    
    def _estimate_study_time(self, performance_analysis: Dict[str, Any]) -> str:
        """Estimate recommended study time"""
        score = performance_analysis["score_percentage"]
        weak_areas_count = len(performance_analysis["weak_areas"])
        
        if score >= 90:
            return "15-30 minutes review"
        elif score >= 80:
            return "30-45 minutes focused study"
        elif score >= 70:
            return "1-2 hours comprehensive review"
        elif score >= 60:
            return "2-3 hours intensive study"
        else:
            return "3+ hours deep learning required"
    
    def _suggest_review_date(self, performance_level: str) -> str:
        """Suggest when to review the material again"""
        days_map = {
            "excellent": 7,      # 1 week
            "good": 5,           # 5 days
            "satisfactory": 3,   # 3 days
            "needs_improvement": 2,  # 2 days
            "requires_significant_study": 1  # 1 day
        }
        
        days = days_map.get(performance_level, 3)
        review_date = datetime.now() + timedelta(days=days)
        return review_date.strftime("%Y-%m-%d")
    
    async def create_comprehensive_notes(self, 
                                    quiz_attempt: QuizAttempt, 
                                    questions: List[Question], 
                                    pdf_document: PDFDocument) -> Dict[str, Any]:
        """Main method to create comprehensive personalized notes"""
        
        print(f"🔍 Analyzing quiz performance for PDF: {pdf_document.original_filename}")
        
        # Step 1: Analyze quiz performance
        performance_analysis = await self.analyze_quiz_performance(quiz_attempt, questions)
        
        print(f"📊 Performance analysis complete:")
        print(f"   Score: {performance_analysis['score_percentage']:.1f}%")
        print(f"   Weak topics: {', '.join(performance_analysis['weak_topics'][:3])}")
        
        # Step 2: Find relevant content using Pinecone
        print(f"🔎 Searching for relevant content in Pinecone...")
        relevant_content = await self.find_relevant_content(
            weak_topics=performance_analysis["weak_topics"],
            pdf_id=pdf_document.id,
            max_chunks=15
        )
        
        print(f"📚 Found {len(relevant_content)} relevant content pieces")
        
        # Step 3: Generate personalized notes
        print(f"✍️  Generating personalized study notes...")
        notes = await self.generate_personalized_notes(
            performance_analysis=performance_analysis,
            relevant_content=relevant_content,
            pdf_document=pdf_document
        )
        
        print(f"✅ Comprehensive notes generated successfully")
        print(f"   Topics covered: {len(notes['topics_covered'])}")
        print(f"   Study priority: {notes['study_priority']}")
        print(f"   Estimated study time: {notes['estimated_study_time']}")
        
        return notes