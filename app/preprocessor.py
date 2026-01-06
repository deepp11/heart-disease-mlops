# create_preprocessor.py
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

# Based on error message, these are the categorical columns
categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']

# Create a preprocessor that matches what models expect
categorical_transformer = OneHotEncoder(
    categories=[
        [0, 1],                    # sex: [0, 1]
        [1, 2, 3, 4],             # cp: [1, 2, 3, 4]  
        [0, 1],                    # fbs: [0, 1]
        [0, 1, 2],                # restecg: [0, 1, 2]
        [0, 1],                    # exang: [0, 1]
        [1, 2, 3],                # slope: [1, 2, 3]
        [0, 1, 2, 3],             # ca: [0, 1, 2, 3]
        [3, 6, 7]                 # thal: [3, 6, 7]
    ],
    drop='first',  # Important: matches likely training setup
    sparse_output=False
)

# Create column transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', categorical_transformer, categorical_features)
    ],
    remainder='passthrough'  # Keep numeric features as-is
)

# Fit the preprocessor with dummy data (to establish categories)
dummy_data = pd.DataFrame({
    'age': [50], 'sex': [0], 'cp': [1], 'trestbps': [120], 
    'chol': [200], 'fbs': [0], 'restecg': [0], 'thalach': [150],
    'exang': [0], 'oldpeak': [1.0], 'slope': [1], 'ca': [0], 'thal': [3]
})

preprocessor.fit(dummy_data)

# Save the preprocessor
joblib.dump(preprocessor, 'preprocessor.pkl')
print("✅ Created preprocessor.pkl")
print(f"Expected features after preprocessing: {preprocessor.get_feature_names_out()}")
