from playwright.sync_api import sync_playwright


def test_e2e_scenarios():
    with sync_playwright() as p:
        # headless=True yaparsan tarayıcıyı arkaplanda gizli çalıştırır. CI/CD'de bu True olmalı.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Senaryo 1: Sayfanın hatasız yüklenmesi
        page.goto("http://localhost:8000/")
        assert "Quote API" in page.title()

        # Senaryo 2: Arayüzden yeni söz eklenmesi
        page.fill("#qText", "Playwright ile otomatik test sözü")
        page.fill("#qAuthor", "Test Robotu")
        page.fill("#qCategory", "automation")
        page.click("#addBtn")
        # Eklendi mesajının çıkmasını bekle
        page.wait_for_selector("text=Başarıyla Eklendi!")

        # Senaryo 3: Eklenen sözün arama bölümünde bulunması
        page.fill("#sQuery", "Playwright")
        page.click("#searchBtn")
        page.wait_for_selector("#searchResult li")
        sonuclar = page.inner_text("#searchResult")
        assert "Playwright ile otomatik" in sonuclar

        # Senaryo 4: Veritabanında artık söz olduğu için günün sözünün boş dönmemesi
        page.click("#getQodBtn")
        page.wait_for_selector("#qodResult")
        qod_text = page.inner_text("#qodResult")
        assert len(qod_text) > 5

        browser.close()
