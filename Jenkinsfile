pipeline {
    agent any

    environment {
        IMAGE_NAME = "navaneetha4/flask-app"
        IMAGE_TAG  = "latest"
        CHART_DIR  = "./helm/flask-app"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Navaneethasita/task-10-devops-flask.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t $IMAGE_NAME:$IMAGE_TAG .
                """
            }
        }

        stage('Scan Image with Trivy') {
            steps {
                sh """
                    trivy image --severity HIGH,CRITICAL $IMAGE_NAME:$IMAGE_TAG || true
                """
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds', 
                    usernameVariable: 'DOCKER_USER', 
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh 'docker push $IMAGE_NAME:$IMAGE_TAG'
            }
        }

        stage('Test Credentials') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'aws-creds',
                    usernameVariable: 'AWS_ACCESS_KEY_ID',
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    sh 'aws sts get-caller-identity'
                }
        
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_USER'
                }
            }
        }
        
        stage('Deploy to Kubernetes using Helm') {
            steps {
                // Use AWS credentials for EKS authentication
                withCredentials([usernamePassword(
                    credentialsId: 'aws-creds', 
                    usernameVariable: 'AWS_ACCESS_KEY_ID', 
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    sh """
                        export AWS_DEFAULT_REGION=ap-south-1
                        aws sts get-caller-identity
                        helm upgrade --install flask-app $CHART_DIR \\
                            --set image.repository=$IMAGE_NAME \\
                            --set image.tag=$IMAGE_TAG
                    """
                }
                {
                    sh """
                        NODEPORT=\$(kubectl get svc flask-app -o jsonpath='{.spec.ports[0].nodePort}')
                        PUBLIC_IP=\$(aws ec2 describe-instances \\
                            --instance-ids \$(curl -s http://169.254.169.254/latest/meta-data/instance-id) \\
                            --query 'Reservations[0].Instances[0].PublicIpAddress' \\
                            --output text)
                        echo "✅ Your Flask app is live at: http://\$PUBLIC_IP:\$NODEPORT"
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f'
        }
        success {
            echo "Pipeline Succeeded ✅"
        }
        failure {
            echo "Pipeline Failed ❌"
        }
    }
}
