#!/bin/bash
PWD=$(/bin/pwd)
PYTHON_SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
LIB_MYSQL_CLIENT_PATH=/usr/local/mysql/lib/libmysqlclient.18.dylib
LIB_MYSQL_CLIENT_FILENAME=$(/usr/bin/basename "$LIB_MYSQL_CLIENT_PATH")
LIB_MYSQLDB_PATH="$PYTHON_SITE_PACKAGES/_mysql.so"
LIB_MYSQLDB_DIR=$(/usr/bin/dirname $LIB_MYSQLDB_PATH)
LIB_MYSQLDB_NEW_LINK="$LIB_MYSQLDB_DIR/$LIB_MYSQL_CLIENT_FILENAME"

/bin/echo "[INFO] Path to Python's site-packages: $PYTHON_SITE_PACKAGES"
/bin/echo "[INFO] Path to MySQL client library  : $LIB_MYSQL_CLIENT_PATH"
/bin/echo "[INFO] Path to the library we'll fix : $LIB_MYSQLDB_PATH"

/bin/ln -sf "$LIB_MYSQL_CLIENT_PATH" "$LIB_MYSQLDB_NEW_LINK"
/usr/bin/install_name_tool -change "libmysqlclient.18.dylib" "$PYTHON_SITE_PACKAGES/libmysqlclient.18.dylib" "$PYTHON_SITE_PACKAGES/_mysql.so"

/bin/echo "DONE"