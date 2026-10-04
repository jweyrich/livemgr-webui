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

# Django settings for running the test suite.
#
#   python webui/manage.py test --settings=settings_test
#
# Defaults match the devcontainer (.devcontainer/docker-compose.yml). The test
# runner creates and destroys its own `test_<NAME>` database, so it needs a
# MySQL user allowed to CREATE/DROP databases.
from settings import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('LIVEMGR_TEST_DB_NAME', 'livemgr'),
        'USER': os.environ.get('LIVEMGR_TEST_DB_USER', 'root'),
        'PASSWORD': os.environ.get('LIVEMGR_TEST_DB_PASSWORD', '123456'),
        'HOST': os.environ.get('LIVEMGR_TEST_DB_HOST', 'db'),
        'PORT': os.environ.get('LIVEMGR_TEST_DB_PORT', ''),
        # Django < 1.7 reads TEST_CHARSET; newer versions read TEST['CHARSET'].
        'TEST_CHARSET': 'utf8',
        'TEST': {'CHARSET': 'utf8'},
    }
}

TEST_RUNNER = 'webui.livemgr.tests.runner.LivemgrTestRunner'

# Templates used only by the tests.
TEMPLATE_DIRS = (
    os.path.join(ROOT, 'livemgr', 'tests', 'templates'),
)

# Pin the language so assertions on rendered text are deterministic.
LANGUAGE_CODE = 'en-us'

# Keep the license view away from the network and the real certificate.
LICENSE_FILE = os.path.join(ROOT, 'livemgr', 'tests', 'data', 'does-not-exist.pem')
KEYSERVER_HOST = '127.0.0.1'
