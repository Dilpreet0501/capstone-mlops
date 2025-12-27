pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    environment {
        IMAGE_NAME = "cal_housing_api"
        IMAGE_TAG  = "latest"
        CONTAINER_NAME = "test-api"
        
        MLFLOW_TRACKING_URI = "http://mlflow:5000"
        MLFLOW_MODEL_NAME  = "california_housing_model"
        MODEL_ALIAS        = "production"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Model Fetch') {
            steps {
                sh '''
                # Build the fetcher image
                docker build -t fetch-mlflow-model -f jenkins/Dockerfile.fetch_model .
                
                # Cleanup potential stale container
                docker rm -f model-fetcher || true

                # Run the container to fetch the model
                # We use the docker_default network to reach the mlflow container
                docker run --name model-fetcher \
                    --network docker_default \
                    -v docker_mlruns:/mlruns \
                    -e MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
                    -e MLFLOW_MODEL_NAME=${MLFLOW_MODEL_NAME} \
                    -e MODEL_ALIAS=${MODEL_ALIAS} \
                    -e DEST_DIR=model \
                    fetch-mlflow-model

                # Clean up local workspace model directory
                rm -rf model
                
                # Pull the model from the container to the local workspace
                docker cp model-fetcher:/app/model .
                
                # Prepare the inference directory for the Docker build context (Bake-in)
                rm -rf inference/model
                cp -r model/ inference/model
                
                # Cleanup fetcher container
                docker rm -f model-fetcher
                
                # Verify files exist in the workspace for the build stage
                ls -R inference/model
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                # Build the Docker image for the API
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f inference/Dockerfile inference/
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                # Run a quick unit test with pytest to verify the containerized app
                docker rm -f ${CONTAINER_NAME} || true
                
                # Start the container (no port mapping needed as tests run inside)
                docker run -d --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}
                
                # Wait for API to be ready
                sleep 15
                
                # Run pytest inside the container
                docker exec ${CONTAINER_NAME} pytest tests/
                
                # Cleanup
                docker rm -f ${CONTAINER_NAME}
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                # Update the running service using the newly built image
                cd docker && docker-compose up -d api
                '''
            }
        }
    }

    post {
        always {
            sh "docker system prune -f || true"
        }
        success {
            echo "Pipeline completed successfully"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}