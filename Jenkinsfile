pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t booknest-ci .'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'docker run --rm booknest-ci python -m pytest test_app.py -v'
            }
        }
        stage('Deploy with Ansible') {
            steps {
                sh 'docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /deploy.yml'
            }
        }
    }

    post {
        success { echo 'BookNest pipeline completed successfully!' }
        failure { echo 'BookNest pipeline FAILED - check the console output.' }
    }
}
