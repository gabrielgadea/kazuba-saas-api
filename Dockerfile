FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway provides PORT env variable
EXPOSE ${PORT:-8000}

# Start command - try migrations but don't fail if DB not ready yet
CMD ["sh", "-c", "alembic upgrade head 2>/dev/null || echo 'Migrations skipped - will use create_all fallback' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
