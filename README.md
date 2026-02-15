# Kazuba Converter SaaS API

> Transforme documentos corporativos em dados estruturados para LLMs.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-Proprietary-red)]()

## Features

- 🔄 **Document Conversion**: PDF, DOCX, TXT, MD → Markdown/Text
- 🔐 **API Key Authentication**: Tiered access control
- ⚡ **Rate Limiting**: Redis-backed per-user rate limiting
- 💳 **Stripe Integration**: Subscription management via Checkout
- 🐳 **Docker Ready**: Full docker-compose setup
- ☁️ **Cloud Deploy**: Railway + Render configs included
- 📊 **Usage Tracking**: Per-user statistics endpoint
- 📖 **Interactive Docs**: Swagger UI + ReDoc

## Quick Start

### Docker (Recommended)

```bash
# Clone
git clone https://github.com/gabrielgadea/kazuba-saas-api.git
cd kazuba-saas-api

# Start all services
docker-compose up --build -d

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (or use docker-compose for services only)
docker-compose up -d db redis

# Set environment variables
export DATABASE_URL=postgresql://kazuba:kazuba@localhost:5432/kazuba_saas
export REDIS_URL=redis://localhost:6379

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

## API Usage

### Convert a Document

```bash
curl -X POST http://localhost:8000/convert \
  -H "Authorization: Bearer kzb_free_test123" \
  -F "file=@document.pdf" \
  -F "output_format=markdown"
```

### Check Usage

```bash
curl -H "Authorization: Bearer kzb_free_test123" \
  http://localhost:8000/usage
```

### Check Health

```bash
curl http://localhost:8000/health
```

## Project Structure

```
├── app/
│   ├── main.py           # FastAPI application & routes
│   ├── config.py          # Pydantic settings
│   ├── database.py        # SQLAlchemy engine & session
│   ├── auth.py            # API key authentication
│   ├── rate_limit.py      # Redis-backed rate limiting
│   ├── convert.py         # Document conversion logic
│   └── stripe_routes.py   # Stripe payment integration
├── models/
│   └── __init__.py        # SQLAlchemy models (User, ApiKey, UsageLog)
├── alembic/               # Database migrations
├── tests/
│   ├── conftest.py        # Test fixtures
│   ├── test_api.py        # Comprehensive test suite
│   └── test_main.py       # Unit tests
├── landing/
│   └── index.html         # Landing page
├── docs/
│   └── api.md             # Full API documentation
├── docker-compose.yml     # Local development stack
├── Dockerfile             # Production container
├── railway.json           # Railway deployment config
├── render.yaml            # Render deployment config
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (local)
```

## Pricing Tiers

| Feature | Free | Hobby (R$ 29/mês) | Pro (R$ 149/mês) |
|---------|------|-------------------|------------------|
| Requests/day | 50 | 500 | 5,000 |
| Docs/month | 100 | 5,000 | 50,000 |
| Supported formats | All | All | All |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov=models --cov-report=term-missing
```

## Deploy

### Railway

1. Connect repo at [railway.app](https://railway.app)
2. Add PostgreSQL and Redis services
3. Set environment variables (SECRET_KEY, STRIPE_*)
4. Deploy automatically on push

### Render

1. Connect repo at [render.com](https://render.com)
2. Use `render.yaml` for blueprint
3. PostgreSQL and Redis auto-provisioned
4. Set Stripe keys in dashboard

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://kazuba:kazuba@db:5432/kazuba_saas` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `SECRET_KEY` | JWT/session secret | `change-me-in-production` |
| `STRIPE_SECRET_KEY` | Stripe API key | _(empty)_ |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | _(empty)_ |
| `STRIPE_PRICE_HOBBY` | Stripe Price ID for Hobby | _(empty)_ |
| `STRIPE_PRICE_PRO` | Stripe Price ID for Pro | _(empty)_ |
| `FRONTEND_URL` | Frontend URL for Stripe redirects | `http://localhost:3000` |

## License

Proprietary — Kazuba © 2026
