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

from django.contrib.auth.hashers import PBKDF2PasswordHasher

class FastPBKDF2PasswordHasher(PBKDF2PasswordHasher):
	"""
	PBKDF2 with a single iteration, for settings_test only. Django 5.2 runs
	1,000,000, which every account the tests create and log in would pay. The
	algorithm's name is the same, so the hashes look like the real ones.
	"""
	iterations = 1
