# 📚 PDF Quiz & Notes System - Frontend Integration Guide

## 🎯 Complete User Flow for React Frontend

### **User Journey: From PDF Upload to Personalized Study Notes**

---

## 🔐 **Step 1: User Authentication**

### API Endpoint

```
POST /auth/login
```

### Request Data

```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

### Expected Response

```json
{
  "message": "Login successful",
  "user": {
    "uid": "user_123456",
    "email": "student@example.com",
    "name": "John Doe"
  },
  "access_token": "jwt_token_here"
}
```

### React Implementation

```jsx
// Firebase Auth Setup
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase-config";

const handleLogin = async (email, password) => {
  const userCredential = await signInWithEmailAndPassword(
    auth,
    email,
    password
  );
  const firebaseToken = await userCredential.user.getIdToken();

  const response = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ firebase_token: firebaseToken }),
  });

  const data = await response.json();
  localStorage.setItem("access_token", data.access_token);
};
```

---

## 📄 **Step 2: PDF Upload**

### API Endpoint

```
POST /pdf/upload
```

### Request Data

```javascript
const formData = new FormData();
formData.append("file", pdfFile);
```

### Expected Response

```json
{
  "message": "PDF uploaded successfully",
  "pdf_id": "pdf_d287d3b3fe66487a9766a3183f6da031",
  "filename": "machine_learning_basics.pdf",
  "status": "processing"
}
```

### React Implementation

```jsx
const handlePDFUpload = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/pdf/upload", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
    body: formData,
  });

  const data = await response.json();
  setPdfId(data.pdf_id);

  // Poll for processing completion
  pollProcessingStatus(data.pdf_id);
};

const pollProcessingStatus = async (pdfId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/pdf/${pdfId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();

    if (data.status === "completed") {
      clearInterval(interval);
      setProcessingComplete(true);
    }
  }, 2000);
};
```

---

## 🎯 **Step 3: Quiz Generation**

### API Endpoint

```
POST /quiz/generate/{pdf_id}
```

### Request Data

```json
{
  "num_questions": 5,
  "difficulty_range": [1, 3]
}
```

### Expected Response

```json
{
  "id": "quiz_7187a600afb24ba39051f4c03c92ad9c",
  "pdf_id": "pdf_d287d3b3fe66487a9766a3183f6da031",
  "questions": [
    {
      "id": "q1",
      "question_text": "What is machine learning?",
      "question_type": "multiple_choice",
      "options": [
        "AI subset",
        "Programming language",
        "Database",
        "Operating system"
      ],
      "difficulty": 2
    },
    {
      "id": "q2",
      "question_text": "Neural networks are inspired by the human brain.",
      "question_type": "true_false",
      "difficulty": 1
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### React Implementation

```jsx
const generateQuiz = async (pdfId) => {
  const response = await fetch(`/quiz/generate/${pdfId}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      num_questions: 5,
      difficulty_range: [1, 3],
    }),
  });

  const quiz = await response.json();
  setQuizData(quiz);
  setCurrentStep("taking_quiz");
};
```

---

## 📝 **Step 4: Quiz Submission**

### API Endpoint

```
POST /quiz/{quiz_id}/submit
```

### Request Data

```json
{
  "answers": {
    "q1": "AI subset",
    "q2": "True"
  }
}
```

### Expected Response

```json
{
  "quiz_attempt_id": "attempt_88c3d83822974ba5b6c72234c03f3928",
  "score": 40.0,
  "total_questions": 5,
  "correct_answers": 2,
  "detailed_results": [
    {
      "question_id": "q1",
      "user_answer": "AI subset",
      "correct_answer": "AI subset",
      "is_correct": true,
      "explanation": "Machine learning is indeed a subset of artificial intelligence."
    }
  ],
  "performance_level": "needs_improvement"
}
```

### React Implementation

```jsx
const submitQuiz = async (quizId, answers) => {
  const response = await fetch(`/quiz/${quizId}/submit`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answers }),
  });

  const results = await response.json();
  setQuizResults(results);

  // Automatically generate notes after quiz submission
  generateStudyNotes(results.quiz_attempt_id);
};
```

---

## ✍️ **Step 5: Generate Personalized Study Notes**

### API Endpoint

```
POST /notes/generate/{quiz_attempt_id}
```

### Request Data

```json
{
  "include_examples": true,
  "study_level": "comprehensive"
}
```

### Expected Response

```json
{
  "notes": {
    "id": "notes_pdf123_1640995200",
    "pdf_id": "pdf_d287d3b3fe66487a9766a3183f6da031",
    "quiz_attempt_id": "attempt_88c3d83822974ba5b6c72234c03f3928",
    "user_id": "user_123456",
    "pdf_title": "Machine Learning Basics.pdf",
    "generated_at": "2024-01-15T11:00:00Z",
    "performance_summary": {
      "score": 40.0,
      "level": "needs_improvement",
      "weak_topics": ["neural_networks", "deep_learning", "algorithms"],
      "total_questions": 5,
      "correct_answers": 2
    },
    "study_notes": "# 📚 Personalized Study Notes: Machine Learning Basics\n\n## 🎯 Executive Summary\nBased on your quiz performance of 40.0%, this study guide focuses on strengthening your understanding in key areas where improvement is needed...",
    "topics_covered": ["neural_networks", "deep_learning", "algorithms"],
    "study_priority": "high",
    "estimated_study_time": "2-3 hours intensive study",
    "next_review_date": "2024-01-17",
    "created_at": "2024-01-15T11:00:00Z"
  },
  "generation_stats": {
    "topics_analyzed": 3,
    "content_sources_used": 8,
    "performance_score": 40.0,
    "weak_areas_identified": 3,
    "generation_time": "completed",
    "ai_provider": "gemini"
  },
  "recommendations": [
    "Focus on neural network fundamentals",
    "Practice with deep learning examples",
    "Review algorithm implementations"
  ]
}
```

### React Implementation

```jsx
const generateStudyNotes = async (quizAttemptId) => {
  setNotesLoading(true);

  const response = await fetch(`/notes/generate/${quizAttemptId}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      include_examples: true,
      study_level: "comprehensive",
    }),
  });

  const notesData = await response.json();
  setStudyNotes(notesData.notes);
  setRecommendations(notesData.recommendations);
  setNotesLoading(false);
  setCurrentStep("study_notes");
};
```

---

## 📖 **Step 6: View & Manage Study Notes**

### Get Specific Notes

```
GET /notes/{notes_id}
```

### Get All Notes for PDF

```
GET /notes/pdf/{pdf_id}
```

### Get All User Notes

```
GET /notes/user/all
```

### Expected Response (All User Notes)

```json
{
  "total_notes": 12,
  "pdfs_with_notes": 4,
  "notes_by_pdf": [
    {
      "pdf_id": "pdf_d287d3b3fe66487a9766a3183f6da031",
      "pdf_title": "Machine Learning Basics.pdf",
      "notes": [
        {
          "id": "notes_pdf123_1640995200",
          "generated_at": "2024-01-15T11:00:00Z",
          "performance_summary": {
            "score": 40.0,
            "level": "needs_improvement"
          },
          "study_priority": "high"
        }
      ]
    }
  ]
}
```

---

## 📊 **Step 7: Performance Analytics**

### API Endpoint

```
GET /notes/analytics/performance
```

### Expected Response

```json
{
  "total_notes": 12,
  "average_score": 67.5,
  "improvement_trend": "improving",
  "common_weak_areas": [
    {
      "topic": "neural_networks",
      "frequency": 8
    },
    {
      "topic": "algorithms",
      "frequency": 6
    }
  ],
  "study_recommendations": [
    "Focus on neural network fundamentals",
    "Practice algorithm implementations",
    "Review mathematical concepts"
  ],
  "last_study_session": "2024-01-15T11:00:00Z"
}
```

---

## 🚀 **Complete React Component Example**

```jsx
import React, { useState, useEffect } from "react";
import { auth } from "./firebase-config";

const StudyPlatform = () => {
  const [currentStep, setCurrentStep] = useState("upload");
  const [pdfId, setPdfId] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [studyNotes, setStudyNotes] = useState(null);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("access_token");

  const handleFileUpload = async (file) => {
    setLoading(true);
    // Implementation from Step 2
    setLoading(false);
  };

  const handleQuizGeneration = async () => {
    setLoading(true);
    // Implementation from Step 3
    setLoading(false);
  };

  const handleQuizSubmission = async (answers) => {
    setLoading(true);
    // Implementation from Step 4 & 5
    setLoading(false);
  };

  return (
    <div className="study-platform">
      {currentStep === "upload" && (
        <PDFUploadComponent onUpload={handleFileUpload} loading={loading} />
      )}

      {currentStep === "quiz" && (
        <QuizComponent
          quiz={quizData}
          onSubmit={handleQuizSubmission}
          loading={loading}
        />
      )}

      {currentStep === "study_notes" && (
        <StudyNotesComponent
          notes={studyNotes}
          recommendations={recommendations}
        />
      )}
    </div>
  );
};
```

---

## 🔧 **Authentication Headers**

All API requests (except login) require:

```javascript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
}
```

---

## ⚡ **Error Handling**

```javascript
const apiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      if (response.status === 401) {
        // Redirect to login
        window.location.href = "/login";
        return;
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API Error:", error);
    // Show user-friendly error message
    setError("Something went wrong. Please try again.");
  }
};
```

---

## 🎯 **Key Features for Frontend**

1. **Real-time Processing Status**: Poll PDF processing completion
2. **Progressive Loading**: Show loading states for each step
3. **Error Recovery**: Handle API failures gracefully
4. **Responsive Design**: Mobile-friendly quiz interface
5. **Markdown Rendering**: Display formatted study notes
6. **Progress Tracking**: Show user's learning journey
7. **Offline Support**: Cache study notes locally
8. **Export Options**: Allow PDF/print of study notes

---

## 📱 **Mobile Considerations**

- Use responsive design for quiz interface
- Implement touch-friendly file upload
- Optimize markdown rendering for mobile
- Add swipe gestures for quiz navigation
- Implement pull-to-refresh for notes list

---

## 🔒 **Security Best Practices**

- Store JWT tokens securely
- Implement token refresh logic
- Validate file types before upload
- Sanitize user inputs
- Use HTTPS for all API calls
- Implement rate limiting on frontend
