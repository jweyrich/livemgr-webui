FROM debian:wheezy
MAINTAINER Jardel Weyrich, jweyrich@gmail.com

# Update the repository
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
	;

# Install database requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	mysql-server \
	mysql-client \
	libmysqlclient-dev \
	;

# Install Java 8
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" > /etc/apt/sources.list.d/webupd8team-java.list
RUN echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" >> /etc/apt/sources.list.d/webupd8team-java.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
RUN apt-get update
# Accept license
RUN /bin/echo debconf shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
# Mark license as seen
RUN /bin/echo debconf shared/accepted-oracle-license-v1-1 seen true | /usr/bin/debconf-set-selections
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
	oracle-java8-installer \
	;

# Configure MySQL to listen on 0.0.0.0
#RUN sed -i "s/^bind-address/#bind-address/" /etc/mysql/my.cnf
RUN sed -i -e "/bind-address\s*=\s*/s/127.0.0.1/0.0.0.0/" /etc/mysql/my.cnf

# Remove cached packages
RUN apt-get clean

# Install virtual env
RUN pip install virtualenv

# Install uwsgi
RUN pip install uwsgi

# Create a virtual environment for our application
# The `--no-size-packages` makes virtualenv remove the system's default site-packages from sys.path
RUN virtualenv --no-site-packages /opt/envs/livemgr-webui

# Copy files
ADD . /opt/apps/livemgr-webui
ADD .docker/supervisor.conf /opt/supervisor.conf
ADD .docker/run.sh /usr/local/bin/run

# Update Git remote to the public address
RUN cd /opt/apps/livemgr-webui \
	&& git remote rm origin \
	&& git remote add origin https://github.com/jweyrich/livemgr-webui.git \
	;

# Install app dependencies
RUN /opt/envs/livemgr-webui/bin/pip install -r /opt/apps/livemgr-webui/requirements.txt

# Setup database
RUN service mysql start \
	&& sleep 5 \
	&& mysql -u root -h localhost < /opt/apps/livemgr-webui/bootstrap/db/create_schema.sql \
	&& mysql -u root -h localhost livemgr < /opt/apps/livemgr-webui/bootstrap/db/create_tables.sql \
	&& cd /opt/apps/livemgr-webui/webui \
	&& /opt/envs/livemgr-webui/bin/python manage.py syncdb --noinput --settings=settings_example \
	&& mysqladmin -u root -h localhost password '123456'  \
	;

# Minify and concatenate media files (.css and .js):
RUN cd /opt/apps/livemgr-webui && make -C media all

# Expose ports
EXPOSE 3306 8000

# Run baby, run!
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
