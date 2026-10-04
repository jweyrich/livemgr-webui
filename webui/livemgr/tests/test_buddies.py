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

from webui.livemgr.models import Buddy
from webui.livemgr.tests.base import LivemgrTestCase

def listed(response):
	return [row.record for row in response.context['page'].object_list]

class BuddiesTest(LivemgrTestCase):
	def setUp(self):
		self.account = self.login_superuser()
		self.alice = self.make_user('alice@example.com')
		self.bob = self.make_buddy(self.alice, 'bob@example.com', displayname='Bob', status='NLN')
		self.carol = self.make_buddy(self.alice, 'carol@example.com', status='BSY', isblocked=True)
		self.other = self.make_user('other@example.com')
		self.others_buddy = self.make_buddy(self.other, 'bob@example.com')
		self.url = '/users/%d/contacts/' % self.alice.id

	def test_list_only_the_users_buddies(self):
		response = self.client.get(self.url)
		self.assertEqual(listed(response), [self.bob, self.carol])
		self.assertEqual(response.context['from_user'], self.alice)
		self.assertContains(response, 'status-online')

	def test_unknown_user(self):
		self.assertEqual(self.client.get('/users/999999/contacts/').status_code, 404)

	def test_search(self):
		self.assertEqual(listed(self.client.post(self.url, {'username': 'car'})), [self.carol])
		self.assertEqual(listed(self.client.post(self.url, {'displayname': 'Bo'})), [self.bob])
		self.assertEqual(listed(self.client.post(self.url, {'status': 'BSY'})), [self.carol])

	def test_invalid_search(self):
		self.assertEqual(self.client.post(self.url, {'status': 'XXX'}).status_code, 400)

	def test_change_page_size(self):
		self.client.post(self.url, {'per_page': '30'})
		self.assertEqual(self.profile_of(self.account).per_page_buddies, 30)

	def blocked(self):
		return sorted(Buddy.objects.filter(isblocked=True).values_list('id', flat=True))

	def test_block(self):
		response = self.client.post('/users/%d/block/' % self.alice.id, {'selection': [self.bob.id]})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(self.blocked(), sorted([self.bob.id, self.carol.id]))

	def test_unblock(self):
		self.client.post('/users/%d/unblock/' % self.alice.id, {'selection': [self.carol.id]})
		self.assertEqual(self.blocked(), [])

	def test_block_ignores_buddies_of_other_users(self):
		self.client.post('/users/%d/block/' % self.alice.id, {'selection': [self.others_buddy.id]})
		self.assertFalse(Buddy.objects.get(pk=self.others_buddy.id).isblocked)
