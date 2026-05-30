# --- Aşama 1: Builder (Geliştirme ve Bağımlılık Derleme) ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Aşama 2: Runner (Hafif Canlı Ortam İmajı) ---
FROM python:3.11-slim AS runner

WORKDIR /app

# Sadece builder aşamasında yüklenen kütüphaneleri kopyala (Boyutu küçültür)
COPY --from=builder /root/.local /root/.local
COPY ./src ./src

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
