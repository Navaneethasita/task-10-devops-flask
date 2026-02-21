pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "navaneetha4/flask-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Navaneethasita/task-10-devops-flask.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $DOCKER_IMAGE:$IMAGE_TAG .
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                trivy image --exit-code 1 --severity CRITICAL $DOCKER_IMAGE:$IMAGE_TAG
                '''
            }
        }

        stage('Debug Kubernetes Access') {
            steps {
                sh '''
                whoami
                echo "HOME=$HOME"
                ls -la ~/.kube
                kubectl get nodes
                '''
            }
        }        

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                docker push $DOCKER_IMAGE:$IMAGE_TAG
                '''
            }
        }

        stage('Deploy to Kubernetes using Helm') {
            steps {
                sh '''
                helm upgrade --install flask-app ./helm/flask-app \
                --set image.repository=$DOCKER_IMAGE \
                --set image.tag=$IMAGE_TAG
                '''
            }
        }
    }

    post {
        success {
            echo "Deployment Successful 🚀"
        }
        failure {
            echo "Pipeline Failed ❌"
        }
        always {
            sh 'docker image prune -f'
        }
    }
}
