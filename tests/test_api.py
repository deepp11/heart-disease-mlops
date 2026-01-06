import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Heart Disease Prediction API Running"
    }


def test_logistic_prediction():
    payload = {
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

    response = client.post("/predict/logistic", json=payload)

    assert response.status_code == 200
    assert "prediction" in response.json()
    assert response.json()["prediction"] in [0, 1]


def test_rf_prediction():
    payload = {
        "age": 58,
        "sex": 0,
        "cp": 2,
        "trestbps": 130,
        "chol": 197,
        "fbs": 0,
        "restecg": 1,
        "thalach": 131,
        "exang": 0,
        "oldpeak": 0.6,
        "slope": 1,
        "ca": 0,
        "thal": 2
    }

    response = client.post("/predict/rf", json=payload)

    assert response.status_code == 200
    assert "prediction" in response.json()
    assert response.json()["prediction"] in [0, 1]
