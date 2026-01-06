#!/bin/bash
echo "🧹 Cleaning up and starting fresh..."

# 1. Stop any container using port 8000
echo "1. Stopping containers on port 8000..."
docker stop $(docker ps -q --filter "publish=8000") 2>/dev/null || true

# 2. Remove all stopped containers
echo "2. Removing old containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

# 3. Check if port 8000 is free
echo "3. Checking port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️ Port 8000 is in use by non-Docker process"
    echo "   Using port 8080 instead..."
    PORT=8080
else
    PORT=8000
fi

# 4. Run new container
echo "4. Starting new container on port $PORT..."
docker run -d -p ${PORT}:8000 --name heart-api-container heart-api

# 5. Wait and test
echo "5. Waiting for API to start..."
sleep 5

echo "6. Testing API..."
curl -s http://localhost:${PORT}/health | python -m json.tool 2>/dev/null || \
  echo "Testing with curl..." && curl http://localhost:${PORT}/health

echo ""
echo "✅ API running on: http://localhost:${PORT}"
echo "📚 Docs: http://localhost:${PORT}/docs"
