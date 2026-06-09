pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "orakzaieesa11"
        IMAGE_UNSTABLE = "${DOCKERHUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE   = "${DOCKERHUB_USER}/sentiment-api:stable"
        CONTAINER_NAME = "sentiment-app"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    # Stop and remove any existing container
                    docker stop ${CONTAINER_NAME} || true
                    docker rm   ${CONTAINER_NAME} || true

                    # Build the unstable image from main branch
                    docker build -t ${IMAGE_UNSTABLE} .

                    # Run the container detached
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 5000:5000 \
                        -v /app/logs:/app/logs \
                        ${IMAGE_UNSTABLE}

                    # Wait for the app to be ready
                    sleep 20
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    # Run PyTest tests inside a temporary container
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -v $(pwd)/tests:/tests \
                        ${IMAGE_UNSTABLE} \
                        bash -c "pip install pytest requests -q && pytest /tests/test_api.py -v"
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    # Run Selenium UI tests inside a temporary container
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -v $(pwd)/tests:/tests \
                        python:3.10-slim \
                        bash -c "pip install pytest selenium requests -q && \
                                 apt-get update -q && apt-get install -y -q chromium chromium-driver && \
                                 pytest /tests/test_ui.py -v"
                '''
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        # Push unstable image (built from main branch)
                        docker push ${IMAGE_UNSTABLE}

                        # Build and push stable image from stable-fallback branch
                        git fetch origin stable-fallback
                        git stash || true
                        git checkout origin/stable-fallback -- app.py requirements.txt Dockerfile
                        docker build -t ${IMAGE_STABLE} .
                        docker push ${IMAGE_STABLE}

                        # Restore main branch files
                        git checkout HEAD -- app.py requirements.txt Dockerfile
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    # Apply persistent volume claim
                    kubectl apply -f k8s/pvc.yaml

                    # Apply both deployments
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml

                    # Apply the service (routes to blue/slot:blue initially)
                    kubectl apply -f k8s/service.yaml

                    # Wait for blue deployment to be ready
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s
                '''
            }
        }

    }

    post {
        always {
            echo "Pipeline finished with status: ${currentBuild.currentResult}"
        }
        failure {
            echo "Pipeline FAILED — check logs above"
        }
    }
}
