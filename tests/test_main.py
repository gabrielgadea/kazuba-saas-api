"""Tests for main.py to achieve 100% coverage."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app, convert, get_usage


class TestMainModule:
    """Tests for app/main.py — 100% coverage."""
    
    @pytest.mark.asyncio
    async def test_convert_endpoint_success(self):
        """Test convert endpoint with successful rate limiting."""
        from fastapi.security import HTTPAuthorizationCredentials
        from app.rate_limit import rate_limit
        
        # Mock user
        user = {
            "tier": "free",
            "requests_limit": 50,
            "docs_limit": 100
        }
        
        # Mock rate_limit to not raise exception
        with patch('app.rate_limit.redis_client') as mock_redis:
            mock_redis.get.return_value = None
            mock_redis.pipeline.return_value = Mock(
                incr=Mock(return_value=None),
                expire=Mock(return_value=None),
                execute=Mock(return_value=[1, True])
            )
            
            # Mock credentials
            credentials = HTTPAuthorizationCredentials(
                credentials="kzb_free_test123",
                scheme="Bearer"
            )
            
            result = await convert(credentials, user)
            
            assert result["status"] == "success"
            assert result["user_tier"] == "free"
    
    @pytest.mark.asyncio
    async def test_convert_endpoint_rate_limit_exceeded(self):
        """Test convert endpoint when rate limit is exceeded."""
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        from app.rate_limit import rate_limit
        
        user = {
            "tier": "free",
            "requests_limit": 50,
            "docs_limit": 100
        }
        
        # Mock rate_limit to raise HTTPException
        with patch('app.rate_limit.redis_client') as mock_redis:
            mock_redis.get.return_value = "50"  # At limit
            
            credentials = HTTPAuthorizationCredentials(
                credentials="kzb_free_test123",
                scheme="Bearer"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await convert(credentials, user)
            
            assert exc_info.value.status_code == 429
    
    @pytest.mark.asyncio
    async def test_get_usage_endpoint(self):
        """Test get_usage endpoint."""
        from fastapi.security import HTTPAuthorizationCredentials
        
        user = {
            "tier": "hobby",
            "requests_today": 10,
            "requests_limit": 500,
            "docs_this_month": 100,
            "docs_limit": 5000
        }
        
        credentials = HTTPAuthorizationCredentials(
            credentials="kzb_hobby_test456",
            scheme="Bearer"
        )
        
        result = await get_usage(credentials, user)
        
        assert result["tier"] == "hobby"
        assert result["requests_today"] == 10
        assert result["requests_limit"] == 500
        assert result["docs_this_month"] == 100
        assert result["docs_limit"] == 5000
    
    @pytest.mark.asyncio
    async def test_get_usage_with_defaults(self):
        """Test get_usage with default values."""
        from fastapi.security import HTTPAuthorizationCredentials
        
        # User with missing fields
        user = {}
        
        credentials = HTTPAuthorizationCredentials(
            credentials="kzb_free_test123",
            scheme="Bearer"
        )
        
        result = await get_usage(credentials, user)
        
        assert result["tier"] == "free"  # Default
        assert result["requests_today"] == 0  # Default
        assert result["requests_limit"] == 50  # Default
        assert result["docs_this_month"] == 0  # Default
        assert result["docs_limit"] == 100  # Default
