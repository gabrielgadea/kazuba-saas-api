"""Authentication and API key management."""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings


def get_current_user(
    credentials: HTTPAuthorizationCredentials,
    db: Session = Depends(get_db)
) -> dict:
    """
    Validate API key and return user info.
    
    For MVP: simplified validation. In production, query database.
    """
    api_key = credentials.credentials
    
    # TODO: Query database for valid API keys
    # For now, return mock user based on key prefix
    if api_key.startswith("kzb_free_"):
        return {
            "id": "user_free",
            "tier": "free",
            "requests_limit": settings.RATE_LIMIT_FREE,
            "docs_limit": settings.DOC_LIMIT_FREE,
        }
    elif api_key.startswith("kzb_hobby_"):
        return {
            "id": "user_hobby",
            "tier": "hobby",
            "requests_limit": settings.RATE_LIMIT_HOBBY,
            "docs_limit": settings.DOC_LIMIT_HOBBY,
        }
    elif api_key.startswith("kzb_pro_"):
        return {
            "id": "user_pro",
            "tier": "pro",
            "requests_limit": settings.RATE_LIMIT_PRO,
            "docs_limit": settings.DOC_LIMIT_PRO,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
