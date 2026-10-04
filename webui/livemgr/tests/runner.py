# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Jardel Weyrich
#
# This file is part of livemgr-webui.
#
# livemgr-webui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# livemgr-webui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jardel Weyrich <jweyrich@gmail.com>

"""
	Test runner that builds the test database the same way production does.

	Most livemgr models are `managed = False`: their tables are owned by
	bootstrap/db/create_tables.sql (shared with the closed-source backend),
	not by Django. After Django creates its own tables, this runner loads that
	SQL file, so the tests exercise the real schema and its reference data
	(the built-in 'guest' group, the rules and the default settings).
"""

from django.db import connection, transaction
import django
import os
import re
import warnings

try:
	from django.test.runner import DiscoverRunner as BaseRunner # Django >= 1.6
except ImportError:
	from django.test.simple import DjangoTestSuiteRunner as BaseRunner

SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
	os.pardir, os.pardir, os.pardir, 'bootstrap', 'db', 'create_tables.sql')

# Django < 1.6 takes app labels; newer versions take dotted module paths.
if django.VERSION >= (1, 6):
	DEFAULT_TEST_LABELS = ['webui.livemgr']
else:
	DEFAULT_TEST_LABELS = ['livemgr']

def split_sql(text):
	"""
	Split a mysql-client script into statements, honoring DELIMITER changes.
	"""
	text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
	delimiter = ';'
	statements = []
	lines = []
	for line in text.splitlines():
		stripped = line.strip()
		if not lines and (not stripped or stripped.startswith('--')):
			continue
		match = re.match(r'^DELIMITER\s+(\S+)$', stripped, re.IGNORECASE)
		if match:
			delimiter = match.group(1)
			continue
		lines.append(line)
		if stripped.endswith(delimiter):
			statement = '\n'.join(lines).rstrip()[:-len(delimiter)].strip()
			lines = []
			if statement:
				statements.append(statement)
	return statements

def schema_statements(path=SCHEMA_FILE):
	statements = []
	for statement in split_sql(open(path).read()):
		# The test runner already selected (and owns) the test database.
		if re.match(r'^(USE|CREATE\s+DATABASE)\b', statement, re.IGNORECASE):
			continue
		# MyISAM ignores transactions, so rows would leak between tests.
		statement = re.sub(r'ENGINE\s*=\s*MyISAM', 'ENGINE=InnoDB', statement)
		statements.append(statement)
	return statements

def load_schema(path=SCHEMA_FILE):
	cursor = connection.cursor()
	with warnings.catch_warnings():
		# "Table 'auth_user_profile' already exists": syncdb created it first.
		warnings.simplefilter('ignore')
		for statement in schema_statements(path):
			cursor.execute(statement)
	commit_unless_managed = getattr(transaction, 'commit_unless_managed', None)
	if commit_unless_managed: # Django < 1.6 doesn't autocommit
		commit_unless_managed()

class LivemgrTestRunner(BaseRunner):
	def setup_databases(self, *args, **kwargs):
		old_config = super(LivemgrTestRunner, self).setup_databases(*args, **kwargs)
		load_schema()
		return old_config

	def run_tests(self, test_labels, *args, **kwargs):
		test_labels = test_labels or DEFAULT_TEST_LABELS
		return super(LivemgrTestRunner, self).run_tests(test_labels, *args, **kwargs)
