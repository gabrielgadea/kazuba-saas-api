# Kazuba Converter SaaS API

API gerenciada para kazuba-converter — transforme documentos corporativos em dados estruturados para LLMs.

## 🚀 Quick Start

```bash
# Clone e setup
git clone https://github.com/gabrielgadea/kazuba-saas-api.git
cd kazuba-saas-api
cp .env.example .env
# Edite .env com suas credenciais

# Instalação
pip install -r requirements.txt

# Rodar local
uvicorn app.main:app --reload

# Deploy (Railway)
railway login
railway link
railway up
```

## 📖 Documentação

- [API Reference](docs/api.md)
- [Autenticação](docs/auth.md)
- [Pricing](docs/pricing.md)
- [Self-hosting](docs/self-hosting.md)

## 💰 Pricing

| Tier | Preço | Limites |
|------|-------|---------|
| Free | R$ 0 | 50 req/dia, 100 docs/mês |
| Hobby | R$ 29/mês | 500 req/dia, 5k docs/mês |
| Pro | R$ 149/mês | 5k req/dia, 50k docs/mês |

## 🛠️ Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (Neon)
- **Cache:** Redis (Upstash)
- **Payments:** Stripe
- **Deploy:** Railway

## 📄 License

MIT — veja [LICENSE](LICENSE)
