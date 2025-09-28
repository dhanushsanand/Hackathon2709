import PyPDF2
import pdfplumber
from typing import List
import re
from io import BytesIO

class PDFProcessor:
    def __init__(self):
        self.chunk_size = 1000  # characters per chunk
        self.overlap = 100      # character overlap between chunks
    
    async def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        text = ""
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e:
                raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return self.clean_text(text)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:()\-"]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [text]
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            if i + self.chunk_size >= len(words):
                break
        
        return chunks