def test_add_quote_endpoint(client):
    """POST /quotes endpoint'inin doğru çalıştığını test eder."""
    response = client.post("/quotes", params={
        "text": "Hayatta en hakiki mürşit ilimdir.",
        "author": "Mustafa Kemal Atatürk",
        "category": "philosophy"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Hayatta en hakiki mürşit ilimdir."
    assert data["author"] == "Mustafa Kemal Atatürk"


def test_get_all_quotes_endpoint(client):
    """GET /quotes endpoint'inin verileri getirdiğini test eder."""
    # Testin patlamaması için önce veritabanına bir kayıt atıyoruz
    client.post("/quotes", params={
        "text": "Test API Sözü",
        "author": "API Yazar",
        "category": "test"
    })

    response = client.get("/quotes")
    assert response.status_code == 200
    data = response.json()

    # En az 1 veri dönmeli
    assert len(data) > 0
    assert any(quote["author"] == "API Yazar" for quote in data)


def test_search_quotes_endpoint(client):
    """GET /quotes/search endpoint'inin arama yapabildiğini test eder."""
    client.post("/quotes", params={
        "text": "Spesifik Bir Arama Sözü",
        "author": "Arama Yazarı",
        "category": "test"
    })

    # 'Spesifik' kelimesini aratıyoruz
    response = client.get("/quotes/search?query=Spesifik")
    assert response.status_code == 200
    data = response.json()

    assert len(data) > 0
    assert "Spesifik Bir Arama Sözü" in data[0]["text"]
