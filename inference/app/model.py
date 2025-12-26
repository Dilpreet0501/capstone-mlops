import mlflow
import mlflow.pyfunc
import pandas as pd
from app.settings import settings

model = None


def load_model():
    global model

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    model_uri = f"models:/{settings.mlflow_model_name}@{settings.model_alias}"

    try:
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
