# API Reference

## Base URL

```
Production: https://api.kazuba.com.br
Local: http://localhost:8000
```

## Authentication

Todas as requisições requerem um API key no header `Authorization`:

```bash
curl -H "Authorization: Bearer kzb_free_xxxxxxxx" \
  https://api.kazuba.com.br/convert
```

## Endpoints

### GET /

Retorna informações sobre a API e pricing.

**Response:**
```json
{
  "name": "Kazuba Converter SaaS API",
  "version": "0.1.0",
  "pricing": {
    "free": {"requests_per_day": 50, "docs_per_month": 100},
    "hobby": {"price": "R$ 29/mês", "requests_per_day": 500, "docs_per_month": 5000},
    "pro": {"price": "R$ 149/mês", "requests_per_day": 5000, "docs_per_month": 50000}
  }
}
```

### GET /health

Health check do serviço.

**Response:**
```json
{"status": "healthy"}
```

### POST /convert

Converte um documento para formato estruturado.

**Headers:**
- `Authorization: Bearer {api_key}` (required)
- `Content-Type: multipart/form-data`

**Body:**
- `file`: Arquivo para converter (PDF, DOCX, TXT, MD)
- `output_format`: `markdown` (default) ou `json`

**Response:**
```json
{
  "status": "success",
  "filename": "documento.pdf",
  "content_type": "application/pdf",
  "output_format": "markdown",
  "content": "# Conteúdo convertido..."
}
```

**Errors:**
- `401 Unauthorized`: API key inválida
- `429 Too Many Requests`: Rate limit excedido
- `400 Bad Request`: Tipo de arquivo não suportado

### GET /usage

Retorna estatísticas de uso do usuário autenticado.

**Headers:**
- `Authorization: Bearer {api_key}` (required)

**Response:**
```json
{
  "tier": "hobby",
  "requests_today": 45,
  "requests_limit": 500,
  "docs_this_month": 1200,
  "docs_limit": 5000
}
```

## Rate Limits

| Tier | Requisições/dia | Documentos/mês |
|------|-----------------|----------------|
| Free | 50 | 100 |
| Hobby | 500 | 5.000 |
| Pro | 5.000 | 50.000 |

Os headers de resposta incluem informações sobre rate limit:

```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 455
X-RateLimit-Reset: 86400
```

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Bad Request — requisição inválida |
| 401 | Unauthorized — API key inválida |
| 429 | Too Many Requests — rate limit excedido |
| 500 | Internal Server Error — erro no servidor |
