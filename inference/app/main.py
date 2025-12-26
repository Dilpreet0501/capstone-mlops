from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from app.model import load_model, predict
from app.schemas import PredictionRequest, PredictionResponse

app = FastAPI(title="Inference Service")

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def startup_event():
    load_model()

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}

@app.post("/predict", response_model=PredictionResponse)
def predict_price(request: PredictionRequest):
    try:
        pred = predict(request.features)
        return PredictionResponse(prediction=pred)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
