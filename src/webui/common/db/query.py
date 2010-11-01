from MySQLdb.cursors import DictCursor
from django.db import connection
from itertools import izip

#from django.db.backends import BaseDatabaseWrapper
#from django.db.backends.mysql.base import DatabaseWrapper

def fetchone_to_dict(query_string, *query_args):
	cursor = connection.cursor()
	cursor.execute(query_string, query_args)
	col_names = [desc[0] for desc in cursor.description]
	row = cursor.fetchone()
	if row is None:
		return None
	return dict(izip(col_names, row))

def fetchall_to_dict(query_string, *query_args):
	"""
	Code from: http://blog.doughellmann.com/2007/12/using-raw-sql-in-django.html
	Run a simple query and produce a generator
	that returns the results as a bunch of dictionaries
	with keys for the column values selected.
	"""
	cursor = connection.cursor()
	cursor.execute(query_string, query_args)
	col_names = [desc[0] for desc in cursor.description]
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		row_dict = dict(izip(col_names, row))
		yield row_dict
	return

def query_to_dicts2(query_string, *query_args):
	cursor = connection.cursor(DictCursor)
	cursor.execute(query_string, query_args)
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		yield row
	return
