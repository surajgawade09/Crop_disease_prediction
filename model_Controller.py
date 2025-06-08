from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import pickle
import xgboost as xgb

# === Load all required models and encoders ===
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('label_encoder_disease.pkl', 'rb') as f:
    le_disease = pickle.load(f)

with open('label_encoder_crop.pkl', 'rb') as f:
    le_crop = pickle.load(f)

# === FastAPI App Setup ===
app = FastAPI()

origins = [
    "*",  # Allow all for testing; restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI Disease Prediction API is running!"}


# === Data Preparation and Prediction Logic ===

def prepare_input_data(data_row):
    processed_data = data_row.copy()
    crop_name = processed_data['Crop'].iloc[0]
    crop_encoded = le_crop.transform([crop_name])[0]

    final_data = pd.DataFrame({
        'Soil_pH': processed_data['Soil_pH'],
        'N_kg_ha': processed_data['N_kg_ha'],
        'P_kg_ha': processed_data['P_kg_ha'],
        'K_kg_ha': processed_data['K_kg_ha'],
        'EC_dS_m': processed_data['EC_dS_m'],
        'OC_percent': processed_data['OC_percent'],
        'Soil_Moisture_percent': processed_data['Soil_Moisture_percent'],
        'Humidity_percent': processed_data['Humidity_percent'],
        'Crop': crop_encoded
    })
    return final_data

def get_top_4_predictions(data_row):
    processed_data = prepare_input_data(data_row)
    scaled_data = scaler.transform(processed_data)
    dtest = xgb.DMatrix(scaled_data)
    probabilities = model.predict(dtest)
    top_4_indices = np.argsort(probabilities[0])[-4:][::-1]
    top_4_probs = probabilities[0][top_4_indices]
    disease_names = le_disease.inverse_transform(top_4_indices)
    return list(zip(disease_names, top_4_probs))


# === API Endpoint ===

@app.get("/predict")
async def predict():
    try:
        # Load row from CSV
        data = pd.read_csv('synthetic_soil_data_maharashtra_with_disease.csv')
        sample_row = data.iloc[[10234]]  # You can make this dynamic with a request param

        predictions = get_top_4_predictions(sample_row)

        return {
            "input_crop": sample_row['Crop'].iloc[0],
            "actual_disease": sample_row['Disease'].iloc[0],
            "predictions": [
                {"disease": disease, "probability": round(float(prob), 4)}
                for disease, prob in predictions
            ]
        }
    except Exception as e:
        return {"error": str(e)}
