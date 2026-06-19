from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """Skema untuk request body endpoint /api/chat"""
    message: str = Field(..., min_length=1, description="Pertanyaan bebas dari mahasiswa")

class CandidateResponse(BaseModel):
    """Skema untuk informasi kandidat kecocokan dalam mode debug"""
    question: str = Field(..., description="Pertanyaan dari dataset FAQ yang dicocokkan")
    score: float = Field(..., description="Skor cosine similarity")

class ChatResponse(BaseModel):
    """Skema untuk response body endpoint /api/chat"""
    answer: str = Field(..., description="Jawaban resmi dari FAQ atau pesan fallback")
    score: float = Field(..., description="Skor similarity tertinggi")
    matched_question: str = Field(..., description="Pertanyaan terdekat yang paling cocok")
    debug_candidates: Optional[List[CandidateResponse]] = Field(
        default=None, 
        description="Top-3 kandidat jawaban untuk kebutuhan analisis evaluasi (hanya aktif jika debug=true)"
    )

class FAQItem(BaseModel):
    """Skema untuk satu item FAQ di endpoint /api/faqs"""
    id: int = Field(..., description="ID unik entri FAQ")
    kategori: str = Field(..., description="Kategori FAQ (misal: akademik, beasiswa)")
    pertanyaan_utama: str = Field(..., description="Pertanyaan baku yang representatif")
    jawaban: str = Field(..., description="Jawaban resmi")

class HealthResponse(BaseModel):
    """Skema untuk response body endpoint /api/health"""
    status: str = Field(default="ok", description="Status server")

class ReloadResponse(BaseModel):
    """Skema untuk response body endpoint /api/reload"""
    status: str = Field(default="success", description="Status reload dataset")
    message: str = Field(..., description="Pesan penjelasan hasil reload")
