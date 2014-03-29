#!/bin/bash
PWD=$(/bin/pwd)
LIB_MYSQL_CLIENT_PATH=/usr/local/mysql/lib/libmysqlclient.18.dylib
LIB_MYSQL_CLIENT_FILENAME=$(/usr/bin/basename $LIB_MYSQL_CLIENT_PATH)
LIB_MYSQLDB_PATH=$(PWD)/env/lib/python2.7/site-packages/_mysql.so
LIB_MYSQLDB_DIR=$(/usr/bin/dirname $LIB_MYSQLDB_PATH)
LIB_MYSQLDB_NEW_LINK="$LIB_MYSQLDB_DIR/$LIB_MYSQL_CLIENT_FILENAME"
/bin/ln -sf $LIB_MYSQL_CLIENT_PATH $LIB_MYSQLDB_NEW_LINK
