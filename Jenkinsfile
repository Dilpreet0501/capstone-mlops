pipeline {
    agent any

    environment {
        IMAGE_NAME = "california-inference"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Inference Image') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME ./inference
                '''
            }
        }

        stage('Test API') {
            steps {
                sh '''
                docker run -d --name test-api \
                  -p 8000:8000 \
                  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
                  -e MLFLOW_MODEL_NAME=california_housing_model \
                  -e MODEL_ALIAS=production \
                  $IMAGE_NAME

                sleep 15
                curl http://localhost:8000/health
                docker rm -f test-api
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploy step (docker-compose / k8s / server)"
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f || true'
        }
    }
}
