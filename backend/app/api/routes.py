from fastapi import APIRouter, Request, Query, HTTPException, status
from typing import List
from app.models.schemas import (
    ChatRequest, 
    ChatResponse, 
    FAQItem, 
    HealthResponse, 
    ReloadResponse
)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest, debug: bool = Query(default=False)):
    """
    Endpoint untuk mengajukan pertanyaan ke chatbot FAQ.
    
    - **message**: Pertanyaan dari pengguna (tidak boleh kosong/whitespace).
    - **debug**: Jika true, menampilkan top-3 kandidat kecocokan beserta skornya.
    """
    # Validasi input kosong atau hanya berisi whitespace
    message = body.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pesan tidak boleh kosong atau hanya berisi spasi."
        )

    # Dapatkan matcher dari app state
    matcher = request.app.state.faq_matcher
    match_result = matcher.match(message)

    # Sembunyikan debug_candidates jika mode debug tidak diaktifkan
    if not debug:
        match_result["debug_candidates"] = None

    return match_result

@router.get("/faqs", response_model=List[FAQItem])
async def get_faqs(request: Request):
    """
    Mendapatkan seluruh daftar entri FAQ yang tersimpan di sistem.
    """
    matcher = request.app.state.faq_matcher
    return matcher.faqs

@router.post("/reload", response_model=ReloadResponse)
async def reload_faqs(request: Request):
    """
    Memuat ulang dataset dari file CSV dan memperbarui memori NLP engine tanpa restart server.
    """
    matcher = request.app.state.faq_matcher
    matcher.reload()
    return {
        "status": "success",
        "message": f"Dataset FAQ berhasil dimuat ulang. Total data saat ini: {len(matcher.faqs)} entri."
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint pengecekan kesehatan server (health check).
    """
    return {"status": "ok"}
