#!/bin/bash
# Deploy script para Render.com (alternativa ao Railway)
# Render permite deploy via GitHub sem login interativo

set -e

echo "🚀 Preparando deploy para Render.com..."

# Criar render.yaml para infraestrutura como código
cat > render.yaml << 'EOF'
services:
  - type: web
    name: kazuba-saas-api
    runtime: docker
    repo: https://github.com/gabrielgadea/kazuba-saas-api
    branch: main
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: kazuba-postgres
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: kazuba-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
      - key: FRONTEND_URL
        value: https://kazuba.com.br
    healthCheckPath: /health

  - type: redis
    name: kazuba-redis
    ipAllowList: []

databases:
  - name: kazuba-postgres
    databaseName: kazuba_saas
    user: kazuba
    plan: free
EOF

echo "✅ render.yaml criado"

# Commit e push
git add render.yaml
git commit -m "Add Render.com deployment config" || true
git push

echo ""
echo "📋 Próximos passos para deploy no Render:"
echo "1. Acesse: https://dashboard.render.com/"
echo "2. Clique em 'New +' → 'Blueprint'"
echo "3. Conecte o repo: gabrielgadea/kazuba-saas-api"
echo "4. Render detectará o render.yaml e criará tudo automaticamente"
echo ""
echo "🔗 Ou use o botão Deploy to Render:"
echo "   https://render.com/deploy?repo=https://github.com/gabrielgadea/kazuba-saas-api"
