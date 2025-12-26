import mlflow
import os
import shutil

MLFLOW_TRACKING_URI = "http://mlflow:5000"
MODEL_NAME = "california_housing_model"
MODEL_ALIAS = "production"

DEST_DIR = "inference/model"
os.makedirs(DEST_DIR, exist_ok=True)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
local_path = mlflow.artifacts.download_artifacts(model_uri)

# Copy ONNX model
for root, dirs, files in os.walk(local_path):
    for file in files:
        if file.endswith(".onnx"):
            shutil.copy(
                os.path.join(root, file),
                os.path.join(DEST_DIR, "model.onnx")
            )
            print("✅ ONNX model copied")
