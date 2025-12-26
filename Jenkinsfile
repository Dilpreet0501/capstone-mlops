pipeline {
    agent any

    environment {
        IMAGE_NAME = "cal_housing_api:latest"
    }

    stages {

        stage("Checkout") {
            steps {
                git branch: 'main',
                    url: 'https://github.com/your-username/capstone-mlops.git'
            }
        }

        stage("Fetch Production Model") {
            steps {
                sh '''
                python3 jenkins/fetch_model.py
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
