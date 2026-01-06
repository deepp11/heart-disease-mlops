# test_api.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing Heart Disease API")
    print("="*50)
    
    # 1. Test root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   ✅ Root: {response.json()}")
    except:
        print("   ❌ API not running")
        return
    
    # 2. Test health check
    print("\n2. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    health = response.json()
    print(f"   ✅ Status: {health['status']}")
    print(f"   ✅ Active model: {health['active_model']}")
    print(f"   ✅ Models loaded: {list(health['models_loaded'].keys())}")
    
    # 3. Test available models
    print("\n3. Testing available models...")
    response = requests.get(f"{BASE_URL}/models")
    models = response.json()
    print(f"   ✅ Available models: {models['available_models']}")
    
    # 4. Test prediction with sample data
    print("\n4. Testing prediction...")
    sample_patient = {
        "age": 63,
        "sex": 1,
        "cp": 3,
        "trestbps": 145,
        "chol": 233,
        "fbs": 1,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 2.3,
        "slope": 0,
        "ca": 0,
        "thal": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=sample_patient,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"   ✅ Prediction successful!")
        print(f"   📊 Model used: {result['result']['model_used']}")
        print(f"   🔮 Prediction: {result['result']['prediction']}")
        print(f"   📈 Probability: {result['result']['probability']:.2%}")
        print(f"   ⚠️ Risk level: {result['result']['risk_level']}")
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
    
    # 5. Test specific model prediction
    print("\n5. Testing with specific model...")
    for model_name in models['available_models']:
        try:
            response = requests.post(
                f"{BASE_URL}/predict/{model_name}",
                json=sample_patient
            )
            result = response.json()
            print(f"   ✅ {model_name}: Prediction={result['result']['prediction']}")
        except:
            print(f"   ❌ {model_name}: Failed")
    
    print("\n" + "="*50)
    print("🎯 API Test Complete!")
    print(f"📚 Open API docs: {BASE_URL}/docs")

if __name__ == "__main__":
    test_api()