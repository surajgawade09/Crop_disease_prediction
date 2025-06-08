import requests

url = "http://127.0.0.1:8000/predict"
data = {
    "pH": 6.5, "N": 50, "P": 20, "K": 30,
    "EC": 0.5, "OC": 1.2, "SoilMoisture": 25, "Humidity": 60
}
response = requests.post(url, json=data)

print(response.json())
