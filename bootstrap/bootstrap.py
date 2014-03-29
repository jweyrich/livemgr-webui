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

from django.db.models import Group, Site, User

#
# SITES
#
#site = Site()
#site.domain = 'livemgr'
#site.name = 'localhost'
#site_livemgr = site.save()
# TODO assert id == 1

#
# GROUPS
#
group = Group()
group.name = 'manager'
group_manager = group.save()

group = Group()
group.name = 'auditor'
group.permissions = [
	'livemgr.see_conversation',
	'livemgr.see_dashboard',
	'livemgr.see_message',
]
group_auditor = group.save()

#
# USERS
#
user = User()
user.username = 'admin'
user.groups.add(group_manager)
user.set_password('admin')
user.is_staff = True
user.is_active = True
user.is_superuser = True
user_admin = user.save()

user = User()
user.username = 'auditor'
user.groups.add(group_auditor)
user.set_password('auditor')
user.is_staff = False
user.is_active = True
user.is_superuser = False
user_auditor = user.save()

#myuser.groups = [group_list]
#myuser.groups.add(group, group, ...)
#myuser.groups.remove(group, group, ...)
#myuser.groups.clear()
#myuser.user_permissions = [permission_list]
#myuser.user_permissions.add(permission, permission, ...)
#myuser.user_permissions.remove(permission, permission, ...)
#myuser.user_permissions.clear()
