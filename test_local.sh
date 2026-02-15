#!/bin/bash
# Test local API

echo "=== Testing Kazuba SaaS API ==="
echo ""

# Start server in background
cd /home/gabrielgadea/projects/analise/kazuba-products/p1-saas-api
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

# Wait for server
sleep 3

echo "1. Testing root endpoint..."
curl -s http://127.0.0.1:8000/ | python3 -m json.tool
echo ""

echo "2. Testing health endpoint..."
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
echo ""

echo "3. Testing convert without auth..."
curl -s http://127.0.0.1:8000/convert -X POST
echo ""

echo "4. Testing convert with free API key..."
curl -s http://127.0.0.1:8000/convert -X POST \
  -H "Authorization: Bearer kzb_free_test123" | python3 -m json.tool
echo ""

echo "5. Testing usage endpoint..."
curl -s http://127.0.0.1:8000/usage \
  -H "Authorization: Bearer kzb_free_test123" | python3 -m json.tool
echo ""

# Stop server
kill $SERVER_PID 2>/dev/null

echo "=== Tests complete ==="
