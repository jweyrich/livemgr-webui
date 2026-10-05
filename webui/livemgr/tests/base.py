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

from datetime import datetime
from django.contrib.auth.models import Permission, User as AuthUser
from django.test import TestCase
from django.utils import six
from webui.livemgr.models import Acl, Badword, Buddy, Conversation, Message, \
	Profile, User, UserGroup

GUEST_GROUP_ID = 1 # Created by bootstrap/db/create_tables.sql

class LivemgrTestCase(TestCase):
	"""
	Base class for tests that touch the database.

	The bootstrap reference data (the 'guest' group, rules 1-16 and the
	default settings) is loaded once by the test runner and is always present.
	"""
	PASSWORD = 'secret'

	#
	# Web UI accounts (django.contrib.auth)
	#
	def create_account(self, username='operator', permissions=(), superuser=False):
		account = AuthUser.objects.create(username=username, is_active=True,
			is_staff=superuser, is_superuser=superuser)
		account.set_password(self.PASSWORD)
		account.save()
		for codename in permissions:
			account.user_permissions.add(
				Permission.objects.get(content_type__app_label='livemgr', codename=codename))
		return account

	def create_superuser(self, username='root'):
		return self.create_account(username, superuser=True)

	def login(self, account):
		self.assertTrue(self.client.login(username=account.username, password=self.PASSWORD))
		return account

	def login_superuser(self):
		return self.login(self.create_superuser())

	def profile_of(self, account):
		return Profile.objects.get(user=account)

	#
	# Monitored domain objects (tables owned by the backend)
	#
	def make_group(self, groupname='sales', **kwargs):
		kwargs.setdefault('description', '')
		return UserGroup.objects.create(groupname=groupname, **kwargs)

	def make_user(self, username='alice@example.com', group_id=GUEST_GROUP_ID, **kwargs):
		kwargs.setdefault('status', 'FLN')
		kwargs.setdefault('lastlogin', None)
		return User.objects.create(username=username, group_id=group_id, **kwargs)

	def make_buddy(self, user, username='bob@example.com', **kwargs):
		kwargs.setdefault('status', 'FLN')
		return Buddy.objects.create(user=user, username=username, **kwargs)

	def make_acl(self, localim='alice@example.com', remoteim='*@example.org', action=Acl.ACTION_ALLOW):
		return Acl.objects.create(localim=localim, remoteim=remoteim, action=action)

	def make_badword(self, badword='darn', **kwargs):
		return Badword.objects.create(badword=badword, **kwargs)

	def make_conversation(self, user, status=1, timestamp=None):
		conversation = Conversation.objects.create(user=user, status=status)
		if timestamp: # auto_now_add ignores the value given on create
			Conversation.objects.filter(pk=conversation.pk).update(timestamp=timestamp)
			conversation.timestamp = timestamp
		return conversation

	def make_message(self, conversation_id, content='hello', timestamp=None, **kwargs):
		kwargs.setdefault('clientip', 0x0100007F) # 127.0.0.1, see ip_long_to_str
		kwargs.setdefault('inbound', False)
		kwargs.setdefault('type', Message.Type.MSG)
		kwargs.setdefault('localim', 'alice@example.com')
		kwargs.setdefault('remoteim', 'bob@example.com')
		kwargs.setdefault('filtered', False)
		message = Message.objects.create(conversation_id=conversation_id,
			content=content, **kwargs)
		if timestamp: # auto_now_add ignores the value given on create
			Message.objects.filter(pk=message.pk).update(timestamp=timestamp)
			message.timestamp = timestamp
		return message

	#
	# Assertions
	#
	def flash_messages(self, response):
		"""Flash messages rendered by the response (via the messages context processor)."""
		return [six.text_type(m) for m in response.context['messages']]

	def assertFlash(self, response, text):
		messages = self.flash_messages(response)
		self.assertTrue(text in messages, '%r not in %r' % (text, messages))

	def assertRedirectsToLogin(self, response):
		self.assertEqual(response.status_code, 302)
		self.assertTrue('/login' in response['Location'], response['Location'])

	def assertRedirectsTo(self, response, path):
		"""Like assertRedirects, but doesn't fetch the target page."""
		self.assertEqual(response.status_code, 302)
		location = response['Location'].replace('http://testserver', '')
		self.assertEqual(location, path)

def at(year, month, day, hour=12, minute=0, second=0):
	return datetime(year, month, day, hour, minute, second)
