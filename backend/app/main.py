import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router as api_router
from app.services.nlp_engine import FAQMatcher

# Pastikan direktori untuk logging dan data tersedia
settings.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Inisialisasi konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Mengelola siklus hidup (lifespan) aplikasi FastAPI.
    Melakukan load dataset & inisialisasi matcher saat startup.
    """
    logger.info("Memulai inisialisasi server FastAPI...")
    
    # Inisialisasi FAQMatcher dengan data CSV
    app.state.faq_matcher = FAQMatcher(
        dataset_path=str(settings.DATASET_PATH),
        threshold=settings.DEFAULT_THRESHOLD
    )
    
    yield
    logger.info("Mematikan server FastAPI...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Service untuk Chatbot FAQ Universitas (TF-IDF & Cosine Similarity)",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS Middleware agar frontend bisa mengakses API secara cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua origin untuk kebutuhan prototype/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan Router API dengan prefix /api
app.include_router(api_router, prefix=settings.API_PREFIX)
