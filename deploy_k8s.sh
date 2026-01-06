#!/bin/bash
echo "☸️  KUBERNETES DEPLOYMENT SIMULATION"
echo "===================================="

echo "1. Building Docker image..."
docker build -t heart-api .

echo "2. Deploying to Kubernetes..."
kubectl apply -f deployment/kubernetes/

echo "3. Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=heart-disease-api --timeout=120s

echo "4. Checking deployment status..."
kubectl get deployments
kubectl get pods
kubectl get services

echo "5. Getting LoadBalancer IP (simulated)..."
# In real cloud, this would give EXTERNAL-IP
# Locally, we use port-forward
kubectl port-forward service/heart-disease-service 8080:80 &
PORT_FORWARD_PID=$!
sleep 3

echo "6. Testing API through Kubernetes..."
curl http://localhost:8080/health

echo ""
echo "✅ KUBERNETES DEPLOYMENT SIMULATED"
echo "🌐 Access via: http://localhost:8080"
echo "📚 Docs: http://localhost:8080/docs"

# Keep running
echo ""
read -p "Press Enter to stop and clean up..."
kill $PORT_FORWARD_PID
kubectl delete -f deployment/kubernetes/
echo "🧹 Cleanup complete"
