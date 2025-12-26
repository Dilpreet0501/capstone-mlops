import os
import mlflow

tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
model_name = os.environ["MLFLOW_MODEL_NAME"]
model_alias = os.environ["MODEL_ALIAS"]

mlflow.set_tracking_uri(tracking_uri)
client = mlflow.MlflowClient()

# Resolve alias → run_id
mv = client.get_model_version_by_alias(model_name, model_alias)
run_id = mv.run_id

print(f"Resolved run_id: {run_id}")

# Directly load known artifact path
model_uri = f"runs:/{run_id}/sklearn-model"
print(f"Loading model from {model_uri}")

mlflow.pyfunc.load_model(model_uri)

print("✅ Model fetched successfully")
