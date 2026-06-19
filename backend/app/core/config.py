import os
from pathlib import Path

# Base Directory of the app folder
APP_DIR = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "Chatbot FAQ Universitas"
    API_PREFIX: str = "/api"
    
    # Path dataset FAQ
    DATASET_PATH: Path = APP_DIR / "data" / "faqs.csv"
    
    # Threshold default untuk Cosine Similarity
    DEFAULT_THRESHOLD: float = 0.3
    
    # Jawaban fallback jika score di bawah threshold
    FALLBACK_ANSWER: str = "Maaf, pertanyaan tidak ditemukan dalam basis FAQ kami."
    
    # Logging configuration
    LOG_FILE_PATH: Path = APP_DIR / "logs" / "chatbot_fallback.log"

settings = Settings()
