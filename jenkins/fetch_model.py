import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://host.docker.internal:5001")

client = MlflowClient()

mv = client.get_model_version_by_alias(
    "california_housing_model", "production"
)

run_id = mv.run_id
model_uri = f"runs:/{run_id}/sklearn-model"

print("Loading model from", model_uri)
mlflow.pyfunc.load_model(model_uri)
print("✅ Model loaded successfully")
