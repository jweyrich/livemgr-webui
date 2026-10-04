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

from webui.livemgr.models import GroupRule, User, UserGroup
from webui.livemgr.tests.base import LivemgrTestCase, GUEST_GROUP_ID

def listed(response):
	return [row.record for row in response.context['page'].object_list]

def rules_of(group):
	return sorted(GroupRule.objects.filter(group=group).values_list('rule_id', flat=True))

def users_of(group):
	return sorted(User.objects.filter(group=group).values_list('username', flat=True))

class GroupListTest(LivemgrTestCase):
	def setUp(self):
		self.account = self.login_superuser()
		self.guest = UserGroup.objects.get(pk=GUEST_GROUP_ID)
		self.sales = self.make_group('sales', description='Sales team')
		self.make_user('a@example.com', group_id=self.sales.id)
		self.make_user('b@example.com', group_id=self.sales.id)
		self.make_user('c@example.com')

	def test_list(self):
		response = self.client.get('/groups/')
		self.assertEqual(listed(response), [self.guest, self.sales])
		self.assertEqual(response.context['page'].paginator.count, 2)

	def test_user_count(self):
		rows = list(self.client.get('/groups/').context['page'].object_list)
		self.assertEqual([row['user_count'] for row in rows], [1, 2])

	def test_search(self):
		self.assertEqual(listed(self.client.post('/groups/', {'groupname': 'sal'})), [self.sales])
		self.assertEqual(listed(self.client.post('/groups/', {'description': 'team'})), [self.sales])

	def test_change_page_size(self):
		self.client.post('/groups/', {'per_page': '15'})
		self.assertEqual(self.profile_of(self.account).per_page_usergroups, 15)

class GroupAddTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.alice = self.make_user('alice@example.com')
		self.bob = self.make_user('bob@example.com')

	def test_form_offers_every_user_and_rule(self):
		response = self.client.get('/groups/add/')
		self.assertEqual(list(response.context['available_users']), [self.alice, self.bob])
		self.assertEqual(len(response.context['available_rules']), 16)

	def test_add_with_users_and_rules(self):
		response = self.client.post('/groups/add/', {
			'groupname': '  sales ', 'description': 'Sales team', 'isactive': 'on',
			'users': [self.alice.id], 'rules': [3, 5],
		})
		group = UserGroup.objects.get(groupname='sales')
		self.assertFlash(response, "The group 'sales' was created successfully.")
		self.assertTrue(group.isactive)
		self.assertFalse(group.isbuiltin)
		self.assertEqual(users_of(group), ['alice@example.com'])
		self.assertEqual(users_of(GUEST_GROUP_ID), ['bob@example.com'])
		self.assertEqual(rules_of(group), [3, 5])

	def test_add_and_edit(self):
		response = self.client.post('/groups/add/', {'groupname': 'sales', '_save_edit': '1'})
		self.assertRedirectsTo(response, '/groups/%d/' % UserGroup.objects.get(groupname='sales').id)

	def test_duplicate(self):
		self.make_group('sales')
		response = self.client.post('/groups/add/', {'groupname': 'sales'})
		self.assertEqual(len(self.flash_messages(response)), 1)
		self.assertEqual(UserGroup.objects.filter(groupname='sales').count(), 1)

class GroupEditTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.sales = self.make_group('sales')
		self.alice = self.make_user('alice@example.com', group_id=self.sales.id)
		self.bob = self.make_user('bob@example.com', group_id=self.sales.id)
		self.carol = self.make_user('carol@example.com')
		GroupRule.objects.create(group=self.sales, rule_id=1)
		GroupRule.objects.create(group=self.sales, rule_id=2)
		self.url = '/groups/%d/' % self.sales.id

	def post(self, url=None, **data):
		data.setdefault('groupname', 'sales')
		return self.client.post(url or self.url, data)

	def test_form(self):
		response = self.client.get(self.url)
		self.assertTrue(response.context['can_delete'])
		self.assertEqual(list(response.context['available_users']), [self.carol])
		self.assertEqual([r.id for r in response.context['available_rules']], list(range(3, 17)))

	def test_builtin_group_cannot_be_deleted(self):
		response = self.client.get('/groups/%d/' % GUEST_GROUP_ID)
		self.assertFalse(response.context['can_delete'])

	def test_edit_fields(self):
		response = self.post(groupname=' marketing ', description='New', users=[self.alice.id, self.bob.id],
			rules=[1, 2])
		self.assertFlash(response, "The group 'marketing' was changed successfully.")
		group = UserGroup.objects.get(pk=self.sales.id)
		self.assertEqual((group.groupname, group.description, group.isactive), ('marketing', 'New', False))

	def test_add_and_remove_users(self):
		self.post(users=[self.alice.id, self.carol.id], rules=[1, 2])
		self.assertEqual(users_of(self.sales), ['alice@example.com', 'carol@example.com'])
		self.assertEqual(users_of(GUEST_GROUP_ID), ['bob@example.com'])

	def test_add_and_remove_rules(self):
		self.post(users=[self.alice.id, self.bob.id], rules=[2, 7])
		self.assertEqual(rules_of(self.sales), [2, 7])

	def test_removing_a_rule_removes_it_from_every_group(self):
		# KNOWN BUG, pinned on purpose: the delete isn't filtered by group.
		other = self.make_group('other')
		GroupRule.objects.create(group=other, rule_id=1)
		self.post(users=[self.alice.id, self.bob.id], rules=[2])
		self.assertEqual(rules_of(self.sales), [2])
		self.assertEqual(rules_of(other), [])

	def test_users_cannot_be_removed_from_the_guest_group(self):
		response = self.post('/groups/%d/' % GUEST_GROUP_ID, groupname='guest', users=[])
		self.assertFlash(response, "However, the users weren't removed because they must belong to one group at least.")
		self.assertEqual(users_of(GUEST_GROUP_ID), ['carol@example.com'])

	def test_rename_to_an_existing_group(self):
		self.post(groupname='guest', users=[self.alice.id, self.bob.id], rules=[1, 2])
		self.assertEqual(UserGroup.objects.get(pk=self.sales.id).groupname, 'sales')

	def test_not_found(self):
		self.assertEqual(self.client.get('/groups/999999/').status_code, 404)

class GroupDeleteTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.sales = self.make_group('sales')
		self.alice = self.make_user('alice@example.com', group_id=self.sales.id)
		GroupRule.objects.create(group=self.sales, rule_id=1)

	def test_delete_moves_users_to_guest(self):
		response = self.client.get('/groups/%d/delete/' % self.sales.id)
		self.assertRedirectsTo(response, '/groups/')
		self.assertFalse(UserGroup.objects.filter(pk=self.sales.id).exists())
		self.assertEqual(User.objects.get(pk=self.alice.id).group_id, GUEST_GROUP_ID)
		self.assertFalse(GroupRule.objects.filter(group=self.sales.id).exists())

	def test_delete_from_ajax(self):
		self.assertEqual(self.client.post('/groups/%d/delete/' % self.sales.id).status_code, 200)
		self.assertFalse(UserGroup.objects.filter(pk=self.sales.id).exists())

	def test_builtin_group_from_link(self):
		response = self.client.get('/groups/%d/delete/' % GUEST_GROUP_ID)
		self.assertRedirectsTo(response, '/groups/%d/' % GUEST_GROUP_ID)
		self.assertTrue(UserGroup.objects.filter(pk=GUEST_GROUP_ID).exists())
		self.assertFlash(self.client.get('/groups/%d/' % GUEST_GROUP_ID), "Can't delete built-in groups.")

	def test_builtin_group_from_ajax(self):
		response = self.client.post('/groups/%d/delete/' % GUEST_GROUP_ID)
		self.assertEqual(response.status_code, 403)
		self.assertTrue(UserGroup.objects.filter(pk=GUEST_GROUP_ID).exists())

	def test_delete_many_skips_builtin_groups(self):
		other = self.make_group('other')
		response = self.client.post('/groups/delete/', {'selection': [GUEST_GROUP_ID, self.sales.id, other.id]})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(UserGroup.objects.values_list('id', flat=True)), [GUEST_GROUP_ID])
		self.assertEqual(User.objects.get(pk=self.alice.id).group_id, GUEST_GROUP_ID)
