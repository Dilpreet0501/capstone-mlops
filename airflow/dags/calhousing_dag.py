from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import json
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


DATA_PATH = "/opt/airflow/data/raw/raw_data.csv"
SCHEMA_PATH = "/opt/airflow/include/schema.json"


def ingest_data():
    data = fetch_california_housing(as_frame=True)
    df = data.frame
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)


def validate_data():
    df = pd.read_csv(DATA_PATH)

    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    if list(df.columns) != schema["columns"]:
        raise ValueError("Schema mismatch detected")

    if df.isnull().any().any():
        raise ValueError("Null values detected")


def train_and_log_model():
    df = pd.read_csv(DATA_PATH)

    X = df.drop("MedHouseVal", axis=1)
    y = df["MedHouseVal"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    mlflow.set_experiment(os.environ["MLFLOW_EXPERIMENT_NAME"])

    with mlflow.start_run():
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mse = mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)

        mlflow.sklearn.log_model(
            model,
            artifact_path="sklearn-model",
            registered_model_name="california_housing_model"
        )

        initial_type = FloatTensorType([None, X.shape[1]])
        onnx_model = convert_sklearn(model, initial_types=[("float_input", initial_type)])

        with open("model.onnx", "wb") as f:
            f.write(onnx_model.SerializeToString())

        mlflow.log_artifact("model.onnx")

with DAG(
    dag_id="california_housing_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["mlops", "training"],
) as dag:

    ingest = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_data
    )

    validate = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data
    )

    train = PythonOperator(
        task_id="train_and_log_model",
        python_callable=train_and_log_model
    )

    ingest >> validate >> train
