pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'batchpilot-api'

        PYTHON_EXE = 'C:/Users/heman/AppData/Local/Programs/Python/Python313/python.exe'

        TRIVY_EXE = 'C:/Tools/Trivy/trivy.exe'

        AWS_CLI = 'C:/Users/heman/AppData/Local/Programs/Amazon/AWSCLIV2/aws.exe'

        AWS_REGION = 'us-east-1'
        AWS_ACCOUNT_ID = '040954566436'
        ECR_REPOSITORY = 'batchpilot'
    }

    stages {
        stage('Verify Tools') {
            steps {
                bat '"%PYTHON_EXE%" --version'
                bat 'docker --version'
                bat 'docker info --format "{{.ServerVersion}}"'
                bat '"%AWS_CLI%" --version'
                bat '"%TRIVY_EXE%" --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON_EXE%" -m venv .venv-ci'
                bat '".venv-ci\\Scripts\\python.exe" -m pip install --upgrade pip'
                bat '".venv-ci\\Scripts\\python.exe" -m pip install -r requirements-dev.txt'
            }
        }

        stage('Code Quality') {
            steps {
                bat '".venv-ci\\Scripts\\python.exe" -m ruff check app tests'
            }
        }

        stage('Automated Tests') {
            steps {
                bat '".venv-ci\\Scripts\\python.exe" -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:ci-%BUILD_NUMBER% .'
            }
        }

        stage('Container Vulnerability Scan') {
            steps {
                bat '"%TRIVY_EXE%" image --scanners vuln --severity HIGH,CRITICAL --exit-code 0 %IMAGE_NAME%:ci-%BUILD_NUMBER%'
            }
        }

        stage('Publish Image to Amazon ECR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-ecr-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    bat '"%AWS_CLI%" sts get-caller-identity'

                    bat '''
                        "%AWS_CLI%" ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com
                    '''

                    bat '''
                        docker tag %IMAGE_NAME%:ci-%BUILD_NUMBER% %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY%:build-%BUILD_NUMBER%
                    '''

                    bat '''
                        docker push %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY%:build-%BUILD_NUMBER%
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'BatchPilot CI/CD image publishing completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Review the first failing stage in Console Output.'
        }
    }
}