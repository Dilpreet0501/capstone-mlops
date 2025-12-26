import os
import mlflow
import mlflow.pyfunc
import pandas as pd
from app.settings import settings

model = None


def load_model():
    global model

    print("--- Model Loading Debug ---")
    print(f"Current working directory: {os.getcwd()}")
    
    # Foolproof recursive search for MLflow model (contains MLmodel file)
    model_path = None
    search_root = "/app"
    print(f"Searching for MLflow model in {search_root}...")
    
    for root, dirs, files in os.walk(search_root):
        if "MLmodel" in files:
            model_path = root
            print(f"✅ Found MLflow model at: {model_path}")
            break
            
    if model_path:
        try:
            model = mlflow.pyfunc.load_model(model_path)
            print(f"Successfully loaded model from: {model_path}")
            return
        except Exception as e:
            print(f"Failed to load from {model_path}: {e}")

    # 2. Fallback to MLflow tracking server
    print("No valid local model found in image, falling back to MLflow Tracking Server")
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    model_uri = f"models:/{settings.mlflow_model_name}@{settings.model_alias}"

    try:
        print(f"Loading model from MLflow: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        print(f"✅ Model loaded from {model_uri}")
    except Exception as e:
        model = None
        print(f"❌ Failed to load model from {model_uri}")
        raise e


def predict(features: dict) -> float:
    if model is None:
        raise RuntimeError("Model is not loaded. Cannot run prediction.")

    df = pd.DataFrame([features])
    prediction = model.predict(df)

    return float(prediction[0])
