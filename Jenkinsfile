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
                    -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                    -e MLFLOW_MODEL_NAME=${MLFLOW_MODEL_NAME} \
                    -e MODEL_ALIAS=${MODEL_ALIAS} \
                    -e DEST_DIR=model \
                    fetch-mlflow-model

                # Pull the model to a local directory in the workspace
                rm -rf model
                docker cp model-fetcher:/app/model .
                
                # Move/Copy to inference directory for Docker build context
                rm -rf inference/model
                cp -r model inference/model
                
                docker rm -f model-fetcher
                
                # Verify files exist
                ls -R model
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
                
                # Start the container
                docker run -d --name ${CONTAINER_NAME} -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}
                
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
                # Update the running service
                cd docker && docker-compose down && docker-compose up -d api
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