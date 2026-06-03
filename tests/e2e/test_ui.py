from playwright.sync_api import sync_playwright

def test_e2e_scenarios():
    with sync_playwright() as p:
        # CI/CD pipeline'ında patlamaması için headless=True KALMAK ZORUNDA.
        # Demoda kendi gözlerinle görmek istersen geçici olarak False yapabilirsin.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Senaryo 1: Sayfanın hatasız yüklenmesi
        page.goto("http://localhost:8000/")
        assert "Quote API" in page.title()

        # Senaryo 2: Arayüzden yeni söz eklenmesi (Bu veritabanındaki ilk veri, yani ID'si 1 olacak)
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

        # Senaryo 5: Söz Güncelleme (ID = 1)
        page.fill("#uId", "1")
        page.fill("#uText", "Playwright ile güncellenmiş söz")
        page.fill("#uAuthor", "Güncel Robot")
        page.click("#updateBtn")
        page.wait_for_selector("text=Başarıyla Güncellendi!")

        # Senaryo 6: Söz Silme (ID = 1)
        page.fill("#dId", "1")
        page.click("#deleteBtn")
        page.wait_for_selector("text=Başarıyla Silindi!")

        browser.close()