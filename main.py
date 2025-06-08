from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_controller import router as auth_router
from model_Controller import get_top_4_predictions  # Just importing logic, not app

import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "FastAPI Backend is running with Auth and Prediction APIs!"}

# Disease prediction endpoint
@app.get("/predict", tags=["Prediction"])
async def predict():
    try:
        data = pd.read_csv('synthetic_soil_data_maharashtra_with_disease.csv')
        sample_row = data.iloc[[1023]]  # You can update this to be dynamic later

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
