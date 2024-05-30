FROM node:10 AS media_build

WORKDIR /media

COPY package*.json ./

# Install all dependencies
RUN npm install

COPY media/ ./

# Minify and concatenate media files (.css and .js):
RUN npx gulp --gulpfile gulpfile.js all

###

FROM debian:buster
LABEL maintainer="jweyrich@gmail.com"

# Install prerequisites
RUN apt-get -qq update

# Install system requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	net-tools \
	procps \
	supervisor \
	git-core \
	python2.7-dev \
	python-pip \
	swig \
	libssl-dev \
	gcc \
	;

# Install database requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	default-mysql-client \
	libmariadbclient-dev \
	mariadb-client \
	;

# Fix missing mysql_config
RUN ln -s /usr/bin/mariadb_config /usr/bin/mysql_config

# Remove cached packages
RUN apt-get clean

# Install virtual env
RUN pip install virtualenv

# Install uwsgi
RUN pip install uwsgi

# Create a virtual environment for our application
# The `--no-size-packages` makes virtualenv remove the system's default site-packages from sys.path
RUN virtualenv /opt/envs/livemgr-webui

# Copy files (TODO: Reorganize to avoid installing dependencies from scratch every time a file changes!)
ADD . /opt/apps/livemgr-webui
ADD .docker/supervisor.conf /opt/supervisor.conf
ADD .docker/run.sh /usr/local/bin/run

WORKDIR /opt/apps/livemgr-webui

# Update Git remote to the public address
RUN git remote set-url origin https://github.com/jweyrich/livemgr-webui.git

# Fix MySQL/MariaDB header file for MySQL-python to compile
RUN sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mariadb/mysql.h -i.bkp

# Install app dependencies
RUN /opt/envs/livemgr-webui/bin/pip install -r requirements.txt

# Copy minified media files back to this container
COPY --from=media_build /media/css/all.min.css ./media/css/
COPY --from=media_build /media/js/all.min.js ./media/js/

# Expose ports
EXPOSE 8000

# Run baby, run!
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
