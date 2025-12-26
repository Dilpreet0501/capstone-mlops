import os
import shutil
import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = os.environ["MLFLOW_MODEL_NAME"]
MODEL_ALIAS = os.environ.get("MODEL_ALIAS", "production")
DEST_DIR = "model_dir"

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(tracking_uri)

client = MlflowClient()

def fetch_model():
    print(f"Fetching model: {MODEL_NAME} ({MODEL_ALIAS})")

    mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
    run_id = mv.run_id

    print(f"Resolved run_id: {run_id}")

    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    # 🔥 THIS IS THE KEY FIX 🔥
    local_path = mlflow.artifacts.download_artifacts(
        run_id=run_id,
        artifact_path="sklearn-model",
        dst_path=DEST_DIR
    )

    print(f"✅ Model downloaded to {local_path}")

if __name__ == "__main__":
    fetch_model()
