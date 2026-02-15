# 🚀 Railway Deploy Guide

## Opção 1: Deploy via Dashboard (Recomendado - 5 min)

1. **Acesse**: https://railway.com/new
2. **Clique**: "Deploy from GitHub repo"
3. **Selecione**: `gabrielgadea/kazuba-saas-api`
4. **Aguarde**: Railway detectará o `railway.json` e configurará automaticamente

## Opção 2: Deploy via CLI

```bash
# Instalar CLI
npm install -g @railway/cli

# Login (abre browser)
railway login

# Linkar projeto
railway link

# Deploy
railway up
```

## Variáveis de Ambiente (Obrigatórias)

Após criar o projeto, adicione estas variáveis em Settings → Variables:

| Variável | Valor | Onde obter |
|----------|-------|------------|
| `DATABASE_URL` | (auto) | Railway provisiona automaticamente |
| `REDIS_URL` | (auto) | Railway provisiona automaticamente |
| `SECRET_KEY` | `openssl rand -hex 32` | Gere localmente |
| `STRIPE_SECRET_KEY` | `sk_live_...` | Stripe Dashboard |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Stripe CLI/Dashboard |
| `STRIPE_PRICE_HOBBY` | `price_...` | Stripe Product Catalog |
| `STRIPE_PRICE_PRO` | `price_...` | Stripe Product Catalog |
| `FRONTEND_URL` | `https://kazuba.com.br` | Seu domínio |

## Configuração Stripe

1. Crie conta em https://stripe.com/br
2. Crie 2 produtos:
   - **Hobby**: R$ 29/mês
   - **Pro**: R$ 149/mês
3. Copie os Price IDs para as variáveis acima
4. Configure webhook: `https://api.kazuba.com.br/webhooks/stripe`

## Domínio Customizado

1. Em Settings → Domains, adicione: `api.kazuba.com.br`
2. Configure DNS na Hostinger:
   - Tipo: CNAME
   - Nome: `api`
   - Valor: (fornecido pelo Railway)

## Verificação

```bash
# Health check
curl https://api.kazuba.com.br/health

# Docs
curl https://api.kazuba.com.br/docs
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Build falha | Verifique `railway.json` e `Dockerfile` |
| DB connection error | Aguarde 1 min após provisionar PostgreSQL |
| 502 Bad Gateway | Verifique se a porta é `$PORT` (não hardcoded) |
| Migrations não rodam | Confira logs: `railway logs` |

## Repositório

🔗 https://github.com/gabrielgadea/kazuba-saas-api
