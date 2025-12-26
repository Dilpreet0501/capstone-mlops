pipeline {
    agent any

    environment {
        IMAGE_NAME = "cal_housing_api:latest"
    }

    stages {

        stage("Checkout") {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Dilpreet0501/capstone-mlops.git'
            }
        }

    stage('Fetch Production Model') {
      steps {
            sh '''
            docker build -t fetch-mlflow-model -f jenkins/Dockerfile.fetch_model .
            docker run --rm \
            -e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
            -e MLFLOW_MODEL_NAME=california_housing_model \
            -e MODEL_ALIAS=production \
            fetch-mlflow-model

            '''
        }
    }


        stage("Build Docker Image") {
            steps {
                sh '''
                docker build -t $IMAGE_NAME ./inference
                '''
            }
        }

        stage("Test API") {
            steps {
                sh '''
                docker run -d -p 8000:8000 --name test_api $IMAGE_NAME
                sleep 10
                pytest inference/tests
                docker rm -f test_api
                '''
            }
        }

        stage("Deploy") {
            steps {
                sh '''
                docker-compose down
                docker-compose up -d inference
                '''
            }
        }
    }
}
