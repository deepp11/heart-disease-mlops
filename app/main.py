# app/main.py - UPDATED WITH PREPROCESSING
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import pandas as pd
import numpy as np
import joblib
import os
from typing import List, Optional
from datetime import datetime
import logging
import json


# Initialize FastAPI
app = FastAPI(
    title="Heart Disease Prediction API",
    description="API using trained models",
    version="1.0.0"
)

# ============================================
# LOAD MODELS AND PREPROCESSOR
# ============================================

print("📦 Loading models...")

# Try to load preprocessing objects if they exist
preprocessor = None
try:
    if os.path.exists("preprocessor.pkl"):
        preprocessor = joblib.load("preprocessor.pkl")
        print("✅ Loaded preprocessor")
except:
    print("⚠️ No preprocessor found")

# Load models
MODEL_PATHS = {
    "logistic_regression": "final_logistic_regression.pkl",
    "random_forest": "final_random_forest.pkl"
}

models = {}
model_info = {}

for model_name, model_path in MODEL_PATHS.items():
    try:
        if os.path.exists(model_path):
            models[model_name] = joblib.load(model_path)
            model_info[model_name] = {
                "loaded": True,
                "type": type(models[model_name]).__name__
            }
            print(f"✅ Loaded {model_name}: {model_info[model_name]['type']}")
        else:
            print(f"⚠️ {model_path} not found")
            models[model_name] = None
            model_info[model_name] = {"loaded": False, "error": "File not found"}
    except Exception as e:
        print(f"❌ Error loading {model_name}: {e}")
        models[model_name] = None
        model_info[model_name] = {"loaded": False, "error": str(e)}

current_model_name = next((name for name, model in models.items() if model is not None), None)
current_model = models.get(current_model_name) if current_model_name else None
print(f"🎯 Active model: {current_model_name}\n")

# ============================================
# MANUAL PREPROCESSING FUNCTION
# ============================================


def preprocess_features(features_dict):
    """Convert raw features to match training preprocessing"""
    
    # Create DataFrame
    df = pd.DataFrame([features_dict])
    
    # Load preprocessor if exists
    if os.path.exists("preprocessor.pkl"):
        try:
            preprocessor = joblib.load("preprocessor.pkl")
            return preprocessor.transform(df)
        except:
            print("⚠️ Preprocessor failed, using manual encoding")
    
    # Manual encoding as fallback
    # Based on error, the model expects one-hot encoded features
    
    # Create a copy
    df_processed = df.copy()
    
    # One-hot encode categorical variables manually
    categorical_mappings = {
        'sex': {0: 'sex_0', 1: 'sex_1'},
        'cp': {1: 'cp_1', 2: 'cp_2', 3: 'cp_3', 4: 'cp_4'},
        'fbs': {0: 'fbs_0', 1: 'fbs_1'},
        'restecg': {0: 'restecg_0', 1: 'restecg_1', 2: 'restecg_2'},
        'exang': {0: 'exang_0', 1: 'exang_1'},
        'slope': {1: 'slope_1', 2: 'slope_2', 3: 'slope_3'},
        'ca': {0: 'ca_0', 1: 'ca_1', 2: 'ca_2', 3: 'ca_3'},
        'thal': {3: 'thal_3', 6: 'thal_6', 7: 'thal_7'}
    }
    
    # Apply one-hot encoding
    for col, mapping in categorical_mappings.items():
        if col in df_processed.columns:
            for value, new_col in mapping.items():
                df_processed[new_col] = (df_processed[col] == value).astype(int)
            # Drop original column
            df_processed = df_processed.drop(columns=[col])
    
    # Ensure all expected columns exist
    expected_columns = [
        'sex_0', 'sex_1',
        'cp_1', 'cp_2', 'cp_3', 'cp_4',
        'fbs_0', 'fbs_1', 
        'restecg_0', 'restecg_1', 'restecg_2',
        'exang_0', 'exang_1',
        'slope_1', 'slope_2', 'slope_3',
        'ca_0', 'ca_1', 'ca_2', 'ca_3',
        'thal_3', 'thal_6', 'thal_7',
        'age', 'trestbps', 'chol', 'thalach', 'oldpeak'
    ]
    
    # Add missing columns
    for col in expected_columns:
        if col not in df_processed.columns:
            df_processed[col] = 0
    
    # Reorder columns
    df_processed = df_processed[expected_columns]
    
    return df_processed.values  
    df = pd.DataFrame([features_dict])
    
    # If we have a preprocessor saved, use it
    if preprocessor is not None:
        return preprocessor.transform(df)
    
    # Otherwise, apply manual preprocessing to match training
    # Based on the error, you need to one-hot encode categorical features
    
    # List of categorical columns (from training)
    categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    
    # Apply one-hot encoding
    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=False)
    
    # Ensure all expected columns exist (fill missing with 0)
    # This is the CRITICAL part - must match training columns exactly
    
    # Expected columns from training (based on error message)
    expected_columns = [
        'age', 'trestbps', 'chol', 'thalach', 'oldpeak',
        # Add all one-hot encoded columns from training
        'sex_0', 'sex_1',
        'cp_1', 'cp_2', 'cp_3', 'cp_4',
        'fbs_0', 'fbs_1',
        'restecg_0', 'restecg_1', 'restecg_2',
        'exang_0', 'exang_1',
        'slope_1', 'slope_2', 'slope_3',
        'ca_0', 'ca_1', 'ca_2', 'ca_3',
        'thal_3', 'thal_6', 'thal_7'
    ]
    
    # Add missing columns with 0 values
    for col in expected_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    
    # Reorder columns to match training
    df_encoded = df_encoded[expected_columns]
    
    return df_encoded.values

# ============================================
# Data Models
# ============================================

class PatientFeatures(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    age: float
    sex: float  # 1=male, 0=female
    cp: float  # chest pain type (1-4)
    trestbps: float  # resting blood pressure
    chol: float  # cholesterol
    fbs: float  # fasting blood sugar > 120 mg/dl
    restecg: float  # resting electrocardiographic results
    thalach: float  # maximum heart rate achieved
    exang: float  # exercise induced angina
    oldpeak: float  # ST depression induced by exercise
    slope: float  # slope of peak exercise ST segment
    ca: float  # number of major vessels colored by flourosopy (0-3)
    thal: float  # thalassemia (3=normal, 6=fixed, 7=reversible)

class PredictionResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_used: str
    prediction: int
    probability: float
    risk_level: str
    confidence: Optional[float] = None

class SinglePrediction(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    features: PatientFeatures
    result: PredictionResult
    timestamp: str

class HealthCheck(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    status: str
    models_loaded: dict
    active_model: str

# ============================================
# Helper Function with Preprocessing
# ============================================

def predict_with_model(features: dict, model_name: str = None) -> dict:
    if model_name and model_name in models and models[model_name] is not None:
        model = models[model_name]
        used_model_name = model_name
    elif current_model:
        model = current_model
        used_model_name = current_model_name
    else:
        raise HTTPException(status_code=503, detail="No models available")
    
    try:
        # CRITICAL: Preprocess features before prediction
        features_processed = preprocess_features(features)
        
        # Make prediction
        prediction = model.predict(features_processed)[0]
        
        # Get probability if available
        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(features_processed)[0][1])
        else:
            probability = float(prediction)
        
        # Determine risk level
        if prediction == 0:
            risk_level = "Low Risk"
            confidence = 1 - probability
        else:
            risk_level = "High Risk" if probability > 0.7 else "Moderate Risk"
            confidence = probability
        
        return {
            "model_used": used_model_name,
            "prediction": int(prediction),
            "probability": float(probability),
            "risk_level": risk_level,
            "confidence": float(confidence)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# ============================================
# API Endpoints (same as before)
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('api_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add these TWO new endpoints:

@app.get("/logs")
async def get_logs():
    """Simple endpoint to view logs"""
    try:
        with open("api_logs.log", "r") as f:
            logs = f.readlines()[-20:]  # Last 20 lines
        return {"logs": logs}
    except FileNotFoundError:
        return {"logs": [], "error": "Log file not found"}

@app.get("/metrics")
async def get_metrics():
    """Simple metrics endpoint"""
    import os
    import psutil
    
    log_exists = os.path.exists("api_logs.log")
    log_size = os.path.getsize("api_logs.log") if log_exists else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "log_file_size_bytes": log_size,
        "log_file_exists": log_exists,
        "api_status": "running"
    }

# Add this endpoint
@app.get("/monitor")
async def monitor():
    """Simple monitoring endpoint"""
    import os
    log_size = os.path.getsize('api_requests.log') if os.path.exists('api_requests.log') else 0
    
    return {
        "status": "monitoring_active",
        "log_file": "api_requests.log",
        "log_size_bytes": log_size,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "Heart Disease Prediction API",
        "version": "1.0.0",
        "available_models": list(models.keys()),
        "active_model": current_model_name,
        "endpoints": {
            "health": "/health",
            "models": "/models",
            "predict": "/predict",
            "predict_with_model": "/predict/{model_name}",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return {
        "status": "healthy" if current_model else "unhealthy",
        "models_loaded": model_info,
        "active_model": current_model_name or "none"
    }

@app.get("/models")
async def list_models():
    return {
        "available_models": list(models.keys()),
        "model_details": model_info,
        "current_model": current_model_name
    }

@app.post("/predict", response_model=SinglePrediction)
async def predict(features: PatientFeatures):
    # Log request
    logging.info(f"PREDICT_REQUEST: {features.dict()}")

    result = predict_with_model(features.dict())
    
    # Log response
    logging.info(f"PREDICT_RESPONSE: prediction={PredictionResult[0]}")
    
    return SinglePrediction(
        features=features,
        result=PredictionResult(**result),
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict/{model_name}", response_model=SinglePrediction)
async def predict_with_specific_model(model_name: str, features: PatientFeatures):
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    if models[model_name] is None:
        raise HTTPException(status_code=503, detail=f"Model '{model_name}' not loaded")
    
    result = predict_with_model(features.dict(), model_name)
    
    return SinglePrediction(
        features=features,
        result=PredictionResult(**result),
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)