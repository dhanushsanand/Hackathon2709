# PDF Quiz System API Testing Guide

## Prerequisites

1. **Start your backend server:**

   ```bash
   cd backend
   python main.py
   ```

   Server should be running on `http://localhost:8000`

2. **Import Postman Collection:**
   - Open Postman
   - Click "Import" → "Upload Files"
   - Select `postman_collection.json`
   - Collection will be imported with all endpoints

## Step-by-Step Testing Process

### Phase 1: Basic Health Checks

#### 1.1 Test Root Endpoint

- **Request:** `GET /`
- **Expected Response:** `{"message": "PDF Quiz System API"}`
- **Purpose:** Verify server is running

#### 1.2 Test Health Check

- **Request:** `GET /health`
- **Expected Response:** `{"status": "healthy"}`
- **Purpose:** Verify all services are operational

### Phase 2: Authentication Flow

#### 2.1 Login with Google (Firebase)

- **Request:** `POST /auth/google`
- **Body:**
  ```json
  {
    "firebase_token": "YOUR_FIREBASE_TOKEN_HERE"
  }
  ```
- **Expected Response:**
  ```json
  {
    "access_token": "jwt_token_here",
    "token_type": "bearer"
  }
  ```
- **Note:** You need a valid Firebase token. For testing, you can:
  - Use Firebase Auth in a web app to get a token
  - Or temporarily modify the auth middleware for testing

#### 2.2 Get Current User Info

- **Request:** `GET /auth/me`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** User object with uid, email, etc.

### Phase 3: PDF Management

#### 3.1 Upload PDF

- **Request:** `POST /pdf/upload`
- **Headers:** `Authorization: Bearer {access_token}`
- **Body:** Form-data with `file` field containing a PDF
- **Expected Response:**
  ```json
  {
    "pdf_id": "generated_pdf_id",
    "message": "PDF uploaded successfully",
    "status": "processing"
  }
  ```
- **Note:** Save the `pdf_id` for subsequent tests

#### 3.2 Get PDF Details

- **Request:** `GET /pdf/{pdf_id}`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** PDF document details including processing status

#### 3.3 Get All User PDFs

- **Request:** `GET /pdf/user/all`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Array of user's PDF documents

### Phase 4: Quiz Generation and Management

#### 4.1 Generate Quiz from PDF

- **Request:** `POST /quiz/generate/{pdf_id}`
- **Headers:** `Authorization: Bearer {access_token}`
- **Body:**
  ```json
  {
    "num_questions": 5,
    "difficulty": "medium"
  }
  ```
- **Expected Response:**
  ```json
  {
    "quiz_id": "generated_quiz_id",
    "questions": [...],
    "message": "Quiz generated successfully"
  }
  ```
- **Note:** Save the `quiz_id` for subsequent tests

#### 4.2 Get Quiz Details

- **Request:** `GET /quiz/{quiz_id}`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Complete quiz with questions and options

#### 4.3 Submit Quiz Answers

- **Request:** `POST /quiz/{quiz_id}/submit`
- **Headers:** `Authorization: Bearer {access_token}`
- **Body:**
  ```json
  {
    "answers": {
      "question_1_id": "option_a",
      "question_2_id": "option_b",
      "question_3_id": "option_c"
    }
  }
  ```
- **Expected Response:** Quiz results with score and feedback

#### 4.4 Get Quiz Attempts

- **Request:** `GET /quiz/{quiz_id}/attempts`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Array of quiz attempts with scores

#### 4.5 Get All User Quizzes

- **Request:** `GET /quiz/user/all`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Array of user's quizzes

### Phase 5: User Dashboard and Analytics

#### 5.1 Get User Dashboard

- **Request:** `GET /user/dashboard`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Dashboard data with stats and recent activity

#### 5.2 Get User Recommendations

- **Request:** `GET /user/recommendations`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Personalized learning recommendations

#### 5.3 Get User Analytics

- **Request:** `GET /user/analytics`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Detailed analytics and performance metrics

### Phase 6: Cleanup (Optional)

#### 6.1 Delete PDF

- **Request:** `DELETE /pdf/{pdf_id}`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Confirmation message

#### 6.2 Logout

- **Request:** `POST /auth/logout`
- **Headers:** `Authorization: Bearer {access_token}`
- **Expected Response:** Logout confirmation

## Testing Tips

### 1. Environment Variables

Set up Postman environment variables:

- `base_url`: `http://localhost:8000`
- `access_token`: Will be auto-populated after login
- `pdf_id`: Will be auto-populated after PDF upload
- `quiz_id`: Will be auto-populated after quiz generation

### 2. Test Data Preparation

- Prepare a sample PDF file for upload testing
- Have a valid Firebase token ready (or modify auth for testing)

### 3. Error Testing

Test error scenarios:

- Upload invalid file types
- Access resources without authentication
- Submit invalid quiz answers
- Access non-existent resources

### 4. Performance Testing

- Test with large PDF files
- Test concurrent requests
- Monitor response times

## Common Issues and Solutions

### Authentication Issues

- **Problem:** 401 Unauthorized
- **Solution:** Ensure valid Firebase token and proper Authorization header

### File Upload Issues

- **Problem:** 413 Request Entity Too Large
- **Solution:** Check file size limits in FastAPI configuration

### Database Connection Issues

- **Problem:** 500 Internal Server Error
- **Solution:** Verify Firebase/Pinecone credentials and network connectivity

### Embedding Service Issues

- **Problem:** Embedding generation fails
- **Solution:** Check Gemini API key and network connectivity

## Automated Testing Script

You can also run the collection using Newman (Postman CLI):

```bash
# Install Newman
npm install -g newman

# Run the collection
newman run postman_collection.json \
  --environment your_environment.json \
  --reporters cli,html \
  --reporter-html-export test-results.html
```

This will generate an HTML report with all test results.
