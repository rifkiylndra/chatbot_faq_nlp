# Frontend Chatbot FAQ Kampus

Direktori ini berisi antarmuka pengguna (UI) chatbot berbentuk halaman web interaktif.

## Deskripsi

Antarmuka ini dibangun menggunakan HTML, CSS, dan Javascript murni tanpa framework tambahan. Halaman ini menyediakan kotak chat interaktif dengan indikator mengetik (*typing indicator*), bubble chat untuk user dan bot, serta informasi kecocokan (skor & kategori) jika respons ditemukan.

## Integrasi API

Halaman web ini berkomunikasi langsung dengan FastAPI backend yang berjalan secara lokal pada port 8000:
- **Endpoint:** `POST http://localhost:8000/api/chat`
- **Request Body:** `{"message": "pertanyaan user"}`

## Cara Menjalankan

Ada dua cara utama untuk membuka frontend ini secara lokal:

### Cara 1: Menggunakan VS Code Live Server (Sangat Direkomendasikan)
1. Pasang ekstensi **Live Server** di VS Code jika belum ada.
2. Klik kanan pada file [index.html](file:///d:/tugas%20Rifki/Project/NLP/chatbot-faq/frontend/index.html) dan pilih **Open with Live Server**.
3. Browser akan membuka halaman chat pada `http://127.0.0.1:5500/frontend/index.html` (atau port serupa).

### Cara 2: Membuka Langsung di Browser
1. Buka File Explorer di komputer Anda.
2. Cari dan klik dua kali pada file [index.html](file:///d:/tugas%20Rifki/Project/NLP/chatbot-faq/frontend/index.html).
3. Halaman akan terbuka di browser default dengan protokol file (`file:///...`).
