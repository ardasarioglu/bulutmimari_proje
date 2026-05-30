from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from src.models import Base, Quote
from src import services
import os
import boto3

app = FastAPI(title="Quote of the Day API")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quotes.db")

if DATABASE_URL.startswith("sqlite"):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
        raise HTTPException(status_code=404, detail="Henuz veritabaninda soz yok.")
    
    # Şartname AWS Gereksinimi: Sözü S3'e yedekle
    try:
        s3 = get_s3_client()
        # Yerel ortamda bucket yoksa otomatik oluştur
        try:
            s3.create_bucket(Bucket=BUCKET_NAME)
        except:
            pass
        
        backup_content = f"Author: {quote.author}\nQuote: {quote.text}"
        s3.put_object(Bucket=BUCKET_NAME, Key=f"quote_{quote.id}.txt", Body=backup_content)
    except Exception as e:
        print(f"S3 Yedekleme hatası (Testlerde SQLite modundaysa normaldir): {e}")

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
