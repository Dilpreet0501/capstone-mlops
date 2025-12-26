from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mlflow_tracking_uri: str = Field(..., env="MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field(..., env="MLFLOW_EXPERIMENT_NAME")
    mlflow_model_name: str = Field(..., env="MLFLOW_MODEL_NAME")
    model_alias: str = Field(..., env="MODEL_ALIAS")

settings = Settings()
