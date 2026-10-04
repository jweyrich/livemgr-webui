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

from webui.livemgr.models import Buddy, User
from webui.livemgr.tests.base import LivemgrTestCase, GUEST_GROUP_ID, at

def listed(response):
	return [row.record for row in response.context['page'].object_list]

class UserListTest(LivemgrTestCase):
	def setUp(self):
		self.account = self.login_superuser()
		self.sales = self.make_group('sales')
		self.alice = self.make_user('alice@example.com', status='NLN', displayname='Alice')
		self.bob = self.make_user('bob@example.com', group_id=self.sales.id,
			status='AWY', lastlogin=at(2010, 5, 17))
		self.make_buddy(self.bob, 'carol@example.com')

	def test_list(self):
		response = self.client.get('/users/')
		self.assertEqual(listed(response), [self.alice, self.bob])
		self.assertEqual(response.context['page'].paginator.count, 2)

	def test_columns(self):
		rows = list(self.client.get('/users/').context['page'].object_list)
		alice, bob = rows[0], rows[1]
		self.assertEqual(alice['group'], '<a href="/groups/%d/">guest</a>' % GUEST_GROUP_ID)
		self.assertEqual(bob['group'], '<a href="/groups/%d/">sales</a>' % self.sales.id)
		self.assertEqual(alice['contacts'], 'None')
		self.assertEqual(bob['contacts'], '<a href="/users/%d/contacts/">Manage</a>' % self.bob.id)
		self.assertEqual(alice['lastlogin'], 'Never logged')
		self.assertTrue(alice['status'].endswith(' Online'))
		self.assertTrue(bob['status'].endswith(' Away'))

	def test_search(self):
		self.assertEqual(listed(self.client.post('/users/', {'username': 'ali'})), [self.alice])
		self.assertEqual(listed(self.client.post('/users/', {'displayname': 'Ali'})), [self.alice])
		self.assertEqual(listed(self.client.post('/users/', {'group': self.sales.id})), [self.bob])
		self.assertEqual(listed(self.client.post('/users/', {'status': 'NLN'})), [self.alice])

	def test_invalid_search(self):
		self.assertEqual(self.client.post('/users/', {'status': 'XXX'}).status_code, 400)

	def test_change_page_size(self):
		self.client.post('/users/', {'per_page': '50'})
		self.assertEqual(self.profile_of(self.account).per_page_users, 50)

class UserAddTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()

	def test_form(self):
		response = self.client.get('/users/add/')
		self.assertEqual(sorted(response.context['form'].fields.keys()),
			['group', 'isenabled', 'username'])

	def test_add(self):
		response = self.client.post('/users/add/',
			{'username': '  Alice@Example.COM ', 'group': GUEST_GROUP_ID, 'isenabled': 'on'})
		user = User.objects.get()
		self.assertEqual(user.username, 'alice@example.com')
		self.assertEqual(user.status, 'FLN')
		self.assertEqual(user.lastlogin, None)
		self.assertTrue(user.isenabled)
		self.assertFlash(response, "The user 'alice@example.com' was created successfully.")

	def test_add_and_edit(self):
		response = self.client.post('/users/add/',
			{'username': 'alice@example.com', 'group': GUEST_GROUP_ID, '_save_edit': '1'})
		self.assertRedirectsTo(response, '/users/%d/' % User.objects.get().id)

	def test_requires_a_group(self):
		response = self.client.post('/users/add/', {'username': 'alice@example.com'})
		self.assertTrue('group' in response.context['form'].errors)
		self.assertFalse(User.objects.exists())

	def test_duplicate(self):
		self.make_user('alice@example.com')
		response = self.client.post('/users/add/',
			{'username': 'ALICE@example.com', 'group': GUEST_GROUP_ID})
		self.assertEqual(len(self.flash_messages(response)), 1)
		self.assertEqual(User.objects.count(), 1)

class UserEditTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.sales = self.make_group('sales')
		self.never = self.make_user('never@example.com')
		self.seen = self.make_user('seen@example.com', lastlogin=at(2010, 5, 17))

	def test_form(self):
		response = self.client.get('/users/%d/' % self.never.id)
		self.assertTrue(response.context['can_delete'])
		self.assertFalse('readonly' in unicode(response.context['form']['username']))

	def test_form_for_a_user_that_logged_in(self):
		response = self.client.get('/users/%d/' % self.seen.id)
		self.assertFalse(response.context['can_delete'])
		self.assertTrue('readonly' in unicode(response.context['form']['username']))

	def test_edit(self):
		response = self.client.post('/users/%d/' % self.never.id,
			{'username': 'Renamed@example.com', 'group': self.sales.id})
		self.assertFlash(response, "The user 'renamed@example.com' was changed successfully.")
		user = User.objects.get(pk=self.never.id)
		self.assertEqual(user.username, 'renamed@example.com')
		self.assertEqual(user.group_id, self.sales.id)
		self.assertFalse(user.isenabled) # unchecked checkbox

	def test_cannot_rename_a_user_that_logged_in(self):
		response = self.client.post('/users/%d/' % self.seen.id,
			{'username': 'renamed@example.com', 'group': GUEST_GROUP_ID})
		self.assertEqual(response.context['form'].errors['username'],
			['Changing the username for a user that already logged in is not permitted.'])
		self.assertEqual(User.objects.get(pk=self.seen.id).username, 'seen@example.com')

	def test_can_change_other_fields_of_a_user_that_logged_in(self):
		self.client.post('/users/%d/' % self.seen.id,
			{'username': 'seen@example.com', 'group': self.sales.id, 'isenabled': 'on'})
		self.assertEqual(User.objects.get(pk=self.seen.id).group_id, self.sales.id)

	def test_not_found(self):
		self.assertEqual(self.client.get('/users/999999/').status_code, 404)

class UserDeleteTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()

	def test_delete(self):
		user = self.make_user()
		self.make_buddy(user)
		response = self.client.get('/users/%d/delete/' % user.id)
		self.assertRedirectsTo(response, '/users/')
		self.assertFalse(User.objects.exists())
		self.assertFalse(Buddy.objects.exists())

	def test_cannot_delete_a_user_that_logged_in(self):
		user = self.make_user(lastlogin=at(2010, 5, 17))
		response = self.client.get('/users/%d/delete/' % user.id)
		self.assertRedirectsTo(response, '/users/%d/' % user.id)
		self.assertTrue(User.objects.filter(pk=user.id).exists())
		response = self.client.get('/users/%d/' % user.id)
		self.assertFlash(response, 'Deleting a user that already logged in is not permitted.')
