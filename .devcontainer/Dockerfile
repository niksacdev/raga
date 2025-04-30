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

# Install Python 3 and pip3
RUN apt-get install -y python3 python3-pip

# Install uv (fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Add entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Set default shell
SHELL ["/bin/bash", "-c"]
