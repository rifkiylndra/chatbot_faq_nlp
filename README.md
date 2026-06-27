# Chatbot FAQ Universitas (TF-IDF & Cosine Similarity)

Proyek ini adalah prototipe / demo Chatbot FAQ Universitas berbasis pendekatan **TF-IDF** (Term Frequency-Inverse Document Frequency) dan **Cosine Similarity** untuk pencocokan teks Bahasa Indonesia. Proyek ini dibangun sebagai Tugas Akhir mata kuliah Natural Language Processing (NLP).

## Struktur Repositori

Repositori ini menggunakan arsitektur multi-komponen untuk mempermudah kolaborasi tim:
- `backend/` : Berisi kode sumber untuk API server menggunakan FastAPI.
- `frontend/` : Berisi antarmuka pengguna (UI) chat berbasis web murni.
- `legacy/` : Berisi kode prototipe Flask lama yang diarsipkan untuk referensi tim.
- `AGENTS.md` : Panduan kerja dan deskripsi tugas masing-masing role (NLP, Backend, Frontend).
- `PRD_Chatbot_FAQ_Universitas.md` : Product Requirements Document lengkap dari proyek ini.

## Pembagian Branch Tim

Untuk menghindari konflik saat pengembangan paralel, setiap anggota tim bekerja pada branch masing-masing sebelum digabungkan (merge) ke branch `main`:
1. **Branch `main`** : Berisi skeleton proyek awal dan integrasi akhir yang sudah stabil.
2. **Branch `feature/nlp-engine`** : Digunakan oleh **NLP & Data Engineer** untuk mengembangkan modul TF-IDF, preprocessing (Sastrawi), dan kurasi data (file `faqs.csv`).
3. **Branch `feature/frontend`** : Digunakan oleh **Frontend & Dokumentasi** untuk mengembangkan antarmuka web chat dan menyusun laporan.

## Cara Menjalankan Backend Secara Lokal

1. Masuk ke direktori backend: `cd backend`
2. Buat dan aktifkan virtual environment: 
   - Windows: `python -m venv venv` lalu `.\venv\Scripts\activate`
   - Linux/Mac: `python3 -m venv venv` lalu `source venv/bin/activate`
3. Instal dependensi: `pip install -r requirements.txt`
4. Jalankan server: `uvicorn app.main:app --reload --port 8000`
5. Buka dokumentasi API (Swagger) di: `http://localhost:8000/docs`
