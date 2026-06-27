import json
import csv
from pathlib import Path

# Path konfigurasi
JSON_PATH = Path("d:/tugas Rifki/Project/NLP/chatbot-faq/faq-chatbot/faq-chatbot/dataset.json")
CSV_PATH = Path("d:/tugas Rifki/Project/NLP/chatbot-faq/backend/app/data/faqs.csv")

def convert_json_to_csv():
    # Buat direktori output jika belum ada
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    intents = data.get("intents", [])
    
    csv_rows = []
    # Kolom: id, kategori, pertanyaan_utama, variasi_pertanyaan, jawaban
    
    for idx, intent in enumerate(intents, start=1):
        kategori = intent.get("tag", "")
        patterns = [p for p in intent.get("patterns", []) if p.strip()]
        
        if not patterns:
            continue
            
        pertanyaan_utama = patterns[0]
        variasi_pertanyaan = ";".join(patterns[1:])
        
        responses = intent.get("responses", "")
        # Jika response berbentuk list, ambil elemen pertama (seperti di chatbot.py rekan)
        if isinstance(responses, list):
            jawaban = responses[0] if responses else ""
        else:
            jawaban = responses
            
        csv_rows.append({
            "id": idx,
            "kategori": kategori,
            "pertanyaan_utama": pertanyaan_utama,
            "variasi_pertanyaan": variasi_pertanyaan,
            "jawaban": jawaban
        })
        
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "kategori", "pertanyaan_utama", "variasi_pertanyaan", "jawaban"])
        writer.writeheader()
        writer.writerows(csv_rows)
        
    print(f"Berhasil mengonversi {len(csv_rows)} entri FAQ ke {CSV_PATH}")

if __name__ == "__main__":
    convert_json_to_csv()
