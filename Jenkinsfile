```groovy
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
    }

    stages {
        stage('Verify Tools') {
            steps {
                bat '"%PYTHON_EXE%" --version'
                bat 'docker --version'
                bat 'docker info --format "{{.ServerVersion}}"'
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
```