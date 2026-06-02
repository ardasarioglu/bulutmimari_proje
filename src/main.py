from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from src.models import Base, Quote
from src import services
import os
import boto3
from fastapi.responses import HTMLResponse

app = FastAPI(title="Quote of the Day API")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quotes.db")

if DATABASE_URL.startswith("sqlite"):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(DATABASE_URL, connect_args={
                           "check_same_thread": False})
else:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- AWS S3 (LocalStack) Kurulumu ---
AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "http://localhost:4566")
BUCKET_NAME = "quote-backups"


def get_s3_client():
    """LocalStack veya gerçek AWS için S3 istemcisi üretir."""
    return boto3.client(
        "s3",
        endpoint_url=AWS_S3_ENDPOINT,
        aws_access_key_id="mock",
        aws_secret_access_key="mock",
        region_name="us-east-1"
    )


@app.get("/quotes/today")
def read_today_quote(db: Session = Depends(get_db)):
    quote = services.get_quote_of_the_day(db)
    if not quote:
        raise HTTPException(
            status_code=404, detail="Henuz veritabaninda soz yok.")

    # Şartname AWS Gereksinimi: Sözü S3'e yedekle
    try:
        s3 = get_s3_client()
        # Yerel ortamda bucket yoksa otomatik oluştur
        try:
            s3.create_bucket(Bucket=BUCKET_NAME)
        except Exception:
            pass

        backup_content = f"Author: {quote.author}\nQuote: {quote.text}"
        s3.put_object(Bucket=BUCKET_NAME,
                      Key=f"quote_{quote.id}.txt", Body=backup_content)
    except Exception as e:
        print(
            f"S3 Yedekleme hatası (Testlerde SQLite modundaysa normaldir): {e}")

    return quote


@app.get("/quotes/search")
def search_quotes(query: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    return services.search_quotes(db, query)


@app.post("/quotes", status_code=201)
def add_quote(text: str, author: str, category: str, db: Session = Depends(get_db)):
    return services.create_quote(db, text, author, category)


@app.get("/quotes")
def get_all_quotes(db: Session = Depends(get_db)):
    return db.query(Quote).all()


@app.put("/quotes/{quote_id}")
def update_quote(quote_id: int, text: str = None, author: str = None, category: str = None, db: Session = Depends(get_db)):
    quote = services.update_quote(db, quote_id, text, author, category)
    if not quote:
        raise HTTPException(status_code=404, detail="Güncellenmek istenen söz bulunamadı.")
    return quote


@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    success = services.delete_quote(db, quote_id)
    if not success:
        raise HTTPException(status_code=404, detail="Silinmek istenen söz bulunamadı.")
    return {"message": "Söz başarıyla silindi."}


@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """<!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Quote API E2E UI</title>
        <style>body { font-family: sans-serif; max-width: 600px; margin: 20px auto; }</style>
    </head>
    <body>
        <h1>Quote API Test Arayüzü</h1>

        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h2>Günün Sözü</h2>
            <button id="getQodBtn" onclick="getQod()">Getir</button>
            <p id="qodResult"></p>
        </div>

        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h2>Söz Ekle</h2>
            <input type="text" id="qText" placeholder="Söz Metni"><br><br>
            <input type="text" id="qAuthor" placeholder="Yazar"><br><br>
            <input type="text" id="qCategory" placeholder="Kategori"><br><br>
            <button id="addBtn" onclick="addQuote()">Ekle</button>
            <p id="addResult" style="color: green; font-weight: bold;"></p>
        </div>

        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h2>Arama Yap</h2>
            <input type="text" id="sQuery" placeholder="Aranacak Kelime">
            <button id="searchBtn" onclick="searchQuote()">Ara</button>
            <ul id="searchResult"></ul>
        </div>

        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h2>Söz Güncelle</h2>
            <input type="number" id="uId" placeholder="Söz ID (Zorunlu)"><br><br>
            <input type="text" id="uText" placeholder="Yeni Söz Metni (Opsiyonel)"><br><br>
            <input type="text" id="uAuthor" placeholder="Yeni Yazar (Opsiyonel)"><br><br>
            <input type="text" id="uCategory" placeholder="Yeni Kategori (Opsiyonel)"><br><br>
            <button id="updateBtn" onclick="updateQuote()">Güncelle</button>
            <p id="updateResult" style="color: blue; font-weight: bold;"></p>
        </div>

        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h2>Söz Sil</h2>
            <input type="number" id="dId" placeholder="Silinecek Söz ID">
            <button id="deleteBtn" onclick="deleteQuote()">Sil</button>
            <p id="deleteResult" style="color: red; font-weight: bold;"></p>
        </div>

        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h2>Tüm Sözler Listesi</h2>
            <button id="getAllBtn" onclick="getAllQuotes()">Tümünü Listele</button>
            <ul id="allQuotesResult" style="margin-top: 10px; padding-left: 20px;"></ul>
        </div>

        <script>
            async function getQod() {
                let res = await fetch('/quotes/today');
                if(res.ok) {
                    let data = await res.json();
                    document.getElementById('qodResult').innerText = data.text + " - " + data.author;
                } else {
                    document.getElementById('qodResult').innerText = "Henüz söz yok.";
                }
            }
            async function addQuote() {
                let t = document.getElementById('qText').value;
                let a = document.getElementById('qAuthor').value;
                let c = document.getElementById('qCategory').value;
                let res = await fetch(`/quotes?text=${encodeURIComponent(t)}&author=${encodeURIComponent(a)}&category=${encodeURIComponent(c)}`, {method: 'POST'});
                if(res.ok) {
                    document.getElementById('addResult').innerText = "Başarıyla Eklendi!";
                    getAllQuotes(); // Yeni eklenen sözü listede anlık görmek için otomatik yeniliyoruz
                }
            }
            async function searchQuote() {
                let q = document.getElementById('sQuery').value;
                let res = await fetch(`/quotes/search?query=${encodeURIComponent(q)}`);
                if(res.ok) {
                    let data = await res.json();
                    let ul = document.getElementById('searchResult');
                    ul.innerHTML = "";
                    data.forEach(d => {
                        let li = document.createElement('li');
                        li.innerText = d.text + " (" + d.author + ")";
                        ul.appendChild(li);
                    });
                }
            }
            async function updateQuote() {
                let id = document.getElementById('uId').value;
                if(!id) { alert("Güncelleme için ID numarası girmek zorundasın!"); return; }
                let t = document.getElementById('uText').value;
                let a = document.getElementById('uAuthor').value;
                let c = document.getElementById('uCategory').value;
                let params = new URLSearchParams();
                if(t) params.append('text', t);
                if(a) params.append('author', a);
                if(c) params.append('category', c);
                let res = await fetch(`/quotes/${id}?${params.toString()}`, {method: 'PUT'});
                if(res.ok) {
                    document.getElementById('updateResult').innerText = "Başarıyla Güncellendi!";
                    getAllQuotes(); // Güncellenen halini listede görmek için yeniliyoruz
                } else {
                    document.getElementById('updateResult').innerText = "Hata: Güncellenemedi.";
                }
            }
            async function deleteQuote() {
                let id = document.getElementById('dId').value;
                if(!id) { alert("Silmek için ID numarası girmek zorundasın!"); return; }
                let res = await fetch(`/quotes/${id}`, {method: 'DELETE'});
                if(res.ok) {
                    document.getElementById('deleteResult').innerText = "Başarıyla Silindi!";
                    getAllQuotes(); // Silinen sözün listeden kaybolması için yeniliyoruz
                } else {
                    document.getElementById('deleteResult').innerText = "Hata: Silinemedi.";
                }
            }
            async function getAllQuotes() {
                let res = await fetch('/quotes');
                if(res.ok) {
                    let data = await res.json();
                    let ul = document.getElementById('allQuotesResult');
                    ul.innerHTML = "";
                    if(data.length === 0) {
                        ul.innerHTML = "<li>Veritabanında henüz hiç söz yok.</li>";
                        return;
                    }
                    data.forEach(d => {
                        let li = document.createElement('li');
                        li.innerHTML = `<strong>ID:</strong> ${d.id} | <strong>Söz:</strong> "${d.text}" | <strong>Yazar:</strong> ${d.author} | <strong>Kategori:</strong> ${d.category}`;
                        ul.appendChild(li);
                    });
                } else {
                    document.getElementById('allQuotesResult').innerText = "Sözler yüklenirken bir hata oluştu.";
                }
            }
        </script>
    </body>
    </html>
    """
