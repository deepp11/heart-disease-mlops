<<<<<<< HEAD
# heart-disease-mlops
Heart Diseas prediction with ML pipeline
=======
# ❤️ Heart Disease MLOps Pipeline

## 🚀 Quick Deployment
```bash
./run_api.sh
```

## 📁 Project Structure
- `app/` - FastAPI application
- `deployment/` - Docker & Kubernetes configs
- `MLOps/` - Machine learning code
- `Dockerfile` - Container definition
- `requirements.txt` - Dependencies

# Clone, setup, test, and deploy
- git clone https://github.com/deepp11/heart-disease-mlops.git
- cd heart-disease-mlops
- pip install -r requirements.txt
- ./run-api.sh &  # Run in background
- sleep 5  # Wait for API to start
- ./quick_test.sh  # Run tests
-  ./simulate_load_balancer.sh # to simulate load balancer

## 🌐 API Endpoints
- Health: `curl http://localhost:8000/health`
- Docs: http://localhost:8080/docs

>>>>>>> ef5f7de (Complete MLOps pipeline: Heart Disease Prediction)
