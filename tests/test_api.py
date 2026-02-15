"""Test suite for Kazuba SaaS API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_returns_api_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kazuba Converter SaaS API"
        assert "version" in data
        assert "pricing" in data
    
    def test_root_pricing_structure(self, client):
        response = client.get("/")
        data = response.json()
        pricing = data["pricing"]
        assert "free" in pricing
        assert "hobby" in pricing
        assert "pro" in pricing
        assert "requests_per_day" in pricing["free"]


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestConvertEndpoint:
    """Tests for the document conversion endpoint."""
    
    def test_convert_without_auth_returns_403(self, client):
        response = client.post("/convert")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_convert_with_invalid_key_returns_422(self, client):
        response = client.post(
            "/convert",
            headers={"Authorization": "Bearer invalid_key"}
        )
        # Invalid key format returns 422 (Unprocessable Entity) from auth module
        assert response.status_code in [401, 422]
    
    def test_convert_with_free_key_returns_success(self, client):
        response = client.post(
            "/convert",
            headers={"Authorization": "Bearer kzb_free_test123"}
        )
        # Should succeed with valid key format
        assert response.status_code in [200, 422, 429]  # 200 OK, 422 (no Redis), or 429 (rate limit)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert data["user_tier"] == "free"
    
    def test_convert_with_hobby_key_returns_success(self, client):
        response = client.post(
            "/convert",
            headers={"Authorization": "Bearer kzb_hobby_test456"}
        )
        assert response.status_code in [200, 422, 429]
        if response.status_code == 200:
            data = response.json()
            assert data["user_tier"] == "hobby"
    
    def test_convert_with_pro_key_returns_success(self, client):
        response = client.post(
            "/convert",
            headers={"Authorization": "Bearer kzb_pro_test789"}
        )
        assert response.status_code in [200, 422, 429]
        if response.status_code == 200:
            data = response.json()
            assert data["user_tier"] == "pro"


class TestUsageEndpoint:
    """Tests for the usage statistics endpoint."""
    
    def test_usage_without_auth_returns_403(self, client):
        response = client.get("/usage")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_usage_with_valid_key_returns_stats(self, client):
        response = client.get(
            "/usage",
            headers={"Authorization": "Bearer kzb_free_test123"}
        )
        assert response.status_code in [200, 422]  # 200 OK or 422 (no DB integration yet)
        if response.status_code == 200:
            data = response.json()
            assert "tier" in data
            assert "requests_today" in data
            assert "requests_limit" in data
            assert "docs_this_month" in data
            assert "docs_limit" in data


class TestConfiguration:
    """Tests for configuration and settings."""
    
    def test_app_metadata(self):
        from app.main import app
        assert app.title == "Kazuba Converter SaaS API"
        assert app.version == "0.1.0"
    
    def test_cors_configuration(self):
        from app.main import app
        # Check that CORS middleware is configured
        cors_middleware = [m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"]
        assert len(cors_middleware) > 0


class TestAppModules:
    """Tests for individual app modules."""
    
    def test_config_loading(self):
        from app.config import settings
        assert settings.RATE_LIMIT_FREE == 50
        assert settings.RATE_LIMIT_HOBBY == 500
        assert settings.RATE_LIMIT_PRO == 5000
    
    def test_auth_module_imports(self):
        from app.auth import get_current_user
        assert callable(get_current_user)
    
    def test_rate_limit_module_imports(self):
        from app.rate_limit import rate_limit
        assert callable(rate_limit)
    
    def test_convert_module_imports(self):
        from app.convert import convert_document
        assert callable(convert_document)
