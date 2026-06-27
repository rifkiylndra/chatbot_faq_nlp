import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

    _stemmer = StemmerFactory().create_stemmer()
    STEMMING_AVAILABLE = True
except ImportError:
    _stemmer = None
    STEMMING_AVAILABLE = False

STOPWORDS = set(
    """
    yang untuk pada ke para namun menurut antara dia dua ia seperti jika
    sehingga kembali dan tidak ini karena kepada oleh saat harus sementara
    setelah belum kemudian sekitar guna kenapa keduanya itu kapan ada apa
    di dari adalah dengan akan bisa atau juga saya kamu kita mereka aku
    anda mau ya gak nggak deh sih kok nih bagaimana gimana banget
    cara berapa apakah adakah tersebut yaitu sebagai sebuah suatu hal
    """.split()
)


def preprocess(text: str) -> str:
    """Bersihkan teks: lowercase, hapus simbol/angka, hapus stopword, lalu stem."""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    if STEMMING_AVAILABLE:
        tokens = [_stemmer.stem(t) for t in tokens]
    return " ".join(tokens)


class FAQChatbot:
    def __init__(self, faq_path: str, threshold: float = 0.25):
        self.faq_path = Path(faq_path)
        self.threshold = threshold
        self.faqs = []
        self.variant_texts = []       
        self.variant_faq_index = []   
        self.vectorizer = None
        self.tfidf_matrix = None
        self._load_and_fit()

    @staticmethod
    def _normalize(raw):
        if isinstance(raw, dict) and "intents" in raw:
            faqs = []
            for idx, intent in enumerate(raw["intents"]):
                patterns = [p for p in intent.get("patterns", []) if p and p.strip()]
                if not patterns:
                    continue
                responses = intent.get("responses", "")
                answer = responses[0] if isinstance(responses, list) else responses
                faqs.append({
                    "id": idx + 1,
                    "category": intent.get("tag", ""),
                    "question": patterns[0],
                    "alt_questions": patterns[1:],
                    "answer": answer,
                })
            return faqs
        return raw

    def _load_and_fit(self):
        with open(self.faq_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.faqs = self._normalize(raw)

        self.variant_texts = []
        self.variant_faq_index = []

        for idx, faq in enumerate(self.faqs):
            semua_pertanyaan = [faq["question"]] + faq.get("alt_questions", [])
            for q in semua_pertanyaan:
                self.variant_texts.append(preprocess(q))
                self.variant_faq_index.append(idx)

        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.variant_texts)

    def reload(self):
        self._load_and_fit()

    def ask(self, user_question: str) -> dict:
        clean = preprocess(user_question)

        if not clean.strip():
            return {
                "answer": "Pertanyaannya belum saya tangkap. Coba tulis ulang dengan kata lain ya.",
                "matched_question": None,
                "category": None,
                "score": 0.0,
            }

        query_vec = self.vectorizer.transform([clean])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])

        if best_score < self.threshold:
            return {
                "answer": (
                    "Maaf, saya belum punya jawaban untuk pertanyaan itu. "
                    "Coba pakai kata kunci lain, atau hubungi admin di [kontak-admin]."
                ),
                "matched_question": None,
                "category": None,
                "score": round(best_score, 3),
            }

        faq_idx = self.variant_faq_index[best_idx]
        faq = self.faqs[faq_idx]
        return {
            "answer": faq["answer"],
            "matched_question": faq["question"],
            "category": faq.get("category"),
            "score": round(best_score, 3),
        }


if __name__ == "__main__":
    bot = FAQChatbot("faq_data.json")
    print(f"Stemming Sastrawi aktif: {STEMMING_AVAILABLE}")
    print(f"Total varian pertanyaan ter-index: {len(bot.variant_texts)}\n")

    contoh_pertanyaan = [
        "gimana sih cara daftar jadi mahasiswa baru",
        "berapa ukt semester ini",
        "wifi kampus namanya apa",
        "cara pesan ojek online",  
    ]
    for q in contoh_pertanyaan:
        hasil = bot.ask(q)
        print(f"Q: {q}")
        print(f"   -> skor={hasil['score']} | kategori={hasil['category']}")
        print(f"   -> {hasil['answer']}\n")
