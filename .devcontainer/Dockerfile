# Development image for livemgr-webui (Python 2.7 + Django 1.2 + Node for gulp).
# Mirrors the production Dockerfile at the repository root, but keeps the
# source tree bind-mounted instead of baked in.

FROM node:10-buster AS node

###

FROM debian:buster

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Buster is EOL: its packages now live only on archive.debian.org
RUN printf '%s\n' \
		'deb http://archive.debian.org/debian buster main' \
		'deb http://archive.debian.org/debian-security buster/updates main' \
		> /etc/apt/sources.list \
	&& apt-get -qq update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
		git \
		less \
		net-tools \
		procps \
		sudo \
		gcc \
		swig \
		libssl-dev \
		python2.7-dev \
		python-pip \
		python-setuptools \
		python-virtualenv \
		default-mysql-client \
		libmariadbclient-dev \
	&& rm -rf /var/lib/apt/lists/*

# MySQL-python expects mysql_config and the `reconnect` field in st_mysql
RUN ln -s /usr/bin/mariadb_config /usr/bin/mysql_config \
	&& sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mariadb/mysql.h -i.bkp

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
RUN python2.7 -m virtualenv $VIRTUAL_ENV && chown -R $USERNAME:$USERNAME $VIRTUAL_ENV

USER $USERNAME
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
