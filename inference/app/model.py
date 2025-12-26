import os
import mlflow
import mlflow.pyfunc
import pandas as pd
from app.settings import settings

model = None


def load_model():
    global model

    # 1. Self-contained image loading: Search for the MLflow model locally
    model_path = None
    # We search the app directory for an 'MLmodel' file which indicates an MLflow flavor
    for root, dirs, files in os.walk("/app"):
        if "MLmodel" in files:
            model_path = root
            break
            
    if model_path:
        try:
            print(f"Loading local model from: {model_path}")
            model = mlflow.pyfunc.load_model(model_path)
            print("✅ Model loaded successfully from local artifact")
            return
        except Exception as e:
            print(f"⚠️ Failed to load local model from {model_path}: {e}")

    # 2. Remote Fallback: Load from MLflow Tracking Server
    print("No local model found or failed to load; falling back to MLflow Server")
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    model_uri = f"models:/{settings.mlflow_model_name}@{settings.model_alias}"

    try:
        print(f"Loading model from MLflow URI: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        print(f"✅ Model loaded successfully from MLflow: {model_uri}")
    except Exception as e:
        model = None
        print(f"❌ Critical: Failed to load model from any source: {model_uri}")
        raise e


def predict(features: dict) -> float:
    if model is None:
        raise RuntimeError("Model is not loaded. Cannot run prediction.")

    df = pd.DataFrame([features])
    prediction = model.predict(df)

    return float(prediction[0])
