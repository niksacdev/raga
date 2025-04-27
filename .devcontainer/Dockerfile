# Dockerfile for raga dev container
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install up-to-date Git
RUN apt-get update \
    && apt-get install -y build-essential libssl-dev libcurl4-gnutls-dev libexpat1-dev gettext unzip \
    && git --version | grep -q 'git version 2' || ( \
        GIT_VERSION=2.44.0 && \
        curl -LO https://github.com/git/git/archive/refs/tags/v$GIT_VERSION.zip && \
        unzip v$GIT_VERSION.zip && \
        cd git-$GIT_VERSION && \
        make prefix=/usr/local all && \
        make prefix=/usr/local install && \
        cd .. && rm -rf git-$GIT_VERSION v$GIT_VERSION.zip \
    )

# Install Node.js, npm, and eslint
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g eslint

# Install Python 3 and pip3
RUN apt-get install -y python3 python3-pip

# Set default shell
SHELL ["/bin/bash", "-c"]
