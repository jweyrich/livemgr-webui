FROM node:10 AS media_build

WORKDIR /media

COPY package*.json ./

# Install all dependencies
RUN npm install

COPY media/ ./

# Minify and concatenate media files (.css and .js):
RUN npx gulp --gulpfile gulpfile.js all

###

# Debian buster ships Python 3.7 only. The official image builds 3.5 on top of
# buster, with git, gcc and the OpenSSL and MariaDB client headers (including
# mysql_config) already installed.
FROM python:3.5-buster
LABEL maintainer="jweyrich@gmail.com"

# Buster is EOL: its packages now live only on archive.debian.org
RUN printf '%s\n' \
		'deb http://archive.debian.org/debian buster main' \
		'deb http://archive.debian.org/debian-security buster/updates main' \
		> /etc/apt/sources.list \
	&& apt-get -qq update

# Install system requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	net-tools \
	procps \
	supervisor \
	swig \
	;

# Install database requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	default-mysql-client \
	mariadb-client \
	;

# Remove cached packages
RUN apt-get clean

# Install uwsgi (2.0.31 still builds on Python 3.5)
RUN pip install uwsgi==2.0.31

# Create a virtual environment for our application.
# Its bundled pip 9 is upgraded to 20.3.4, the last release that supports Python 3.5
RUN python3.5 -m venv /opt/envs/livemgr-webui \
	&& /opt/envs/livemgr-webui/bin/pip install pip==20.3.4

# Copy files (TODO: Reorganize to avoid installing dependencies from scratch every time a file changes!)
ADD . /opt/apps/livemgr-webui
ADD .docker/supervisor.conf /opt/supervisor.conf
ADD .docker/run.sh /usr/local/bin/run

WORKDIR /opt/apps/livemgr-webui

# Update Git remote to the public address
RUN git remote set-url origin https://github.com/jweyrich/livemgr-webui.git

# Install app dependencies
RUN /opt/envs/livemgr-webui/bin/pip install -r requirements.txt

# Copy minified media files back to this container
COPY --from=media_build /media/css/all.min.css ./media/css/
COPY --from=media_build /media/js/all.min.js ./media/js/

# Expose ports
EXPOSE 8000

# Run baby, run!
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
