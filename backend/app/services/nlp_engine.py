import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from app.core.config import settings

logger = logging.getLogger(__name__)

class FAQMatcher:
    """
    Wrapper/Interface untuk NLP engine (TF-IDF + Cosine Similarity).
    Untuk sementara menggunakan mock/stub berbasis keyword-overlap matching.
    
    # TODO: integrate real NLP engine from teammate (NLP & Data Engineer)
    """
    def __init__(self, dataset_path: str, threshold: float = 0.3):
        self.dataset_path = Path(dataset_path)
        self.threshold = threshold
        self.faqs: List[Dict[str, Any]] = []
        self.load_dataset()

    def load_dataset(self) -> None:
        """Membaca file CSV dataset FAQ ke memori."""
        try:
            if self.dataset_path.exists():
                df = pd.read_csv(self.dataset_path)
                # Pastikan kolom-kolom yang diperlukan ada
                required_cols = ["id", "kategori", "pertanyaan_utama", "variasi_pertanyaan", "jawaban"]
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = ""
                
                # Konversi data ke format list dict
                self.faqs = []
                for _, row in df.iterrows():
                    self.faqs.append({
                        "id": int(row["id"]) if pd.notna(row["id"]) else 0,
                        "kategori": str(row["kategori"]),
                        "pertanyaan_utama": str(row["pertanyaan_utama"]),
                        "variasi_pertanyaan": str(row["variasi_pertanyaan"]),
                        "jawaban": str(row["jawaban"])
                    })
                logger.info(f"Dataset berhasil dimuat. Total: {len(self.faqs)} FAQ.")
            else:
                logger.warning(f"File dataset tidak ditemukan di {self.dataset_path}. Menggunakan data kosong.")
                self.faqs = []
        except Exception as e:
            logger.error(f"Gagal memuat dataset: {str(e)}")
            self.faqs = []

    def reload(self) -> None:
        """Memuat ulang dataset tanpa harus me-restart server."""
        logger.info("Memulai reload dataset FAQ...")
        self.load_dataset()

    def match(self, query: str) -> Dict[str, Any]:
        """
        Mencocokkan pertanyaan pengguna terhadap dataset FAQ menggunakan
        skema keyword overlap (Mock).
        
        Mengembalikan dict yang kompatibel dengan ChatResponse schema.
        """
        if not self.faqs:
            return {
                "answer": settings.FALLBACK_ANSWER,
                "score": 0.0,
                "matched_question": "-"
            }

        # Sederhanakan query untuk pemrosesan keyword overlap
        query_cleaned = query.lower().strip()
        query_words = set(query_cleaned.split())

        candidates = []

        for faq in self.faqs:
            # Gabungkan pertanyaan utama dan variasi pertanyaan sebagai corpus pencocokan
            corpus_text = f"{faq['pertanyaan_utama']} {faq['variasi_pertanyaan']}".lower()
            corpus_words = set(corpus_text.split())

            # Hitung keyword overlap
            intersection = query_words.intersection(corpus_words)
            if query_words:
                overlap_ratio = len(intersection) / len(query_words)
            else:
                overlap_ratio = 0.0

            # Hitung skor mock similarity
            # Jika ada overlap, berikan skor proporsional antara 0.35 dan 0.95
            if overlap_ratio > 0:
                score = round(0.35 + 0.6 * overlap_ratio, 4)
                score = min(score, 0.99)
            else:
                # Nilai default rendah jika tidak ada kata yang cocok sama sekali
                score = round(0.05 + 0.1 * (len(corpus_words.intersection(set(["akademik", "kkn", "beasiswa"]))) / 10), 4)

            candidates.append({
                "question": faq["pertanyaan_utama"],
                "answer": faq["jawaban"],
                "score": score
            })

        # Urutkan kandidat berdasarkan skor tertinggi
        candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
        top_candidate = candidates[0]
        
        # Ambil top 3 kandidat untuk mode debug
        debug_candidates = [
            {"question": c["question"], "score": c["score"]} 
            for c in candidates[:3]
        ]

        # Log jika di bawah threshold (FR-8)
        if top_candidate["score"] < self.threshold:
            logger.warning(
                f"Pertanyaan di bawah threshold: '{query}' | "
                f"Kandidat terdekat: '{top_candidate['question']}' (score: {top_candidate['score']})"
            )
            return {
                "answer": settings.FALLBACK_ANSWER,
                "score": top_candidate["score"],
                "matched_question": top_candidate["question"],
                "debug_candidates": debug_candidates
            }

        return {
            "answer": top_candidate["answer"],
            "score": top_candidate["score"],
            "matched_question": top_candidate["question"],
            "debug_candidates": debug_candidates
        }
