# Kazuba Converter SaaS API — Documentation

## Overview

The Kazuba Converter SaaS API transforms corporate documents (PDF, DOCX, TXT, MD) into structured, LLM-ready data. It provides a simple REST API with tiered pricing, rate limiting, and Stripe integration.

**Base URL**: `https://api.kazuba.com.br` (production) or `http://localhost:8000` (development)

---

## Authentication

All authenticated endpoints require a Bearer token (API key) in the `Authorization` header.

```bash
Authorization: Bearer kzb_<tier>_<key>
```

### API Key Formats

| Tier | Prefix | Example |
|------|--------|---------|
| Free | `kzb_free_` | `kzb_free_abc123def456` |
| Hobby | `kzb_hobby_` | `kzb_hobby_abc123def456` |
| Pro | `kzb_pro_` | `kzb_pro_abc123def456` |

---

## Pricing Tiers

| Feature | Free | Hobby (R$ 29/mês) | Pro (R$ 149/mês) |
|---------|------|-------------------|------------------|
| Requests/day | 50 | 500 | 5,000 |
| Docs/month | 100 | 5,000 | 50,000 |
| File size limit | 5 MB | 25 MB | 100 MB |
| Support | Community | Email | Priority |

---

## Endpoints

### `GET /`

Returns API info or serves the landing page.

**Response** (JSON):
```json
{
  "name": "Kazuba Converter SaaS API",
  "version": "0.1.0",
  "docs": "/docs",
  "pricing": {
    "free": {"requests_per_day": 50, "docs_per_month": 100},
    "hobby": {"price": "R$ 29/mês", "requests_per_day": 500, "docs_per_month": 5000},
    "pro": {"price": "R$ 149/mês", "requests_per_day": 5000, "docs_per_month": 50000}
  }
}
```

---

### `GET /health`

Health check endpoint for monitoring and load balancers.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "0.1.0"
}
```

---

### `GET /formats`

Returns supported input and output formats. No authentication required.

**Response**:
```json
{
  "input_formats": [
    {"type": "application/pdf", "extension": ".pdf", "description": "PDF documents"},
    {"type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "extension": ".docx", "description": "Microsoft Word documents"},
    {"type": "text/plain", "extension": ".txt", "description": "Plain text files"},
    {"type": "text/markdown", "extension": ".md", "description": "Markdown files"}
  ],
  "output_formats": [
    {"format": "markdown", "description": "Markdown with metadata header"},
    {"format": "text", "description": "Plain text extraction"}
  ]
}
```

---

### `POST /convert`

🔐 **Requires authentication**

Convert a document to structured format.

**Request**:
- `Content-Type: multipart/form-data`
- `file` (required): The document file
- `output_format` (optional): `markdown` (default) or `text`

**Example (curl)**:
```bash
curl -X POST https://api.kazuba.com.br/convert \
  -H "Authorization: Bearer kzb_free_your_api_key" \
  -F "file=@document.pdf" \
  -F "output_format=markdown"
```

**Example (Python)**:
```python
import httpx

with open("document.pdf", "rb") as f:
    response = httpx.post(
        "https://api.kazuba.com.br/convert",
        headers={"Authorization": "Bearer kzb_free_your_api_key"},
        files={"file": ("document.pdf", f, "application/pdf")},
        data={"output_format": "markdown"}
    )

result = response.json()
print(result["content"])
```

**Success Response** (200):
```json
{
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "file_type": "pdf",
  "output_format": "markdown",
  "status": "converted",
  "content": "# document.pdf\n\n---\n\nExtracted text content here...\n\n---\n\n*Converted by Kazuba Converter*",
  "content_length": 1234,
  "extracted_text_length": 1000,
  "user_tier": "free",
  "requests_remaining": 49
}
```

**Error Responses**:

| Status | Detail |
|--------|--------|
| 400 | Unsupported file type |
| 400 | Empty file uploaded |
| 401 | Invalid API key |
| 403 | Missing authentication |
| 429 | Rate limit exceeded |
| 503 | PDF/DOCX processing not available |

---

### `GET /usage`

🔐 **Requires authentication**

Get current usage statistics for the authenticated user.

**Example**:
```bash
curl -H "Authorization: Bearer kzb_free_your_key" \
  https://api.kazuba.com.br/usage
```

**Response**:
```json
{
  "tier": "free",
  "requests_today": 5,
  "requests_limit": 50,
  "docs_this_month": 12,
  "docs_limit": 100,
  "requests_remaining": 45
}
```

---

### `POST /stripe/create-checkout-session`

Create a Stripe Checkout session for upgrading to a paid tier.

**Query Parameters**:
- `tier`: `hobby` or `pro`

**Response**:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

---

### `POST /stripe/webhook`

Stripe webhook endpoint for handling subscription events. Configure in Stripe Dashboard.

**Events handled**:
- `checkout.session.completed`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.subscription.deleted`

---

### `GET /stripe/config`

Get public Stripe configuration.

---

## Rate Limiting

Rate limiting is enforced per user per day using Redis.

| Header | Description |
|--------|-------------|
| `Retry-After: 86400` | Seconds until rate limit resets (returned on 429) |

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded. Limit: 50 requests per day."
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid API key) |
| 403 | Forbidden (missing authentication) |
| 429 | Too Many Requests (rate limited) |
| 503 | Service Unavailable |

---

## Interactive Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

---

## SDKs & Libraries

### Python
```python
import httpx

class KazubaClient:
    def __init__(self, api_key: str, base_url: str = "https://api.kazuba.com.br"):
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    def convert(self, filepath: str, output_format: str = "markdown") -> dict:
        with open(filepath, "rb") as f:
            response = self.client.post(
                "/convert",
                files={"file": f},
                data={"output_format": output_format}
            )
        response.raise_for_status()
        return response.json()
    
    def usage(self) -> dict:
        response = self.client.get("/usage")
        response.raise_for_status()
        return response.json()

# Usage
client = KazubaClient("kzb_free_your_key")
result = client.convert("document.pdf")
print(result["content"])
```

### curl
```bash
# Convert a PDF
curl -X POST https://api.kazuba.com.br/convert \
  -H "Authorization: Bearer kzb_free_your_key" \
  -F "file=@document.pdf"

# Check usage
curl -H "Authorization: Bearer kzb_free_your_key" \
  https://api.kazuba.com.br/usage
```
