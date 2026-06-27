# Chatbot FAQ Kampus (TF-IDF)

Prototipe chatbot FAQ yang mencocokkan pertanyaan mahasiswa dengan basis data
FAQ menggunakan TF-IDF + cosine similarity. Tidak butuh API berbayar atau koneksi
internet ke layanan AI eksternal — semua perhitungan jalan di server sendiri.

## Struktur folder

```
faq-chatbot/
├── app.py              # Server Flask + endpoint API
├── chatbot.py          # Mesin TF-IDF (praproses teks, pencocokan, skor)
├── faq_data.json       # Basis data FAQ — EDIT INI dengan info kampusmu
├── requirements.txt
├── templates/
│   └── index.html      # Tampilan chat (HTML/CSS/JS, tanpa dependency eksternal)
└── README.md
```

## Cara menjalankan

```bash
pip install -r requirements.txt
python app.py
```

Buka `http://localhost:5000` di browser. Cek juga `python chatbot.py` untuk
tes cepat mesin pencocokan dari terminal, tanpa perlu Flask.

## Mengedit isi FAQ

Edit `faq_data.json`. Tiap entri punya bentuk:

```json
{
  "id": 1,
  "category": "Pendaftaran",
  "question": "Bagaimana cara mendaftar sebagai mahasiswa baru?",
  "alt_questions": ["cara daftar mahasiswa baru", "syarat pendaftaran"],
  "answer": "..."
}
```

`alt_questions` penting — isi sebanyak mungkin variasi cara mahasiswa biasa
bertanya hal yang sama. Makin banyak variasi yang di-index, makin akurat
pencocokannya, karena TF-IDF cuma mengenali kata yang pernah dilihat saat
training (`fit`).

Setelah edit, panggil ulang model dengan salah satu cara:
- Restart `python app.py`, atau
- `curl -X POST http://localhost:5000/api/reload` (tanpa restart server)

## Tuning threshold

Di `app.py`, baris `FAQChatbot("faq_data.json", threshold=0.25)`. Skor
cosine similarity berkisar 0–1.

- Threshold terlalu rendah → bot kadang menjawab dengan FAQ yang tidak relevan.
- Threshold terlalu tinggi → bot terlalu sering bilang "tidak tahu" walau
  pertanyaannya sebenarnya cocok.

Mulai dari 0.25–0.35, lalu sesuaikan berdasarkan hasil uji coba pertanyaan asli.

## Catatan penting soal TF-IDF + teks pendek

Saat menguji kode ini, ditemukan kasus: pertanyaan di luar topik FAQ ("cara
pesan ojek online") sempat salah cocok ke FAQ "cuti akademik" dengan skor 0.45 —
ternyata cuma karena kata "cara" (kata umum yang muncul di banyak pertanyaan
FAQ). Karena pertanyaan FAQ biasanya pendek (3–6 kata), satu kata umum yang
kebetulan sama saja bisa mendongkrak skor similarity secara tidak proporsional.

Sudah diperbaiki di `chatbot.py` dengan menambah kata seperti "cara", "berapa",
"apakah" ke daftar stopword (`STOPWORDS`), karena kata-kata itu adalah pola
tanya yang generik dan tidak membedakan topik. Kalau nanti menambah FAQ baru
dan menemukan kasus serupa (skor tinggi tapi jawabannya salah), cek dulu kata
apa yang menyebabkan kecocokan itu (lihat fungsi `preprocess`), lalu
pertimbangkan menambahkannya ke `STOPWORDS` atau menambah `alt_questions`
yang lebih spesifik.

## Deploy ke web server

Untuk prototype/demo, `python app.py` (server development Flask) sudah cukup.
Untuk yang lebih tahan lama, jalankan dengan WSGI server seperti Gunicorn:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Lalu arahkan reverse proxy (Nginx/Apache) kampus ke port tersebut.

## Upgrade lanjutan (opsional)

Kalau nanti butuh jawaban yang lebih natural/luwes (bukan cuma jawaban FAQ
yang baku), TF-IDF bisa dipakai sebagai langkah *retrieval* (cari FAQ paling
relevan), lalu hasilnya dirangkai ulang oleh model AI seperti Claude API
supaya bahasanya lebih natural. Itu pendekatan hybrid/RAG sederhana — tapi
untuk prototype ini, TF-IDF murni sudah cukup jalan tanpa biaya API.
