from src import services
from tests.factories import QuoteFactory

def test_create_quote(db_session):
    # Given (Kurulum / Girdi)
    text = "Bilgi guctur."
    author = "Bacon"
    category = "philosophy"

    # When (Eylem / Fonksiyonun calismasi)
    quote = services.create_quote(db_session, text, author, category)

    # Then (Dogrulama / Kontrol)
    assert quote.id is not None
    assert quote.text == text
    assert quote.author == author

def test_get_quote_of_the_day(db_session):
    # Given: Fabrikamiz vasitasiyla sahte bir soz uretip gecici DB'ye kaydedelim
    mock_quote = QuoteFactory()
    db_session.add(mock_quote)
    db_session.commit()

    # When: Gunun sozunu cekme fonksiyonunu tetikleyelim
    quote = services.get_quote_of_the_day(db_session)

    # Then: Gelen soz bos olmamali ve ekledigimiz sozun metniyle eslesmeli
    assert quote is not None
    assert quote.text == mock_quote.text

def test_search_quotes(db_session):
    # Given: Arama algoritmasini test etmek icin spesifik bir soz ekleyelim
    q1 = QuoteFactory(text="Hayat kisa, sanat uzun.", author="Hippocrates")
    db_session.add(q1)
    db_session.commit()

    # When: "Hayat" kelimesini aratalim
    results = services.search_quotes(db_session, "Hayat")

    # Then: Sonuc listesinde 1 eleman olmali ve yazari Hippocrates olmali
    assert len(results) == 1
    assert results[0].author == "Hippocrates"
