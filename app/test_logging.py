# test_logging.py
import requests
import time

print("Testing API logging and monitoring...")
print("=" * 50)

# Test 1: Make a prediction (this will create logs)
print("\n1. Making prediction request...")
try:
    response = requests.post(
        "http://localhost:8000/predict",
        json={
            "age": 52, "sex": 1, "cp": 0, "trestbps": 125,
            "chol": 212, "fbs": 0, "restecg": 1, "thalach": 168,
            "exang": 0, "oldpeak": 1.0, "slope": 2, "ca": 2, "thal": 3
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Check health endpoint
print("\n2. Checking health...")
try:
    health = requests.get("http://localhost:8000/health")
    print(f"   Health: {health.json()}")
except:
    print("   Health endpoint not available")

# Test 3: Check logs endpoint
print("\n3. Checking logs...")
try:
    logs = requests.get("http://localhost:8000/logs")
    log_data = logs.json()
    
    if "logs" in log_data:
        print(f"   Found {len(log_data['logs'])} log entries")
        print("   Recent logs:")
        for i, log in enumerate(log_data['logs'][-3:], 1):  # Show last 3
            print(f"   {i}. {log.strip()}")
    else:
        print(f"   Response: {log_data}")
except Exception as e:
    print(f"   Error accessing logs: {e}")

# Test 4: Check metrics
print("\n4. Checking metrics...")
try:
    metrics = requests.get("http://localhost:8000/metrics")
    print(f"   Metrics: {metrics.json()}")
except:
    print("   Metrics endpoint not available")

print("\n" + "=" * 50)
print("✅ Testing complete!")
print("Check 'api_logs.log' file for detailed logs")