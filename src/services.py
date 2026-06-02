from sqlalchemy.orm import Session
from src.models import Quote
import random


def get_quote_of_the_day(db: Session):
    """Veritabanındaki sözlerden rastgele birini günün sözü seçer."""
    quotes = db.query(Quote).all()
    if not quotes:
        return None
    return random.choice(quotes)


def search_quotes(db: Session, query: str):
    """Yazar ismine veya söz metnine göre filtreleme yapar."""
    return db.query(Quote).filter(
        (Quote.author.ilike(f"%{query}%")) | (Quote.text.ilike(f"%{query}%"))
    ).all()


def create_quote(db: Session, text: str, author: str, category: str):
    """Veritabanına yeni bir söz ekler."""
    db_quote = Quote(text=text, author=author, category=category)
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote


def update_quote(db: Session, quote_id: int, text: str = None, author: str = None, category: str = None):
    """Var olan bir sözü günceller."""
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote:
        if text:
            db_quote.text = text
        if author:
            db_quote.author = author
        if category:
            db_quote.category = category
        db.commit()
        db.refresh(db_quote)
    return db_quote


def delete_quote(db: Session, quote_id: int):
    """Veritabanından id'ye göre söz siler."""
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote:
        db.delete(db_quote)
        db.commit()
        return True
    return False


def get_quote_by_id(db: Session, quote_id: int):
    """Belirli bir ID'ye sahip sözü getirir."""
    return db.query(Quote).filter(Quote.id == quote_id).first()
