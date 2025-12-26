import os
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

MODEL_NAME = os.environ["MLFLOW_MODEL_NAME"]
MODEL_ALIAS = os.environ["MODEL_ALIAS"]

client = MlflowClient()

# Resolve model version via registry
mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
run_id = mv.run_id

print(f"Resolved run_id: {run_id}")

# 🔥 IMPORTANT: use models:/ not runs:/
model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
print(f"Loading model from {model_uri}")

# This works via REST + serve-artifacts
model = mlflow.pyfunc.load_model(model_uri)

print("✅ Model loaded successfully")
