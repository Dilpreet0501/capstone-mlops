from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import json
import pandas as pd
import mlflow
import mlflow.sklearn
import requests
import tarfile
import io

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


DATA_PATH = "/opt/airflow/data/raw/raw_data.csv"
SCHEMA_PATH = "/opt/airflow/include/schema.json"
SKLEARN_DATA_PATH = "/opt/airflow/data/sklearn"


def ingest_data():
    os.makedirs(SKLEARN_DATA_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    
    # URL for sklearn source
    url = "https://ndownloader.figshare.com/files/5976036"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        print(f"Attempting to download dataset from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
    
        tar_path = os.path.join(SKLEARN_DATA_PATH, "cal_housing.tgz")
        with open(tar_path, "wb") as f:
            f.write(response.content)
            
        print("Successfully downloaded tgz file. Loading with fetch_california_housing.")
        data = fetch_california_housing(as_frame=True, data_home=SKLEARN_DATA_PATH)
        df = data.frame
        
    except Exception as e:
        print(f"Primary download failed: {e}. Falling back to Github mirror.")
        
        fallback_url = "https://raw.githubusercontent.com/ageron/handson-ml/master/datasets/housing/housing.csv"
        df_raw = pd.read_csv(fallback_url)
        
        
        df = pd.DataFrame()
        df['MedInc'] = df_raw['median_income']
        df['HouseAge'] = df_raw['housing_median_age']
        df['AveRooms'] = df_raw['total_rooms'] / df_raw['households']
        df['AveBedrms'] = df_raw['total_bedrooms'] / df_raw['households']
        df['Population'] = df_raw['population']
        df['AveOccup'] = df_raw['population'] / df_raw['households']
        df['Latitude'] = df_raw['latitude']
        df['Longitude'] = df_raw['longitude']
        df['MedHouseVal'] = df_raw['median_house_value'] / 100000.0
        
        
        df = df.dropna()

    print(f"Saving {len(df)} rows to {DATA_PATH}")
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
