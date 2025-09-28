# main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from config import settings
from routers import auth, pdf, quiz, user, test, notes
from middleware.auth import verify_firebase_token

app = FastAPI(title="PDF Quiz System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(notes.router, prefix="/notes", tags=["study-notes"])
app.include_router(test.router, prefix="/test", tags=["testing"])

@app.get("/")
async def root():
    return {"message": "PDF Quiz System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
