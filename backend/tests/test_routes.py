import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="module")
def client():
    # Menggunakan context manager 'with' untuk memicu event lifespan (startup/shutdown)
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Menguji endpoint /api/health selalu mengembalikan status 200 ok"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_faqs(client):
    """Menguji endpoint /api/faqs mengembalikan daftar FAQ"""
    response = client.get("/api/faqs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "pertanyaan_utama" in data[0]
    assert "jawaban" in data[0]

def test_chat_valid_question(client):
    """Menguji endpoint /api/chat dengan pertanyaan valid yang menghasilkan kecocokan"""
    response = client.post("/api/chat", json={"message": "Bagaimana cara mendaftar menjadi mahasiswa baru?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "score" in data
    assert "matched_question" in data
    assert data["score"] >= settings.DEFAULT_THRESHOLD
    assert "daftar" in data["matched_question"].lower()

def test_chat_empty_question(client):
    """Menguji input kosong atau whitespace mengembalikan error 422"""
    # Mencoba dengan spasi saja
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 422
    
    # Mencoba dengan string kosong
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422

def test_chat_fallback_response(client):
    """Menguji pertanyaan tidak relevan mengembalikan pesan fallback (skor di bawah threshold)"""
    response = client.post("/api/chat", json={"message": "nasi goreng bakso"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == settings.FALLBACK_ANSWER
    assert data["score"] < settings.DEFAULT_THRESHOLD

def test_chat_debug_mode(client):
    """Menguji apakah mode debug melampirkan candidates sedangkan mode non-debug menyembunyikannya"""
    # Tanpa debug param
    response = client.post("/api/chat", json={"message": "syarat KKN"})
    assert response.status_code == 200
    assert response.json()["debug_candidates"] is None

    # Dengan debug param (?debug=true)
    response = client.post("/api/chat?debug=true", json={"message": "syarat KKN"})
    assert response.status_code == 200
    data = response.json()
    assert data["debug_candidates"] is not None
    assert len(data["debug_candidates"]) > 0
    assert "question" in data["debug_candidates"][0]
    assert "score" in data["debug_candidates"][0]

def test_reload_endpoint(client):
    """Menguji reload dataset secara manual"""
    response = client.post("/api/reload")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "berhasil dimuat ulang" in data["message"]

def test_chat_conversational_fillers(client):
    """Menguji kueri dengan kata pengisi/panggilan percakapan (min, kak, dong) tidak merusak pencocokan"""
    # Kueri: "apakah ada program beasiswa min"
    response = client.post("/api/chat", json={"message": "apakah ada program beasiswa min"})
    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= settings.DEFAULT_THRESHOLD
    # Harus mencocokkan FAQ beasiswa, bukan sapaan Halo
    assert "beasiswa" in data["matched_question"].lower()
    
    # Kueri: "syarat pendaftaran dong kak"
    response = client.post("/api/chat", json={"message": "syarat pendaftaran dong kak"})
    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= settings.DEFAULT_THRESHOLD
    assert "daftar" in data["matched_question"].lower() or "persyaratan" in data["matched_question"].lower()
