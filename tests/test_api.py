"""Comprehensive test suite for Kazuba SaaS API — Production-Ready."""

import pytest
import io
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.config import settings


# Setup test database (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite://"

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


@pytest.fixture
def mock_redis():
    """Mock Redis for rate limiting tests."""
    with patch('app.rate_limit.redis_client') as mock:
        with patch('app.rate_limit.redis_available', True):
            yield mock


@pytest.fixture
def free_auth_header():
    return {"Authorization": "Bearer kzb_free_test123"}


@pytest.fixture
def hobby_auth_header():
    return {"Authorization": "Bearer kzb_hobby_test456"}


@pytest.fixture
def pro_auth_header():
    return {"Authorization": "Bearer kzb_pro_test789"}


# =============================================================================
# ROOT ENDPOINT
# =============================================================================

class TestRootEndpoint:
    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_pricing_all_tiers(self, client):
        response = client.get("/")
        # It may return landing page HTML or JSON
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "pricing" in data
            assert "free" in data["pricing"]
            assert "hobby" in data["pricing"]
            assert "pro" in data["pricing"]


# =============================================================================
# HEALTH ENDPOINT
# =============================================================================

class TestHealthEndpoint:
    def test_health_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_version(self, client):
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "0.1.0"


# =============================================================================
# FORMATS ENDPOINT (new)
# =============================================================================

class TestFormatsEndpoint:
    def test_formats_returns_200(self, client):
        response = client.get("/formats")
        assert response.status_code == 200
        data = response.json()
        assert "input_formats" in data
        assert "output_formats" in data

    def test_formats_input_types(self, client):
        response = client.get("/formats")
        data = response.json()
        extensions = [f["extension"] for f in data["input_formats"]]
        assert ".pdf" in extensions
        assert ".docx" in extensions
        assert ".txt" in extensions
        assert ".md" in extensions

    def test_formats_output_types(self, client):
        response = client.get("/formats")
        data = response.json()
        formats = [f["format"] for f in data["output_formats"]]
        assert "markdown" in formats
        assert "text" in formats


# =============================================================================
# AUTH MODULE
# =============================================================================

class TestAuthModule:
    def test_free_key_returns_free_user(self):
        from app.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials

        creds = HTTPAuthorizationCredentials(credentials="kzb_free_test", scheme="Bearer")
        user = get_current_user(credentials=creds, db=Mock())
        assert user["tier"] == "free"
        assert user["requests_limit"] == 50

    def test_hobby_key_returns_hobby_user(self):
        from app.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials

        creds = HTTPAuthorizationCredentials(credentials="kzb_hobby_test", scheme="Bearer")
        user = get_current_user(credentials=creds, db=Mock())
        assert user["tier"] == "hobby"
        assert user["requests_limit"] == 500

    def test_pro_key_returns_pro_user(self):
        from app.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials

        creds = HTTPAuthorizationCredentials(credentials="kzb_pro_test", scheme="Bearer")
        user = get_current_user(credentials=creds, db=Mock())
        assert user["tier"] == "pro"
        assert user["requests_limit"] == 5000

    def test_invalid_key_raises_401(self):
        from app.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException

        creds = HTTPAuthorizationCredentials(credentials="invalid", scheme="Bearer")
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=creds, db=Mock())
        assert exc_info.value.status_code == 401


# =============================================================================
# RATE LIMIT MODULE
# =============================================================================

class TestRateLimitModule:
    def test_rate_limit_none_user(self):
        from app.rate_limit import rate_limit
        result = rate_limit(None)
        assert result is None

    def test_rate_limit_first_request(self, mock_redis):
        from app.rate_limit import rate_limit

        mock_redis.get.return_value = None
        pipe = Mock()
        pipe.incr.return_value = None
        pipe.expire.return_value = None
        pipe.execute.return_value = [1, True]
        mock_redis.pipeline.return_value = pipe

        user = {"id": "u1", "tier": "free", "requests_limit": 50}
        rate_limit(user)
        assert user["requests_today"] == 1
        assert user["requests_remaining"] == 49

    def test_rate_limit_exceeded(self, mock_redis):
        from app.rate_limit import rate_limit
        from fastapi import HTTPException

        mock_redis.get.return_value = "50"
        user = {"id": "u1", "tier": "free", "requests_limit": 50}
        with pytest.raises(HTTPException) as exc_info:
            rate_limit(user)
        assert exc_info.value.status_code == 429


# =============================================================================
# CONVERT MODULE (unit tests)
# =============================================================================

class TestConvertModule:
    @pytest.mark.asyncio
    async def test_convert_txt_file(self):
        from app.convert import convert_document

        mock_file = AsyncMock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"Hello, World!"

        result = await convert_document(mock_file)
        assert result["status"] == "converted"
        assert result["filename"] == "test.txt"
        assert result["file_type"] == "txt"
        assert "Hello, World!" in result["content"]

    @pytest.mark.asyncio
    async def test_convert_md_file(self):
        from app.convert import convert_document

        mock_file = AsyncMock()
        mock_file.filename = "test.md"
        mock_file.content_type = "text/markdown"
        mock_file.read.return_value = b"# Title\n\nParagraph"

        result = await convert_document(mock_file)
        assert result["status"] == "converted"
        assert result["file_type"] == "md"
        assert "# Title" in result["content"]

    @pytest.mark.asyncio
    async def test_convert_unsupported_type_raises_400(self):
        from app.convert import convert_document
        from fastapi import HTTPException

        mock_file = AsyncMock()
        mock_file.filename = "test.exe"
        mock_file.content_type = "application/x-msdownload"
        mock_file.read.return_value = b"binary"

        with pytest.raises(HTTPException) as exc_info:
            await convert_document(mock_file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_convert_empty_file_raises_400(self):
        from app.convert import convert_document
        from fastapi import HTTPException

        mock_file = AsyncMock()
        mock_file.filename = "empty.txt"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b""

        with pytest.raises(HTTPException) as exc_info:
            await convert_document(mock_file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_convert_text_output_format(self):
        from app.convert import convert_document

        mock_file = AsyncMock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"Raw text content"

        result = await convert_document(mock_file, output_format="text")
        assert result["output_format"] == "text"
        assert result["content"] == "Raw text content"

    @pytest.mark.asyncio
    async def test_convert_invalid_output_format(self):
        from app.convert import convert_document
        from fastapi import HTTPException

        mock_file = AsyncMock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"content"

        with pytest.raises(HTTPException) as exc_info:
            await convert_document(mock_file, output_format="html")
        assert exc_info.value.status_code == 400


# =============================================================================
# CONVERT ENDPOINT (integration)
# =============================================================================

class TestConvertEndpoint:
    def test_convert_no_auth_returns_403(self, client):
        response = client.post("/convert")
        assert response.status_code == 403

    def test_convert_invalid_key_returns_401(self, client):
        response = client.post(
            "/convert",
            headers={"Authorization": "Bearer invalid_key"},
            files={"file": ("test.txt", b"hello", "text/plain")}
        )
        assert response.status_code == 401

    def test_convert_txt_file_success(self, client, mock_redis, free_auth_header):
        mock_redis.get.return_value = None
        pipe = Mock()
        pipe.incr.return_value = None
        pipe.expire.return_value = None
        pipe.execute.return_value = [1, True]
        mock_redis.pipeline.return_value = pipe

        response = client.post(
            "/convert",
            headers=free_auth_header,
            files={"file": ("test.txt", b"Hello World", "text/plain")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "converted"
        assert data["filename"] == "test.txt"
        assert data["user_tier"] == "free"
        assert "Hello World" in data["content"]

    def test_convert_md_file_success(self, client, mock_redis, hobby_auth_header):
        mock_redis.get.return_value = None
        pipe = Mock()
        pipe.incr.return_value = None
        pipe.expire.return_value = None
        pipe.execute.return_value = [1, True]
        mock_redis.pipeline.return_value = pipe

        response = client.post(
            "/convert",
            headers=hobby_auth_header,
            files={"file": ("readme.md", b"# Title\nContent", "text/markdown")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "converted"
        assert data["user_tier"] == "hobby"

    def test_convert_rate_limited(self, client, mock_redis, free_auth_header):
        mock_redis.get.return_value = "50"

        response = client.post(
            "/convert",
            headers=free_auth_header,
            files={"file": ("test.txt", b"hello", "text/plain")}
        )
        assert response.status_code == 429


# =============================================================================
# USAGE ENDPOINT
# =============================================================================

class TestUsageEndpoint:
    def test_usage_no_auth_returns_403(self, client):
        response = client.get("/usage")
        assert response.status_code == 403

    def test_usage_with_free_key(self, client, free_auth_header):
        response = client.get("/usage", headers=free_auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "free"
        assert data["requests_limit"] == 50
        assert data["docs_limit"] == 100

    def test_usage_with_pro_key(self, client, pro_auth_header):
        response = client.get("/usage", headers=pro_auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "pro"
        assert data["requests_limit"] == 5000


# =============================================================================
# STRIPE ROUTES
# =============================================================================

class TestStripeRoutes:
    def test_stripe_config_returns_200(self, client):
        response = client.get("/stripe/config")
        assert response.status_code == 200
        data = response.json()
        assert "prices" in data

    def test_checkout_without_stripe_returns_503(self, client):
        response = client.post("/stripe/create-checkout-session?tier=hobby")
        assert response.status_code == 503

    def test_webhook_without_config_returns_ok(self, client):
        response = client.post(
            "/stripe/webhook",
            content=b'{"type": "test"}',
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"


# =============================================================================
# MODELS
# =============================================================================

class TestModels:
    def test_user_tier_enum(self):
        from models import UserTier
        assert UserTier.FREE == "free"
        assert UserTier.HOBBY == "hobby"
        assert UserTier.PRO == "pro"
        assert UserTier.ENTERPRISE == "enterprise"

    def test_user_model_columns(self):
        from models import User
        assert User.__tablename__ == "users"
        assert hasattr(User, 'email')
        assert hasattr(User, 'tier')
        assert hasattr(User, 'stripe_customer_id')

    def test_api_key_model_columns(self):
        from models import ApiKey
        assert ApiKey.__tablename__ == "api_keys"
        assert hasattr(ApiKey, 'key_hash')
        assert hasattr(ApiKey, 'user_id')

    def test_usage_log_model_columns(self):
        from models import UsageLog
        assert UsageLog.__tablename__ == "usage_logs"
        assert hasattr(UsageLog, 'endpoint')
        assert hasattr(UsageLog, 'status_code')


# =============================================================================
# DATABASE MODULE
# =============================================================================

class TestDatabaseModule:
    def test_get_db_yields_session(self):
        from app.database import get_db
        gen = get_db()
        db = next(gen)
        assert db is not None
        try:
            next(gen)
        except StopIteration:
            pass


# =============================================================================
# CONFIG MODULE
# =============================================================================

class TestConfigModule:
    def test_default_rate_limits(self):
        from app.config import Settings
        s = Settings()
        assert s.RATE_LIMIT_FREE == 50
        assert s.RATE_LIMIT_HOBBY == 500
        assert s.RATE_LIMIT_PRO == 5000

    def test_default_doc_limits(self):
        from app.config import Settings
        s = Settings()
        assert s.DOC_LIMIT_FREE == 100
        assert s.DOC_LIMIT_HOBBY == 5000
        assert s.DOC_LIMIT_PRO == 50000


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    def test_full_flow_free_tier(self, client, mock_redis, free_auth_header):
        mock_redis.get.return_value = None
        pipe = Mock()
        pipe.incr.return_value = None
        pipe.expire.return_value = None
        pipe.execute.return_value = [1, True]
        mock_redis.pipeline.return_value = pipe

        # 1. Health
        assert client.get("/health").status_code == 200

        # 2. Formats
        assert client.get("/formats").status_code == 200

        # 3. Usage
        usage = client.get("/usage", headers=free_auth_header)
        assert usage.status_code == 200
        assert usage.json()["tier"] == "free"

        # 4. Convert
        convert = client.post(
            "/convert",
            headers=free_auth_header,
            files={"file": ("doc.txt", b"Document content here", "text/plain")}
        )
        assert convert.status_code == 200
        assert convert.json()["status"] == "converted"

    def test_rate_limit_enforcement(self, client, mock_redis, free_auth_header):
        mock_redis.get.return_value = "50"

        response = client.post(
            "/convert",
            headers=free_auth_header,
            files={"file": ("test.txt", b"content", "text/plain")}
        )
        assert response.status_code == 429
