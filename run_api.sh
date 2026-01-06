#!/bin/bash
# ============================================
# HEART DISEASE API - ONE-COMMAND LAUNCHER
# ============================================
# Just run: ./run_api.sh
# ============================================

set -e  # Stop on any error

echo "🚀 HEART DISEASE ML API LAUNCHER"
echo "========================================"

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# ============================================
# STEP 1: CHECK REQUIREMENTS
# ============================================

print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found! Install Docker Desktop first:"
    echo "   https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running! Start Docker Desktop first."
    exit 1
fi

print_status "Docker is installed and running"

# ============================================
# STEP 2: CLEANUP OLD CONTAINERS
# ============================================

print_status "Cleaning up old containers..."

# Stop any container using port 8000 or 8080
for PORT in 8000 8080 9000; do
    CONTAINER_IDS=$(docker ps -q --filter "publish=$PORT")
    if [ ! -z "$CONTAINER_IDS" ]; then
        print_warning "Stopping containers on port $PORT..."
        docker stop $CONTAINER_IDS 2>/dev/null || true
    fi
done

# Remove all stopped containers
docker rm $(docker ps -aq) 2>/dev/null || true
print_status "Old containers cleaned up"

# ============================================
# STEP 3: CHECK PORT AVAILABILITY
# ============================================

print_status "Checking available port..."

# Try port 8000 first, then 8080, then 9000
for PORT in 8000 8080 9000; do
    if ! lsof -i :$PORT > /dev/null 2>&1; then
        SELECTED_PORT=$PORT
        break
    fi
done

if [ -z "$SELECTED_PORT" ]; then
    SELECTED_PORT=8001
    print_warning "All common ports busy, using $SELECTED_PORT"
else
    print_status "Using port: $SELECTED_PORT"
fi

# ============================================
# STEP 4: BUILD DOCKER IMAGE (IF NEEDED)
# ============================================

print_status "Checking Docker image..."

if [[ "$1" == "--rebuild" ]] || ! docker images | grep -q heart-api; then
    print_status "Building Docker image..."
    docker build -t heart-api .
else
    print_status "Using existing Docker image: heart-api"
fi

# ============================================
# STEP 5: RUN THE CONTAINER
# ============================================

print_status "Starting API container..."
CONTAINER_NAME="heart-api-$SELECTED_PORT"

docker run -d \
  -p $SELECTED_PORT:8000 \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  heart-api

print_status "Container started: $CONTAINER_NAME"
print_status "Waiting for API to initialize..."

# Wait for API to be ready
for i in {1..10}; do
    if curl -s http://localhost:$SELECTED_PORT/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 2
done

echo ""

# ============================================
# STEP 6: TEST THE API
# ============================================

print_status "Testing API endpoints..."

# Test root endpoint
if curl -s http://localhost:$SELECTED_PORT/ | grep -q "Heart Disease"; then
    print_status "Root endpoint: ✓ Working"
else
    print_warning "Root endpoint: Could not verify"
fi

# Test health endpoint
HEALTH_RESPONSE=$(curl -s http://localhost:$SELECTED_PORT/health)
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    print_status "Health endpoint: ✓ Healthy"
    
    # Extract model info
    MODELS=$(echo "$HEALTH_RESPONSE" | grep -o '"models_loaded":[^}]*}' || echo "")
    if [[ ! -z "$MODELS" ]]; then
        print_status "Models loaded successfully"
    fi
else
    print_warning "Health endpoint: Not fully healthy"
fi

# ============================================
# STEP 7: DISPLAY USAGE INFORMATION
# ============================================

echo ""
echo "========================================"
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "========================================"
echo ""
echo "🌐 API URLS:"
echo "   Health check:  http://localhost:$SELECTED_PORT/health"
echo "   API Root:      http://localhost:$SELECTED_PORT/"
echo "   Documentation: http://localhost:$SELECTED_PORT/docs"
echo "   Interactive:   http://localhost:$SELECTED_PORT/docs (try it out!)"
echo ""
echo "🐳 DOCKER COMMANDS:"
echo "   View logs:     docker logs $CONTAINER_NAME"
echo "   Stop API:      docker stop $CONTAINER_NAME"
echo "   Restart:       docker restart $CONTAINER_NAME"
echo "   Remove:        docker rm $CONTAINER_NAME"
echo ""
echo "🔧 TEST PREDICTION:"
echo "   curl -X POST http://localhost:$SELECTED_PORT/predict \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"age\":63,\"sex\":1,\"cp\":3,\"trestbps\":145,\"chol\":233,\"fbs\":1,\"restecg\":0,\"thalach\":150,\"exang\":0,\"oldpeak\":2.3,\"slope\":0,\"ca\":0,\"thal\":1}'"
echo ""

# ============================================
# STEP 7: OPTIONAL - OPEN BROWSER
# ============================================

read -p "Open API documentation in browser? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:$SELECTED_PORT/docs"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open "http://localhost:$SELECTED_PORT/docs"
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Windows
        start "http://localhost:$SELECTED_PORT/docs"
    else
        print_warning "Could not auto-open browser. Please visit:"
        echo "   http://localhost:$SELECTED_PORT/docs"
    fi
fi

# Keep script running with container info
echo ""
echo "========================================"
echo "📊 Container is running in background."
echo "Press Ctrl+C to exit this script."
echo "Container will continue running."
echo "========================================"

# Show logs if requested
read -p "Show container logs? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker logs -f $CONTAINER_NAME
else
    # Just wait
    sleep infinity
fi
