import os
import mlflow

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

MODEL_NAME = os.environ["MLFLOW_MODEL_NAME"]
MODEL_ALIAS = os.environ["MODEL_ALIAS"]

client = mlflow.tracking.MlflowClient()

# Resolve alias → model version
mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
run_id = mv.run_id

print(f"Resolved run_id: {run_id}")

# List artifacts for this run
artifacts = client.list_artifacts(run_id)
print("Available artifacts:", [a.path for a in artifacts])

# Find the folder that contains MLmodel
model_path = None
for artifact in artifacts:
    sub_artifacts = client.list_artifacts(run_id, artifact.path)
    for sub in sub_artifacts:
        if sub.path.endswith("MLmodel"):
            model_path = artifact.path
            break
    if model_path:
        break

if not model_path:
    raise RuntimeError("❌ No valid MLflow model artifact found")

model_uri = f"runs:/{run_id}/{model_path}"

print(f"✅ Final model URI: {model_uri}")

mlflow.pyfunc.load_model(model_uri)
print("✅ Model fetched successfully")
