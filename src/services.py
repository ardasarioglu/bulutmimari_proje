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
