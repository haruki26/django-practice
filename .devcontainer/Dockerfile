FROM python:3.13-slim

ARG USER_NAME=vscode
ARG USER_ID=1000
ARG GROUP_NAME=${USER_NAME}
ARG GROUP_ID=${USER_ID}

RUN apt-get update && apt-get install -y \
    build-essential pkg-config default-mysql-client default-libmysqlclient-dev python3.13-dev \
    git curl sudo \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -m -d /home/${USER_NAME} -s /bin/bash -u ${USER_ID} -g ${USER_NAME} ${USER_NAME} && \
    echo ${USER_NAME}' ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV HOME=/home/${USER_NAME}
USER ${USER_NAME}

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
