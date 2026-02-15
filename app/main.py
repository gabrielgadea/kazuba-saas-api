"""
Kazuba Converter SaaS API
FastAPI application with authentication, rate limiting, and Stripe integration.
"""

import time
import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base
from app.auth import get_current_user
from app.stripe_routes import router as stripe_router
from app.convert import convert_document

# Create tables with retry logic for Railway deploy
def init_db(max_retries=5, delay=2):
    """Initialize database with retry logic for cloud deployments."""
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Database initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️  DB connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("❌ Failed to connect to database after all retries")
                return False

# Initialize DB (but don't block startup)
db_ready = init_db()

app = FastAPI(
    title="Kazuba Converter SaaS API",
    description="Transforme documentos corporativos em dados estruturados para LLMs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include Stripe routes
app.include_router(stripe_router)

# Mount static files (landing page)
landing_path = os.path.join(os.path.dirname(__file__), "..", "landing")
if os.path.exists(landing_path):
    app.mount("/static", StaticFiles(directory=landing_path), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "https://kazuba.com.br", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Serve landing page if available, otherwise return API info."""
    landing_file = os.path.join(landing_path, "index.html")
    if os.path.exists(landing_file):
        return FileResponse(landing_file)
    
    return {
        "name": "Kazuba Converter SaaS API",
        "version": "0.1.0",
        "docs": "/docs",
        "pricing": {
            "free": {"requests_per_day": 50, "docs_per_month": 100},
            "hobby": {"price": "R$ 29/mês", "requests_per_day": 500, "docs_per_month": 5000},
            "pro": {"price": "R$ 149/mês", "requests_per_day": 5000, "docs_per_month": 50000},
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "database": "connected" if db_ready else "disconnected",
        "version": "0.1.0"
    }


@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    output_format: str = "markdown",
    user: dict = Depends(get_current_user),
):
    """
    Convert a document to structured format.
    
    - **file**: Document to convert (PDF, DOCX, TXT, MD)
    - **output_format**: Desired output format (markdown, text)
    - Requires valid API key (Bearer token)
    - Respects rate limits based on user tier
    
    Returns converted document content.
    """
    # Apply rate limiting
    from app.rate_limit import rate_limit
    try:
        rate_limit(user)
    except HTTPException:
        raise
    
    # Convert document
    result = await convert_document(file, output_format)
    
    # Add user info to response
    result["user_tier"] = user.get("tier", "free")
    result["requests_remaining"] = user.get("requests_remaining", 0)
    
    return result


@app.get("/usage")
async def get_usage(
    user: dict = Depends(get_current_user)
):
    """Get current usage statistics for the authenticated user."""
    return {
        "tier": user.get("tier", "free"),
        "requests_today": user.get("requests_today", 0),
        "requests_limit": user.get("requests_limit", 50),
        "docs_this_month": user.get("docs_this_month", 0),
        "docs_limit": user.get("docs_limit", 100),
        "requests_remaining": user.get("requests_remaining", 50),
    }


@app.get("/formats")
async def get_supported_formats():
    """Get list of supported input and output formats."""
    return {
        "input_formats": [
            {"type": "application/pdf", "extension": ".pdf", "description": "PDF documents"},
            {"type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "extension": ".docx", "description": "Microsoft Word documents"},
            {"type": "text/plain", "extension": ".txt", "description": "Plain text files"},
            {"type": "text/markdown", "extension": ".md", "description": "Markdown files"},
        ],
        "output_formats": [
            {"format": "markdown", "description": "Markdown with metadata header"},
            {"format": "text", "description": "Plain text extraction"},
        ]
    }
