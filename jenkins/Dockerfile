FROM jenkins/jenkins:lts

USER root


RUN apt-get update && \
    apt-get install -y docker.io curl && \
    mkdir -p /usr/local/lib/docker/cli-plugins/ && \
    curl -SL https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-linux-aarch64 -o /usr/local/lib/docker/cli-plugins/docker-compose && \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose && \
    apt-get clean


RUN usermod -aG docker jenkins

USER jenkins
