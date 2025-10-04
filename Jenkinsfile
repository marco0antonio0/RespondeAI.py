pipeline {
    agent any

    environment {
        COMPOSE_FILE = "docker-compose.yml"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Clonando repositório..."
                checkout scm
            }
        }
  
        stage('Build') {
            steps {
                echo "Buildando containers com Docker Compose..."
                sh '''
                  docker compose -f $COMPOSE_FILE build --no-cache
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Subindo containers atualizados..."
                sh '''
                  docker compose -f $COMPOSE_FILE down --volumes --remove-orphans
                  docker compose -f $COMPOSE_FILE up -d --force-recreate --remove-orphans
                '''
            }
        }

        stage('Cleanup') {
            steps {
                echo "Limpando imagens antigas e cache..."
                sh '''
                  docker system prune -af
                '''
            }
        }
    }

    post {
        success {
            echo "🚀 Deploy finalizado com sucesso!"
        }
        failure {
            echo "❌ Falha no pipeline!"
        }
    }
}
