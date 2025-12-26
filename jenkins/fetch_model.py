import os
import shutil
import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = os.environ["MLFLOW_MODEL_NAME"]
MODEL_ALIAS = os.environ.get("MODEL_ALIAS", "production")
# DEST_DIR should be relative to the workspace to be preserved
DEST_DIR = os.environ.get("DEST_DIR", "inference/model/production")

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(tracking_uri)

client = MlflowClient()

def fetch_model():
    print(f"Fetching model: {MODEL_NAME} ({MODEL_ALIAS})")

    try:
        # Use standard model URI scheme
        model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
        
        if os.path.exists(DEST_DIR):
            print(f"Cleaning up old model at {DEST_DIR}")
            shutil.rmtree(DEST_DIR)
        
        os.makedirs(os.path.dirname(DEST_DIR), exist_ok=True)

        print(f"Downloading artifact from {model_uri} to {DEST_DIR}")
        local_path = mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=DEST_DIR
        )

        print(f"✅ Model downloaded to {local_path}")
    except Exception as e:
        print(f"❌ Failed to fetch model: {e}")
        raise e

if __name__ == "__main__":
    fetch_model()
