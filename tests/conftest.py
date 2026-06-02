import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from src.models import Base
from src.main import app, get_db

# Testcontainers'ı tüm test oturumu boyunca 1 kez ayağa kaldırmak için scope="session" yapıyoruz
@pytest.fixture(scope="session", name="postgres_container")
def fixture_postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest.fixture(name="db_session")
def fixture_db_session(postgres_container):
    """Testler icin Testcontainers ile gecici bir PostgreSQL DB olusturur."""
    # Container'ın oluşturduğu rastgele portlu bağlantı URL'sini al
    db_url = postgres_container.get_connection_url()
    engine = create_engine(db_url)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def fixture_client(db_session):
    """FastAPI test istemcisi saglar ve gercek DB bagimliligini test DB'si ile degistirir."""
    from fastapi.testclient import TestClient
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()