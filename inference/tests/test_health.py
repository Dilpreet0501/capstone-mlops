import requests

def test_health():
    r = requests.get("http://localhost:8000/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True

def test_predict():
    payload = {
        "features": {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.02381,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }
    }
    r = requests.post("http://localhost:8000/predict", json=payload)
    assert r.status_code == 200
    assert "prediction" in r.json()