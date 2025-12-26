import os
import mlflow
import mlflow.pyfunc
import pandas as pd
from app.settings import settings

model = None


def load_model():
    global model

    # 1. Try to load from local directory first (self-contained image)
    local_model_path = "./model/production"
    if os.path.exists(local_model_path):
        try:
            print(f"Loading model from local path: {local_model_path}")
            model = mlflow.pyfunc.load_model(local_model_path)
            print("Model loaded successfully from local path")
            return
        except Exception as e:
            print(f"Failed to load from local path: {e}")

    # 2. Fallback to MLflow tracking server
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    model_uri = f"models:/{settings.mlflow_model_name}@{settings.model_alias}"

    try:
        print(f"Loading model from MLflow: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        print(f"Model loaded from {model_uri}")
    except Exception as e:
        model = None
        print(f"Failed to load model from {model_uri}")
        raise e


def predict(features: dict) -> float:
    if model is None:
        raise RuntimeError("Model is not loaded. Cannot run prediction.")

    df = pd.DataFrame([features])
    prediction = model.predict(df)

    return float(prediction[0])
