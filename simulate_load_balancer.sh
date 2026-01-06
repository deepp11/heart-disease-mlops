#!/bin/bash
echo "⚖️  LOAD BALANCER SIMULATION"
echo "============================"

# Start multiple instances on different ports
echo "Starting multiple API instances (simulating load balanced backend)..."
docker run -d -p 8001:8000 --name api-1 heart-api
docker run -d -p 8002:8000 --name api-2 heart-api
docker run -d -p 8003:8000 --name api-3 heart-api

# Simple round-robin simulation
echo ""
echo "Simulating Load Balancer round-robin:"
for i in {1..6}; do
  PORT=$((8000 + (i % 3) + 1))
  echo "Request $i → Instance on port $PORT"
  curl -s http://localhost:$PORT/health | grep -o '"status":"[^"]*"' | head -1
done

echo ""
echo "📊 All instances running:"
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

echo ""
echo "✅ Load Balancer pattern demonstrated"
echo "   - Multiple instances for scalability"
echo "   - Health checks on each instance"
echo "   - Distributed traffic simulation"

# Cleanup
read -p "Press Enter to clean up..."
docker stop api-1 api-2 api-3
docker rm api-1 api-2 api-3
