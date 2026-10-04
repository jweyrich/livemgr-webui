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
	webui/livemgr/management.py hooks post_syncdb (renamed post_migrate in
	Django 1.7, post_syncdb removed in 1.9) to create the default accounts.
	These tests check what that hook left in the freshly created test database.
"""

from django.contrib.auth.models import Group, Permission, User as AuthUser
from webui.livemgr.models import Profile
from webui.livemgr.tests.base import LivemgrTestCase

# Every permission a view checks with @permission_required('livemgr.<codename>')
PERMISSIONS_REQUIRED_BY_VIEWS = [
	'see_dashboard',
	'see_acl', 'add_acl', 'change_acl', 'delete_acl',
	'see_user', 'add_user', 'change_user', 'delete_user',
	'see_buddy', 'change_buddy',
	'see_usergroup', 'add_usergroup', 'change_usergroup', 'delete_usergroup',
	'see_conversation',
	'see_badword', 'add_badword', 'change_badword', 'delete_badword',
	'change_setting',
]

class InstallHookTest(LivemgrTestCase):
	def test_admin_account(self):
		admin = AuthUser.objects.get(username='admin')
		self.assertTrue(admin.is_active)
		self.assertTrue(admin.is_superuser)
		self.assertTrue(admin.is_staff)
		self.assertTrue(admin.check_password('admin'))
		self.assertEqual(Profile.objects.filter(user=admin).count(), 1)

	def test_auditor_account(self):
		auditor = AuthUser.objects.get(username='auditor')
		self.assertTrue(auditor.is_active)
		self.assertFalse(auditor.is_superuser)
		self.assertFalse(auditor.is_staff)
		self.assertTrue(auditor.check_password('auditor'))
		self.assertEqual([g.name for g in auditor.groups.all()], ['auditor'])

	def test_auditor_group_permissions(self):
		# The hook selects permissions by codename only. Up to Django 1.3 that
		# also picked up auth.change_message, from django.contrib.auth's
		# Message model, which Django 1.4 removed.
		auditor = Group.objects.get(name='auditor')
		self.assertEqual(
			sorted(auditor.permissions.values_list('content_type__app_label', 'codename')),
			[
				('livemgr', 'change_message'),
				('livemgr', 'see_conversation'),
				('livemgr', 'see_dashboard'),
				('livemgr', 'see_message'),
			])

class PermissionsTest(LivemgrTestCase):
	def test_permissions_required_by_views_exist(self):
		existing = set(Permission.objects
			.filter(content_type__app_label='livemgr')
			.values_list('codename', flat=True))
		for codename in PERMISSIONS_REQUIRED_BY_VIEWS:
			self.assertTrue(codename in existing, codename)

	def test_license_permission_does_not_exist(self):
		# The license view requires 'livemgr.see_license', which no model
		# declares: only superusers can open it.
		self.assertFalse(Permission.objects.filter(codename='see_license').exists())
