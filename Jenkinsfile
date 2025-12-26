pipeline {
    agent any

    environment {
        IMAGE_NAME = "california-inference"
        CONTAINER_NAME = "test-api"

        MLFLOW_TRACKING_URI = "http://host.docker.internal:5001"
        MLFLOW_MODEL_NAME  = "california_housing_model"
        MODEL_ALIAS        = "production"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Fetch Production Model') {
            steps {
                sh '''
                echo "Building MLflow fetch image..."
                docker build -t fetch-mlflow-model -f jenkins/Dockerfile.fetch_model .

                echo "Fetching production model from MLflow..."
                docker run --rm \
                  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
                  -e MLFLOW_MODEL_NAME=$MLFLOW_MODEL_NAME \
                  -e MODEL_ALIAS=$MODEL_ALIAS \
                  fetch-mlflow-model
                '''
            }
        }

        stage('Build Inference Image') {
            steps {
                sh '''
                echo "Building inference Docker image..."
                docker build -t $IMAGE_NAME -f inference/Dockerfile .
                '''
            }
        }

        stage('Test API') {
            steps {
                sh '''
                echo "Starting inference container..."
                docker run -d --name $CONTAINER_NAME -p 0:8000 \
                  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
                  -e MLFLOW_MODEL_NAME=$MLFLOW_MODEL_NAME \
                  -e MODEL_ALIAS=$MODEL_ALIAS \
                  $IMAGE_NAME

                echo "Waiting for API to start..."
                sleep 20

                echo "Checking container status..."
                docker ps
                docker logs $CONTAINER_NAME || true

                PORT=$(docker port $CONTAINER_NAME 8000/tcp | cut -d: -f2)
                echo "API is running on port $PORT"

                echo "Calling health endpoint..."
                curl http://localhost:$PORT/health

                echo "Stopping test container..."
                docker rm -f $CONTAINER_NAME
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                echo "Deploying inference service..."

                docker rm -f inference-prod || true

                docker run -d --name inference-prod -p 8000:8000 \
                  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
                  -e MLFLOW_MODEL_NAME=$MLFLOW_MODEL_NAME \
                  -e MODEL_ALIAS=$MODEL_ALIAS \
                  $IMAGE_NAME

                echo "Deployment successful"
                '''
            }
        }
    }

    post {
        always {
            echo "Cleaning up Docker resources..."
            docker system prune -f || true
        }

        success {
            echo "Pipeline completed successfully "
        }

        failure {
            echo "Pipeline failed "
        }
    }
}
