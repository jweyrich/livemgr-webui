# Development image for livemgr-webui (Python 3.10 + Django 4.1 + Node for gulp).
# Mirrors the production Dockerfile at the repository root, but keeps the
# source tree bind-mounted instead of baked in.

FROM node:10-buster AS node

###

# The official image builds Python 3.10 on top of Debian bookworm, with gcc and
# the OpenSSL and MariaDB client headers already installed.
FROM python:3.10-bookworm

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get -qq update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		less \
		net-tools \
		procps \
		sudo \
		swig \
		default-mysql-client \
	&& rm -rf /var/lib/apt/lists/*

# Node 10 matches the version the production build uses for gulp
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
	&& ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Non-root user with passwordless sudo
RUN groupadd --gid $USER_GID $USERNAME \
	&& useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME \
	&& echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
	&& chmod 0440 /etc/sudoers.d/$USERNAME

# Python dependencies live in a virtualenv outside the workspace
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN python3.10 -m venv $VIRTUAL_ENV && chown -R $USERNAME:$USERNAME $VIRTUAL_ENV

USER $USERNAME
COPY requirements.txt /tmp/requirements.txt
# pip 26.1 drops Python 3.9; 26.2.1 is the latest release
RUN pip install --no-cache-dir pip==26.2.1 \
	&& pip install --no-cache-dir -r /tmp/requirements.txt
