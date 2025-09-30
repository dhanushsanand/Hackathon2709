# 🎓 LearnNest - AI-Powered Personalized Learning Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Transform any PDF into an intelligent, interactive learning experience with AI-generated quizzes and personalized study notes.

## 🚀 What is LearnNest?

LearnNest revolutionizes studying by converting passive PDF reading into active, adaptive learning. Upload your study materials and get instant AI-generated quizzes, performance analytics, and personalized study recommendations.

### ✨ Key Features

- **🤖 AI-Powered Quiz Generation**: Automatically creates diverse question types from PDF content
- **📊 Smart Analytics**: Track learning progress with detailed performance metrics
- **📝 Personalized Study Notes**: AI-generated notes focusing on weak areas
- **🎯 Adaptive Recommendations**: Custom study plans based on performance patterns
- **☁️ Cloud Integration**: Secure document storage and processing
- **📱 Modern UI**: Responsive React frontend with intuitive design

## 🏗️ Architecture

### Backend (FastAPI + Python)

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── run_all_tests.py       # Test runner script
├── service-account.json   # Firebase credentials
├── .env                   # Environment variables
├── routers/               # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── pdf.py            # PDF upload and processing
│   ├── quiz.py           # Quiz generation and management
│   ├── notes.py          # Study notes generation
│   └── user.py           # User management and analytics
├── services/             # Business logic services
│   ├── gemini.py         # Google Gemini AI integration
│   ├── pdf_processor.py  # PDF text extraction
│   ├── notes_generator.py # Study notes generation
│   ├── embeddings.py     # Vector embeddings for content
│   └── auth.py           # Authentication service
├── models/               # Pydantic data models
│   ├── user.py           # User data models
│   ├── pdf.py            # PDF document models
│   ├── quiz.py           # Quiz and question models
│   └── notes.py          # Study notes models
├── utils/                # Utility functions
│   ├── database.py       # Firebase Firestore operations
│   ├── cloudinary.py     # Cloud storage management
│   ├── storage.py        # File handling utilities
│   └── helper.py         # General helper functions
├── middleware/           # Request middleware
│   └── auth.py           # JWT authentication
└── myVenv/               # Python virtual environment
```

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **AI/ML**: Google Gemini 2.0 Flash, Pinecone Vector DB
- **Database**: Firebase Firestore
- **Storage**: Cloudinary
- **PDF Processing**: PyPDF2, PDFPlumber
- **Authentication**: JWT with Firebase Auth

### Infrastructure

- **Cloud Storage**: Cloudinary
- **Database**: Firebase Firestore
- **Vector Search**: Pinecone
- **Authentication**: Firebase Auth

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Firebase Project
- Google Gemini API Key
- Cloudinary Account
- Pinecone Account

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/dhanushsanand/Hackathon2709.git
   cd Hackathon2709/backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv myVenv
   source myVenv/bin/activate  # On Windows: myVenv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the backend directory:

   ```env
   # Firebase Configuration
   FIREBASE_CREDENTIALS_PATH=./service-account.json
   FIREBASE_STORAGE_BUCKET=your-firebase-bucket

   # Google Gemini AI
   GEMINI_API_KEY=your-gemini-api-key

   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret

   # Pinecone
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_ENVIRONMENT=your-pinecone-environment
   PINECONE_INDEX_NAME=asu-agent

   # Application Settings
   SECRET_KEY=your-secret-key
   TEST_MODE=false
   ```

5. **Firebase Setup**

   - Download your Firebase service account JSON file
   - Place it as `service-account.json` in the backend directory

6. **Run the backend**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API will be available at: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs

## 📚 API Documentation

Once the backend is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication

- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info

#### PDF Management

- `POST /pdf/upload` - Upload PDF document
- `GET /pdf/user/all` - Get user's PDFs
- `DELETE /pdf/{pdf_id}` - Delete PDF

#### Quiz System

- `POST /quiz/generate/{pdf_id}` - Generate quiz from PDF
- `GET /quiz/{quiz_id}` - Get quiz details
- `POST /quiz/{quiz_id}/submit` - Submit quiz answers
- `GET /quiz/user/all` - Get user's quizzes with status

#### Study Notes

- `POST /notes/generate/{quiz_attempt_id}` - Generate study notes
- `GET /notes/user/all` - Get all user notes
- `GET /notes/analytics/performance` - Performance analytics

#### User Analytics

- `GET /user/dashboard` - User dashboard data
- `GET /user/analytics` - Detailed analytics
- `GET /user/files` - Get user's uploaded files

## 🧪 Testing

### Run All Tests

```bash
cd backend
python run_all_tests.py
```

### Manual API Testing

Use tools like Postman, curl, or the interactive API docs at http://localhost:8000/docs to test the endpoints.

### Test with Interactive Docs

1. Start the backend server
2. Visit http://localhost:8000/docs
3. Use the "Try it out" feature for each endpoint

## 🔧 Configuration

### Environment Variables

| Variable                    | Description                           | Required |
| --------------------------- | ------------------------------------- | -------- |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON | Yes      |
| `FIREBASE_STORAGE_BUCKET`   | Firebase storage bucket name          | Yes      |
| `GEMINI_API_KEY`            | Google Gemini API key                 | Yes      |
| `CLOUDINARY_CLOUD_NAME`     | Cloudinary cloud name                 | Yes      |
| `CLOUDINARY_API_KEY`        | Cloudinary API key                    | Yes      |
| `CLOUDINARY_API_SECRET`     | Cloudinary API secret                 | Yes      |
| `PINECONE_API_KEY`          | Pinecone API key                      | Yes      |
| `PINECONE_ENVIRONMENT`      | Pinecone environment                  | Yes      |
| `SECRET_KEY`                | JWT secret key                        | Yes      |
| `TEST_MODE`                 | Enable test mode (true/false)         | No       |

### Test Mode

Set `TEST_MODE=true` to use in-memory storage instead of external services during development.

## 📖 User Guide

### API-Based Usage

### 1. Upload a PDF

- Use `POST /pdf/upload` endpoint
- Send PDF file in the request body
- Wait for processing to complete

### 2. Generate Quiz

- Use `POST /quiz/generate/{pdf_id}` endpoint
- Set number of questions (1-10)
- Set difficulty range
- Receive AI-powered quiz

### 3. Take Quiz

- Use `POST /quiz/{quiz_id}/submit` endpoint
- Submit answers for questions of various types:
  - Multiple choice
  - True/False
  - Short answer
- Get immediate feedback

### 4. View Results

- Use `GET /quiz/{quiz_id}/attempts` endpoint
- Get detailed performance analysis
- See correct answers and explanations
- Track improvement over time

### 5. Study Notes

- Use `POST /notes/generate/{quiz_attempt_id}` endpoint
- Generate personalized study notes
- Focus on identified weak areas
- Get AI-powered recommendations

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation as needed
- Use type hints in Python code

## 🐛 Troubleshooting

### Common Issues

#### "NoneType object has no attribute 'collection'"

- Ensure Firebase credentials are properly configured
- Check `TEST_MODE` setting in environment
- Verify Firebase service account permissions

#### Quiz Generation Fails

- Verify Gemini API key is valid
- Check PDF content is extractable
- Review content length limits

#### File Upload Issues

- Confirm Cloudinary credentials
- Check file size limits
- Verify network connectivity

### Debug Mode

Enable detailed logging by setting log level in `config.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

### Benchmarks

- **Quiz Generation**: ~5-15 seconds per quiz
- **PDF Processing**: ~2-10 seconds per document
- **API Response Time**: <200ms average
- **Concurrent Users**: Tested up to 50 simultaneous users

### Optimization Tips

- Use test mode for development
- Implement caching for frequently accessed data
- Monitor API rate limits
- Optimize PDF preprocessing

## 🛡️ Security

### Implemented Security Measures

- JWT-based authentication
- Firebase security rules
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure file upload validation

### Best Practices

- Keep API keys secure
- Use HTTPS in production
- Implement proper CORS policies
- Regular security audits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Backend Development**: Python, FastAPI, AI Integration
- **Frontend Development**: React, TypeScript, UI/UX
- **DevOps**: Cloud Infrastructure, Database Design
- **AI/ML**: Gemini Integration, Content Processing

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- Firebase for backend infrastructure
- Cloudinary for file storage
- Pinecone for vector search
- FastAPI community for excellent documentation

## 📞 Support

For support and questions:

- 🐛 Issues: [GitHub Issues](https://github.com/dhanushsanand/Hackathon2709/issues)
- 📧 Contact: Through GitHub repository

---

**Built with ❤️ for learners everywhere**

_Transform your documents. Transform your learning. Transform your future with LearnNest._
