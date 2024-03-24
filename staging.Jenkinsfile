pipeline {
  agent none
  environment {
   
    PROJECT_NAME = 'ticketsapp'
    DOCKER_REGISTRY = 'hexakomb/ticketsapp'
    DOCKER_CONTAINER_NAME = 'ticketsapp'
    ENV_FILE = '/env_files/ticketsapp_env.txt'
    DOCKER_NETWORK = 'e_menyesha_appnet'
    DOCKER_VOLUME = '/root/data/ticketsapp/:/ticketsapp/'
    DOCKER_PORT_BINDING = '9910:8000'
  }
  stages {
   
    stage('build and push docker image') {
      agent {
        node {
          label 'master'
        }
      }
      steps {
          sh  "docker build . -f DockerFile -t ${env.DOCKER_REGISTRY}:${env.GIT_COMMIT}"
          sh  'cat ~/my_docker_password.txt | docker login --username hexakomb --password-stdin'
          sh "docker push ${env.DOCKER_REGISTRY}:${env.GIT_COMMIT}"
          sh "docker rmi ${env.DOCKER_REGISTRY}:${env.GIT_COMMIT} || true"
          cleanWs()
      }
    }
    stage('Deploy to staging') {
      agent {
        node {
          label 'master'
        }
      }
      steps([$class: 'BapSshPromotionPublisherPlugin']) {
        sshPublisher(
          continueOnError: false, failOnError: true,
          publishers: [
            sshPublisherDesc(
              configName: 'digital ocean dims droplet',
              verbose: true,
              transfers: [
                sshTransfer(execCommand: 'cat ~/my_password.txt | docker login --username hexakomb --password-stdin'),
                sshTransfer(execCommand: "docker pull ${env.DOCKER_REGISTRY}:${env.GIT_COMMIT}"),
                sshTransfer(execCommand: "docker stop ${env.DOCKER_CONTAINER_NAME} || true "),
                sshTransfer(execCommand: "docker rm ${env.DOCKER_CONTAINER_NAME} || true"),
                sshTransfer(execCommand: "docker run --env-file ${env.ENV_FILE} --network=${env.DOCKER_NETWORK} --publish ${env.DOCKER_PORT_BINDING} --name ${env.DOCKER_CONTAINER_NAME} -d -v ${env.DOCKER_VOLUME} --restart unless-stopped ${env.DOCKER_REGISTRY}:${env.GIT_COMMIT} "),
              ]
            )
          ]
        )
      }
    }
  }
  post {
    success {
      bitbucketStatusNotify(buildState: 'SUCCESSFUL')
    }
    failure {
      bitbucketStatusNotify(buildState: 'FAILED')
    }
  }
}

