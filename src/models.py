from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)          # Günün sözü metni
    author = Column(String(100), nullable=False)  # Sözü söyleyen yazar
    category = Column(String(50), nullable=False) # Kategori (örn: motivation, philosophy)
    created_at = Column(DateTime, default=datetime.utcnow) # Eklenme tarihi
