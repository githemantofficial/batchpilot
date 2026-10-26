pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'batchpilot-api'
    }

    stages {

        stage('Verify Tools') {
            steps {
                bat 'py -3 --version'
                bat 'docker --version'
                bat 'docker info --format "{{.ServerVersion}}"'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'py -3 -m venv .venv-ci'
                bat '.venv-ci\\Scripts\\python.exe -m pip install --upgrade pip'
                bat '.venv-ci\\Scripts\\python.exe -m pip install -r requirements-dev.txt'
            }
        }

        stage('Code Quality') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe -m ruff check app tests'
            }
        }

        stage('Automated Tests') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:ci-%BUILD_NUMBER% .'
            }
        }
    }

    post {
        success {
            echo 'BatchPilot CI pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Review the console output.'
        }
    }
}