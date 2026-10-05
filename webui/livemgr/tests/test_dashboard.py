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
from webui.livemgr.controllers.dashboard import query_most_active_users
from webui.livemgr.tests.base import LivemgrTestCase, at
import json

class DashboardFixtures(object):
	def create_activity(self):
		self.alice = self.make_user('alice@example.com', status='NLN')
		self.bob = self.make_user('bob@example.com', status='AWY')
		self.make_user('carol@example.com', status='FLN')
		# Today's conversations (timestamps default to now)
		self.active = self.make_conversation(self.alice, status=1)
		self.make_message(self.active.id, 'one', localim='alice@example.com')
		self.make_message(self.active.id, 'two', localim='alice@example.com')
		self.make_message(self.active.id, 'reply', localim='alice@example.com', inbound=True)
		self.closed = self.make_conversation(self.bob, status=0)
		self.make_message(self.closed.id, 'hey', localim='bob@example.com')

class DashboardTest(DashboardFixtures, LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.create_activity()

	def test_index(self):
		response = self.client.get('/dashboard/')
		self.assertTemplateUsed(response, 'dashboard/index.html')
		data = json.loads(response.context['data'])
		self.assertEqual(data['total_users_online'], 2)
		self.assertEqual(data['total_active_conversations'], 1)
		latest = dict((c['id'], c) for c in data['latest_conversations'])
		self.assertEqual(sorted(latest.keys()), sorted([self.active.id, self.closed.id]))
		self.assertEqual(latest[self.active.id]['total'], 3)
		self.assertEqual(latest[self.active.id]['user_id'], self.alice.id)
		self.assertEqual(latest[self.active.id]['localim'], 'alice@example.com')
		self.assertEqual(
			sorted(data['latest_conversations'][0].keys()),
			['id', 'localim', 'msg_id', 'remoteim', 'timestamp', 'total', 'user_id'])
		self.assertEqual(
			[(u['username'], u['total']) for u in data['most_active_users']],
			[('alice@example.com', 2), ('bob@example.com', 1)])

	def test_index_root(self):
		self.assertTemplateUsed(self.client.get('/'), 'dashboard/index.html')

	def test_query(self):
		response = self.client.post('/dashboard/query/', {'limit': '1', 'period': 'year'})
		self.assertEqual(response['Content-Type'], 'application/json')
		data = json.loads(response.content.decode('utf-8'))
		self.assertEqual(data['total_users_online'], 2)
		self.assertEqual(len(data['latest_conversations']), 1)
		self.assertEqual(len(data['most_active_users']), 1)

	def test_query_by_get(self):
		data = json.loads(self.client.get('/dashboard/query/').content.decode('utf-8'))
		self.assertEqual(len(data['latest_conversations']), 2)

	def test_query_with_unknown_period(self):
		data = json.loads(self.client.post('/dashboard/query/', {'period': 'decade'}).content.decode('utf-8'))
		self.assertEqual(data['most_active_users'], [])

class MostActiveUsersTest(LivemgrTestCase):
	def setUp(self):
		alice = self.make_user('alice@example.com')
		conversation = self.make_conversation(alice)
		for day in (17, 17, 18):
			self.make_message(conversation.id, timestamp=at(2010, 5, day), localim='alice@example.com')
		self.make_message(conversation.id, timestamp=at(2010, 6, 1), localim='bob@example.com')
		self.make_message(conversation.id, timestamp=at(2010, 5, 17), localim='bob@example.com',
			inbound=True) # inbound messages don't count
		self.alice = alice

	def ranking(self, period, day):
		return [(u.username, u.total, u.user_id)
			for u in query_most_active_users(5, period, day)]

	def test_day(self):
		self.assertEqual(self.ranking('day', datetime(2010, 5, 17)),
			[('alice@example.com', 2, self.alice.id)])
		self.assertEqual(self.ranking('day', datetime(2010, 5, 19)), [])

	def test_week(self):
		self.assertEqual(self.ranking('week', datetime(2010, 5, 19)),
			[('alice@example.com', 3, self.alice.id)])

	def test_month(self):
		self.assertEqual(self.ranking('month', datetime(2010, 6, 15)),
			[('bob@example.com', 1, None)]) # not a monitored user

	def test_year(self):
		self.assertEqual(self.ranking('year', datetime(2010, 1, 1)),
			[('alice@example.com', 3, self.alice.id), ('bob@example.com', 1, None)])

	def test_limit(self):
		self.assertEqual(len(query_most_active_users(1, 'year', datetime(2010, 1, 1))), 1)

	def test_unknown_period(self):
		self.assertEqual(query_most_active_users(5, 'decade', datetime(2010, 1, 1)), [])
