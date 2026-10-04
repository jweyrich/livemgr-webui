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

import django

# Django < 1.6 only collects tests found in the app's `tests` module, so the
# modules must be re-exported here. Newer versions discover test_*.py on their
# own and would run these twice. Remove this block once rolling back to
# Django 1.5 is no longer an option.
if django.VERSION < (1, 6):
	from webui.livemgr.tests.test_access import *
	from webui.livemgr.tests.test_acls import *
	from webui.livemgr.tests.test_badwords import *
	from webui.livemgr.tests.test_buddies import *
	from webui.livemgr.tests.test_common import *
	from webui.livemgr.tests.test_conversations import *
	from webui.livemgr.tests.test_dashboard import *
	from webui.livemgr.tests.test_formatters import *
	from webui.livemgr.tests.test_groups import *
	from webui.livemgr.tests.test_install import *
	from webui.livemgr.tests.test_license import *
	from webui.livemgr.tests.test_models import *
	from webui.livemgr.tests.test_profiles import *
	from webui.livemgr.tests.test_settings import *
	from webui.livemgr.tests.test_templatetags import *
	from webui.livemgr.tests.test_users import *
