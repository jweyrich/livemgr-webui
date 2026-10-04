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

# Django 1.6 marks a transaction as broken when a query fails inside an atomic
# block (every TestCase, or ATOMIC_REQUESTS), and refuses further queries until
# the block ends. Writes that may fail and be handled, like an IntegrityError
# on a duplicate name, must run in their own atomic block so only that block
# is rolled back. Django < 1.6 has no atomic; commit_on_success is the closest.
try:
	from django.db.transaction import atomic
except ImportError:
	from django.db.transaction import commit_on_success as atomic
