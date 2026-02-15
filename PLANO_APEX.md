# Plano APEX: Kazuba SaaS API Production Ready

## 📋 ENQUADRAMENTO

### Pln1: Estado Atual
- **Projeto**: kazuba-products/p1-saas-api
- **Stack**: FastAPI + PostgreSQL + Redis + Stripe
- **Status**: Scaffold funcional, mas incompleto

### Problemas Identificados
1. `convert.py` é placeholder (WIP) - não integra com kazuba-converter real
2. Endpoint `/convert` não aceita arquivo (só retorna mock)
3. Testes existem mas precisam de ajustes
4. Documentação API incompleta
5. Falta integração real com modelos de DB para auth

### Critério de Sucesso
- API 100% funcional com conversão real de documentos
- Testes passando (>90% coverage)
- Documentação OpenAPI completa
- Deploy pronto (Railway/Render)

## 🔬 DECOMPOSIÇÃO

### SP1: Testar Local e Corrigir Bugs
- Executar docker-compose up
- Identificar e corrigir erros de import/dependência
- Validar health check

### SP2: Completar Integração kazuba-converter
- Implementar converter.py com lógica real
- Suportar PDF, DOCX, TXT, MD
- Integrar com endpoint /convert (upload file)

### SP3: Criar/Atualizar Testes
- Corrigir testes existentes
- Adicionar testes de integração
- Atingir 90%+ coverage

### SP4: Documentar API
- OpenAPI/Swagger completo
- Exemplos de requisição/resposta
- Guia de uso

### SP5: Preparar Deploy
- Verificar configs Railway/Render
- Health checks
- Variáveis de ambiente

## ⚡ SOLUÇÕES

### Solução SP1: Local Testing
- Executar: `docker-compose up --build`
- Verificar logs
- Testar endpoints

### Solução SP2: Converter Integration
- Usar PyPDF2 para PDF
- Usar python-docx para DOCX
- Extrair texto e converter para markdown

### Solução SP3: Testing
- pytest com asyncio
- Mock para Redis/Stripe
- Testes de upload de arquivo

### Solução SP4: Documentation
- Docstrings em todos os endpoints
- README atualizado
- docs/api.md completo

### Solução SP5: Deploy
- railway.json validado
- render.yaml validado
- Dockerfile otimizado

## ✅ VALIDAÇÃO

- [ ] Todos os endpoints funcionam
- [ ] Conversão de documentos funciona
- [ ] Testes passam
- [ ] Documentação completa
- [ ] Deploy config validado

## 👹 ADVOGADO DO DIABO

**Objeção**: "Não temos o kazuba-converter real, só um placeholder."
**Refutação**: Vamos implementar a conversão básica (PDF→texto, DOCX→texto) usando bibliotecas existentes. Não precisamos do converter completo para MVP.

## 🎯 RESPOSTA FINAL

Implementar conversão básica de documentos, garantir testes, documentar e preparar para deploy.

## 📊 MÉTRICAS

- Confiança Global: 0.92
- Coverage Target: 90%
- Tempo Estimado: 2-3 horas
