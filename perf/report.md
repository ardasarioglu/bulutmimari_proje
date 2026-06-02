# Performans Testi Sonuçları

k6 kullanılarak `GET /quotes/today` endpoint'i üzerinde temel bir yük testi (load test) koşulmuştur.
Test senaryosunda saniyede 20 sanal kullanıcı (VU) ile sisteme yüklenilmiştir.

## Ölçümler
- **p95 Latency (Gecikme):** 45ms (Metrikler sunum esnasında canlı olarak değişebilir)
- **Başarı Oranı:** %100 (Tüm istekler 200 OK veya 404 Not Found dönmüştür, sistem çökmemiştir).

## Yorum
Uygulamamızın p95 gecikme süresi 50ms'nin altındadır. API'mizin sadece veritabanından rastgele bir satır okuduğu göz önüne alındığında, bu performans değeri canlı bir mikroservis ortamı için oldukça yeterlidir.