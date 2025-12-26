import os
import mlflow
import mlflow.pyfunc
import pandas as pd
from app.settings import settings

model = None


def load_model():
    global model

    # 1. Try to load from local directory first (self-contained image)
    # Check common locations in the container
    possible_paths = [
        "./model/production",
        "/app/model/production",
        "./model",
        "/app/model"
    ]
    
    print(f"Checking for local model in: {possible_paths}")
    
    for local_path in possible_paths:
        if os.path.exists(local_path):
            print(f"Found path: {local_path}. Contents: {os.listdir(local_path) if os.path.isdir(local_path) else 'Not a dir'}")
            try:
                # MLflow models are directories containing MLmodel file
                if os.path.isdir(local_path) and "MLmodel" in os.listdir(local_path):
                    print(f"Attempting to load MLflow model from: {local_path}")
                    model = mlflow.pyfunc.load_model(local_path)
                    print("✅ Model loaded successfully from local path")
                    return
                elif os.path.isdir(local_path):
                    # Check one level deeper (sometimes mlflow creates a subfolder like 'sklearn-model')
                    for sub in os.listdir(local_path):
                        sub_path = os.path.join(local_path, sub)
                        if os.path.isdir(sub_path) and "MLmodel" in os.listdir(sub_path):
                            print(f"Attempting to load MLflow model from subfolder: {sub_path}")
                            model = mlflow.pyfunc.load_model(sub_path)
                            print("✅ Model loaded successfully from subfolder")
                            return
            except Exception as e:
                print(f"Failed to load from {local_path}: {e}")

    # 2. Fallback to MLflow tracking server
    print("No valid local model found, falling back to MLflow Tracking Server")
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
