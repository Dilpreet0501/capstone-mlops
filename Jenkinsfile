pipeline {
    agent any

    environment {
        IMAGE_NAME = "california-inference"
        CONTAINER_NAME = "test-api"

        MLFLOW_TRACKING_URI = "http://host.docker.internal:5001"
        MLFLOW_EXPERIMENT_NAME = "california-housing"
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
                
                # Cleanup potential stale container
                docker rm -f model-fetcher || true

                # Run the container to fetch the model
                docker run --name model-fetcher \
                    -v docker_mlruns:/mlruns \
                    -e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
                    -e MLFLOW_MODEL_NAME=california_housing_model \
                    -e MODEL_ALIAS=production \
                    -e DEST_DIR=inference/model/production \
                    fetch-mlflow-model

                # Explicitly cleanup the local directory to ensure a fresh copy
                rm -rf inference/model/production
                mkdir -p inference/model/production
                
                # Copy the artifacts out of the container
                docker cp model-fetcher:/app/inference/model/production/. inference/model/production/
                
                docker rm -f model-fetcher

                # Verify files exist on the host
                ls -R inference/model/production
                '''
            }
        }




        stage('Build Inference Image') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME -f inference/Dockerfile inference/
                '''
            }
        }

        stage('Test API') {
            steps {
                sh '''
                docker run -d --name $CONTAINER_NAME -p 0:8000 \
                  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
                  -e MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME \
                  -e MLFLOW_MODEL_NAME=$MLFLOW_MODEL_NAME \
                  -e MODEL_ALIAS=$MODEL_ALIAS \
                  $IMAGE_NAME

                sleep 20

                docker logs $CONTAINER_NAME || true

                # Use container IP for testing to avoid localhost/mapping issues in CI
                IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_NAME)
                
                curl http://$IP:8000/health

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
                  -e MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME \
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
