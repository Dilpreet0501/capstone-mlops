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
                docker build -t fetch-mlflow-model -f jenkins/Dockerfile.fetch_model .
                docker run --rm \
                    -v mlruns:/mlruns \
                    -e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
                    -e MLFLOW_MODEL_NAME=california_housing_model \
                    -e MODEL_ALIAS=production \
                    fetch-mlflow-model
                '''
            }
            }




        stage('Build Inference Image') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME -f inference/Dockerfile .
                '''
            }
        }

        stage('Test API') {
            steps {
                sh '''
                docker run -d --name $CONTAINER_NAME -p 0:8000 \
                  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
                  -e MLFLOW_MODEL_NAME=$MLFLOW_MODEL_NAME \
                  -e MODEL_ALIAS=$MODEL_ALIAS \
                  $IMAGE_NAME

                sleep 20

                docker logs $CONTAINER_NAME || true

                PORT=$(docker port $CONTAINER_NAME 8000/tcp | cut -d: -f2)

                curl http://localhost:$PORT/health

                docker rm -f $CONTAINER_NAME
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker rm -f inference-prod || true

                docker run -d --name inference-prod -p 8000:8000 \
                  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
                  -e MLFLOW_MODEL_NAME=$MLFLOW_MODEL_NAME \
                  -e MODEL_ALIAS=$MODEL_ALIAS \
                  $IMAGE_NAME
                '''
            }
        }
    }

    post {
        always {
            sh '''
            docker system prune -f || true
            '''
        }

        success {
            echo "Pipeline completed successfully"
        }

        failure {
            echo "Pipeline failed"
        }
    }
}
