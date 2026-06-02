from src import services
from tests.factories import QuoteFactory
from src.models import Quote


def test_create_quote(db_session):
    # Given
    text = "Bilgi guctur."
    author = "Bacon"
    category = "philosophy"

    # When
    quote = services.create_quote(db_session, text, author, category)

    # Then
    assert quote.id is not None
    assert quote.text == text
    assert quote.author == author


def test_get_quote_of_the_day(db_session):
    # Given
    mock_quote = QuoteFactory()
    db_session.add(mock_quote)
    db_session.commit()

    # When
    quote = services.get_quote_of_the_day(db_session)

    # Then
    assert quote is not None
    assert quote.text == mock_quote.text


def test_search_quotes(db_session):
    # Given
    q1 = QuoteFactory(text="Hayat kisa, sanat uzun.", author="Hippocrates")
    db_session.add(q1)
    db_session.commit()

    # When
    results = services.search_quotes(db_session, "Hayat")

    # Then
    assert len(results) == 1
    assert results[0].author == "Hippocrates"


def test_get_all_quotes_direct(db_session):
    """Veritabani uzerinden tum sozleri cekmeyi doğrudan test eder (Coverage yukseltir)."""
    # Given
    q = Quote(text="Muzik ruhun gidasidir.",
              author="Anonim", category="motivation")
    db_session.add(q)
    db_session.commit()

    # When
    all_quotes = db_session.query(Quote).all()

    # Then
    assert len(all_quotes) == 1
    assert all_quotes[0].author == "Anonim"


def test_services_empty_db(db_session):
    """Veritabanı bosken gunun sozu fonksiyonunun None dondugunu test eder."""
    # When
    quote = services.get_quote_of_the_day(db_session)

    # Then
    assert quote is None


def test_main_get_db_coverage():
    """main.py icindeki get_db dependency fonksiyonunu kapsar."""
    from src.main import get_db
    generator = get_db()
    try:
        db = next(generator)
        assert db is not None
    except StopIteration:
        pass


def test_main_s3_client_coverage():
    """main.py icindeki get_s3_client fonksiyonunu kapsar."""
    from src.main import get_s3_client
    s3 = get_s3_client()
    assert s3 is not None


def test_update_quote_service(db_session):
    """Var olan bir sozun guncellenmesini test eder."""
    # Given
    quote = services.create_quote(db_session, "Eski", "Yazar", "Kategori")

    # When
    updated_quote = services.update_quote(db_session, quote.id, text="Yeni Metin", author="Yeni Yazar")

    # Then
    assert updated_quote.text == "Yeni Metin"
    assert updated_quote.author == "Yeni Yazar"
    assert updated_quote.category == "Kategori"  # Degismemesi lazim


def test_delete_quote_service(db_session):
    """Var olan bir sozun silinmesini test eder."""
    # Given
    quote = services.create_quote(db_session, "Silinecek", "Yazar", "Kategori")
    quote_id = quote.id

    # When
    result = services.delete_quote(db_session, quote_id)

    # Then
    assert result is True

    # Olmayan ID'yi silmeye veya guncellemeye calisinca ne oldugunu da test et
    assert services.delete_quote(db_session, 9999) is False
    assert services.update_quote(db_session, 9999, text="Yok") is None
