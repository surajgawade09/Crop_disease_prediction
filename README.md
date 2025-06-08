# Crop Disease Prediction API

This project provides a FastAPI-based API for predicting crop diseases based on soil and environmental parameters.

## Features

- Disease prediction for various crops
- Authentication system
- RESTful API endpoints
- Machine learning model integration

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd Crop_disease_prediction
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /`: Root endpoint
- `GET /predict`: Get disease predictions
- `POST /auth/login`: User login
- `POST /auth/register`: User registration
- `GET /auth/user/{phone}`: Get user details
- `POST /auth/update_user`: Update user information

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Technologies Used

- FastAPI
- XGBoost
- Pandas
- NumPy
- PyMySQL
- Passlib 