pipeline {
    agent any

    environment {
        AWS_REGION     = 'us-east-1'
        ECR_REGISTRY   = '034363017905.dkr.ecr.us-east-1.amazonaws.com'
        EC2_HOST       = '44.213.82.44'
        EC2_USER       = 'ec2-user'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('AWS ECR Login') {
            steps {
                // Ensure the Jenkins server has the AWS CLI installed and configured.
                // Or use Jenkins AWS credentials plugin.
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
                '''
            }
        }

        stage('Build & Push Backend') {
            steps {
                dir('backend') {
                    sh '''
                        docker build -t cafeteria-backend:latest .
                        docker tag cafeteria-backend:latest $ECR_REGISTRY/cafeteria-backend:latest
                        docker push $ECR_REGISTRY/cafeteria-backend:latest
                    '''
                }
            }
        }

        stage('Build & Push Customer UI') {
            steps {
                dir('customer') {
                    sh '''
                        docker build --build-arg NEXT_PUBLIC_API_URL=http://$EC2_HOST:8000 -t cafeteria-customer:latest .
                        docker tag cafeteria-customer:latest $ECR_REGISTRY/cafeteria-customer:latest
                        docker push $ECR_REGISTRY/cafeteria-customer:latest
                    '''
                }
            }
        }

        stage('Build & Push Merchant UI') {
            steps {
                dir('merchant') {
                    sh '''
                        docker build --build-arg NEXT_PUBLIC_API_URL=http://$EC2_HOST:8000 -t cafeteria-merchant:latest .
                        docker tag cafeteria-merchant:latest $ECR_REGISTRY/cafeteria-merchant:latest
                        docker push $ECR_REGISTRY/cafeteria-merchant:latest
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                // To do this securely, use the SSH Agent plugin in Jenkins and bind your EC2 SSH Key.
                sshagent(['ec2-ssh-credentials-id']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST << 'EOF'
                            echo "Pulling new images..."
                            sudo docker-compose pull
                            echo "Starting updated containers..."
                            sudo docker-compose up -d
                            echo "Done!"
EOF
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
