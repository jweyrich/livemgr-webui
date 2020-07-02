FROM node:latest AS media_build

WORKDIR /media

COPY package*.json ./

# Install gulp and other dependencies
RUN npm install -g gulp && npm install

COPY media/ ./

# Minify and concatenate media files (.css and .js):
RUN gulp --gulpfile gulpfile.js all

###

FROM debian:stretch
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
	;

# Install database requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	mysql-client \
	libmariadbclient-dev \
	;

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

# Install app dependencies
RUN /opt/envs/livemgr-webui/bin/pip install -r requirements.txt

# Copy minified media files back to this container
COPY --from=media_build /media/css/all.min.css ./media/css/
COPY --from=media_build /media/js/all.min.js ./media/js/

# Expose ports
EXPOSE 8000

# Run baby, run!
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
