#!/bin/bash

# ============================================
# Monitoring Setup Script
# ============================================

set -e

echo "🚀 Setting up Monitoring Stack..."

# Create necessary directories
mkdir -p logs grafana/provisioning/datasources grafana/provisioning/dashboards

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

# Build API image
echo "📦 Building API image..."
docker build -t heart-disease-api:latest .

# Start monitoring stack
echo "🔧 Starting monitoring stack..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 15

# Check services
echo "🔍 Checking services..."
for service in api prometheus grafana; do
    if docker-compose ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
    fi
done

echo ""
echo "=========================================="
echo "📊 Monitoring Dashboard URLs:"
echo "=========================================="
echo "API:              http://localhost:8000"
echo "API Metrics:      http://localhost:8000/metrics"
echo "Prometheus:       http://localhost:9090"
echo "Grafana:          http://localhost:3000"
echo "Grafana Login:    admin / admin"
echo ""
echo "📈 Quick Test Commands:"
echo "curl http://localhost:8000/health"
echo "curl http://localhost:8000/metrics"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo "=========================================="