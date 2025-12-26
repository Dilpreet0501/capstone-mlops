import os
import mlflow

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

MODEL_NAME = os.environ["MLFLOW_MODEL_NAME"]
MODEL_ALIAS = os.environ["MODEL_ALIAS"]

client = mlflow.tracking.MlflowClient()

# Resolve alias -> model version
mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)

run_id = mv.run_id

# IMPORTANT: extract actual artifact folder name (sklearn-model)
artifact_path = mv.source.split("/")[-1]

model_uri = f"runs:/{run_id}/{artifact_path}"

print(f"Resolved model URI: {model_uri}")

mlflow.pyfunc.load_model(model_uri)

print("✅ Model fetched successfully")
