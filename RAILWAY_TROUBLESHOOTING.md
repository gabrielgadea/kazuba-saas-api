# Railway Deploy Troubleshooting

## Erro comum: Build falha

### Sintoma
```
Build failed: ERROR: failed to solve: process "/bin/sh -c alembic upgrade head" did not complete successfully
```

### Causa
O Railway tenta rodar migrations antes do PostgreSQL estar pronto.

### Solução aplicada ✅
- Dockerfile agora usa `CMD` em vez de `RUN` para migrations
- Adicionado retry logic no `init_db()` do main.py
- Redis agora tem fallback quando indisponível

## Erro comum: Healthcheck falha

### Sintoma
```
Healthcheck failed: connection refused
```

### Causa
Aplicação demora para iniciar ou porta incorreta.

### Solução aplicada ✅
- Healthcheck timeout aumentado para 60s
- Dockerfile expõe porta `${PORT:-8000}`
- CMD usa `sh -c` para expandir variáveis corretamente

## Deploy Manual (se automático falhar)

1. Acesse https://railway.com/dashboard
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha `gabrielgadea/kazuba-saas-api`
5. Aguarde build (2-3 minutos)
6. Adicione PostgreSQL: "New" → "Database" → "Add PostgreSQL"
7. Adicione Redis: "New" → "Database" → "Add Redis"
8. Configure variáveis em "Variables"

## Variáveis obrigatórias

```
SECRET_KEY=openssl rand -hex 32
FRONTEND_URL=https://kazuba.com.br
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_HOBBY=price_...
STRIPE_PRICE_PRO=price_...
```

`DATABASE_URL` e `REDIS_URL` são preenchidos automaticamente pelo Railway.

## Verificar logs

```bash
railway logs
```

Ou no dashboard: Project → Service → Deployments → Logs

## Redeploy manual

```bash
railway login
railway link
git commit --allow-empty -m "Trigger redeploy"
git push
```

Ou no dashboard: Project → Service → Deployments → ⋮ → Redeploy
