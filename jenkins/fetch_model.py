import mlflow
import os

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

model_name = os.environ["MLFLOW_MODEL_NAME"]
model_alias = os.environ.get("MODEL_ALIAS", "production")

model_uri = f"models:/{model_name}@{model_alias}"

print(f"Fetching model from {model_uri}")
mlflow.pyfunc.load_model(model_uri)
print("Model fetched successfully")
