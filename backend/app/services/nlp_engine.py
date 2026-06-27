import logging
import re
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    _stemmer = StemmerFactory().create_stemmer()
    STEMMING_AVAILABLE = True
except ImportError:
    _stemmer = None
    STEMMING_AVAILABLE = False
    logger.warning("Sastrawi tidak terinstal. Stemming dinonaktifkan.")

STOPWORDS = set(
    """
    yang untuk pada ke para namun menurut antara dia dua ia seperti jika
    sehingga kembali dan tidak ini karena kepada oleh saat harus sementara
    setelah belum kemudian sekitar guna kenapa keduanya itu kapan ada apa
    di dari adalah dengan akan bisa atau juga saya kamu kita mereka aku
    anda mau ya gak nggak deh sih kok nih bagaimana gimana banget
    cara berapa apakah adakah tersebut yaitu sebagai sebuah suatu hal
    min mimin admin kak kakak dong
    """.split()
)

def preprocess(text: str) -> str:
    """Bersihkan teks: lowercase, hapus simbol/angka, hapus stopword, lalu stem."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    if STEMMING_AVAILABLE:
        tokens = [_stemmer.stem(t) for t in tokens]
    return " ".join(tokens)

class FAQMatcher:
    """
    Wrapper/Interface untuk NLP engine (TF-IDF + Cosine Similarity).
    Sudah diintegrasikan dengan modul preprocessing dari rekan tim.
    """
    def __init__(self, dataset_path: str, threshold: float = 0.25):
        self.dataset_path = Path(dataset_path)
        self.threshold = threshold
        self.faqs: List[Dict[str, Any]] = []
        
        self.variant_texts: List[str] = []
        self.variant_faq_index: List[int] = []
        
        self.vectorizer = None
        self.tfidf_matrix = None
        
        self.load_dataset()

    def load_dataset(self) -> None:
        """Membaca file CSV dataset FAQ dan mem-fit model TF-IDF."""
        try:
            if self.dataset_path.exists():
                df = pd.read_csv(self.dataset_path)
                required_cols = ["id", "kategori", "pertanyaan_utama", "variasi_pertanyaan", "jawaban"]
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = ""
                
                self.faqs = []
                self.variant_texts = []
                self.variant_faq_index = []
                
                for idx, row in df.iterrows():
                    faq_data = {
                        "id": int(row["id"]) if pd.notna(row["id"]) and str(row["id"]).isdigit() else idx,
                        "kategori": str(row["kategori"]) if pd.notna(row["kategori"]) else "",
                        "pertanyaan_utama": str(row["pertanyaan_utama"]) if pd.notna(row["pertanyaan_utama"]) else "",
                        "variasi_pertanyaan": str(row["variasi_pertanyaan"]) if pd.notna(row["variasi_pertanyaan"]) else "",
                        "jawaban": str(row["jawaban"]) if pd.notna(row["jawaban"]) else ""
                    }
                    self.faqs.append(faq_data)
                    
                    # Bangun varian pertanyaan
                    semua_pertanyaan = [faq_data["pertanyaan_utama"]]
                    if faq_data["variasi_pertanyaan"]:
                        semua_pertanyaan.extend([p.strip() for p in faq_data["variasi_pertanyaan"].split(";") if p.strip()])
                        
                    for q in semua_pertanyaan:
                        self.variant_texts.append(preprocess(q))
                        self.variant_faq_index.append(idx)
                        
                logger.info(f"Dataset berhasil dimuat. Total FAQ: {len(self.faqs)}. Total Varian: {len(self.variant_texts)}.")
                
                if self.variant_texts:
                    self.vectorizer = TfidfVectorizer()
                    self.tfidf_matrix = self.vectorizer.fit_transform(self.variant_texts)
                    logger.info("TF-IDF Vectorizer berhasil di-fit.")
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
        Mencocokkan pertanyaan pengguna terhadap dataset FAQ menggunakan TF-IDF.
        """
        if not self.faqs or self.vectorizer is None or self.tfidf_matrix is None:
            return {
                "answer": settings.FALLBACK_ANSWER,
                "score": 0.0,
                "matched_question": "-",
                "debug_candidates": None
            }

        clean_query = preprocess(query)
        if not clean_query.strip():
            return {
                "answer": "Pertanyaannya belum saya tangkap. Coba tulis ulang dengan kata lain ya.",
                "score": 0.0,
                "matched_question": "-",
                "debug_candidates": None
            }

        query_vec = self.vectorizer.transform([clean_query])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Cari skor tertinggi untuk masing-masing parent FAQ
        faq_max_scores = {}
        for var_idx, score in enumerate(sims):
            faq_idx = self.variant_faq_index[var_idx]
            if faq_idx not in faq_max_scores or score > faq_max_scores[faq_idx]:
                faq_max_scores[faq_idx] = score
                
        # Urutkan FAQ berdasarkan skor tertinggi
        sorted_faqs = sorted(faq_max_scores.items(), key=lambda item: item[1], reverse=True)
        
        if not sorted_faqs:
            return {
                "answer": settings.FALLBACK_ANSWER,
                "score": 0.0,
                "matched_question": "-",
                "debug_candidates": None
            }
            
        best_idx, best_score = sorted_faqs[0]
        top_candidate_faq = self.faqs[best_idx]
        
        # Ambil top 3 kandidat untuk mode debug
        debug_candidates = []
        for faq_idx, score in sorted_faqs[:3]:
            debug_candidates.append({
                "question": self.faqs[faq_idx]["pertanyaan_utama"],
                "score": round(float(score), 4)
            })

        if best_score < self.threshold:
            logger.warning(
                f"Pertanyaan di bawah threshold: '{query}' | "
                f"Kandidat terdekat: '{top_candidate_faq['pertanyaan_utama']}' (score: {best_score:.4f})"
            )
            return {
                "answer": settings.FALLBACK_ANSWER,
                "score": round(float(best_score), 4),
                "matched_question": top_candidate_faq["pertanyaan_utama"],
                "debug_candidates": debug_candidates
            }

        return {
            "answer": top_candidate_faq["jawaban"],
            "score": round(float(best_score), 4),
            "matched_question": top_candidate_faq["pertanyaan_utama"],
            "debug_candidates": debug_candidates
        }
