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

from webui.livemgr.models import Acl
from webui.livemgr.tests.base import LivemgrTestCase

def listed(response):
	return [row.record for row in response.context['page'].object_list]

class AclListTest(LivemgrTestCase):
	def setUp(self):
		self.account = self.login_superuser()
		self.alice = self.make_acl('alice@example.com', '*@example.org', Acl.ACTION_ALLOW)
		self.bob = self.make_acl('bob@example.com', 'eve@example.net', Acl.ACTION_BLOCK)
		self.carol = self.make_acl('carol@example.org', '*', Acl.ACTION_BLOCK)

	def test_list_sorted_by_user(self):
		response = self.client.get('/acls/')
		self.assertEqual(listed(response), [self.alice, self.bob, self.carol])
		self.assertContains(response, 'alice@example.com')
		self.assertContains(response, "class='icon tick'")
		self.assertContains(response, "class='icon cross'")

	def test_sort(self):
		response = self.client.get('/acls/?sort=-localim')
		self.assertEqual(listed(response), [self.carol, self.bob, self.alice])
		response = self.client.get('/acls/?sort=remoteim')
		self.assertEqual(listed(response), [self.carol, self.alice, self.bob])

	def test_pagination_uses_the_profile_page_size(self):
		for i in range(12):
			self.make_acl('user%02d@example.com' % i)
		response = self.client.get('/acls/')
		self.assertEqual(len(listed(response)), 10)
		self.assertEqual(response.context['page'].paginator.count, 15)
		# Since Django 1.5 previous_page_number() and next_page_number() raise
		# on the first and last pages, so the links must depend on has_previous
		# and has_next.
		self.assertContains(response, '<li class="previous-off">')
		self.assertContains(response, '<li class="next">')
		response = self.client.get('/acls/?page=2')
		self.assertEqual(len(listed(response)), 5)
		self.assertContains(response, '11 - 15')
		self.assertContains(response, '<li class="previous">')
		self.assertContains(response, '<li class="next-off">')

	def test_change_page_size(self):
		response = self.client.post('/acls/', {'per_page': '20'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content, b'')
		self.assertEqual(self.profile_of(self.account).per_page_acls, 20)

	def test_search_either_side(self):
		response = self.client.post('/acls/', {'acl': 'example.org'})
		self.assertEqual(listed(response), [self.alice, self.carol])

	def test_search_by_field(self):
		self.assertEqual(listed(self.client.post('/acls/', {'action': Acl.ACTION_BLOCK})),
			[self.bob, self.carol])
		self.assertEqual(listed(self.client.post('/acls/', {'localim': 'bob'})), [self.bob])
		self.assertEqual(listed(self.client.post('/acls/', {'remoteim': 'eve'})), [self.bob])

	def test_search_without_criteria_lists_everything(self):
		self.assertEqual(len(listed(self.client.post('/acls/', {}))), 3)

	def test_invalid_search(self):
		response = self.client.post('/acls/', {'action': '9'})
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, b'Invalid search criteria')

class AclAddTest(LivemgrTestCase):
	DATA = {'action': Acl.ACTION_BLOCK, 'localim': 'alice@example.com', 'remoteim': '*@example.org'}

	def setUp(self):
		self.login_superuser()

	def test_form(self):
		response = self.client.get('/acls/add/')
		self.assertContains(response, 'name="localim"')
		self.assertContains(response, 'You can use the asterisk as a wildcard character.')

	def test_add(self):
		response = self.client.post('/acls/add/', self.DATA)
		self.assertEqual(response.status_code, 200)
		acl = Acl.objects.get()
		self.assertEqual((acl.action, acl.localim, acl.remoteim),
			(Acl.ACTION_BLOCK, 'alice@example.com', '*@example.org'))
		self.assertFlash(response, 'The acl %d was created successfully.' % acl.id)
		self.assertFalse(response.context['form'].is_bound) # ready for another one

	def test_add_and_list(self):
		response = self.client.post('/acls/add/', dict(self.DATA, _save_list='1'))
		self.assertRedirectsTo(response, '/acls/')

	def test_add_and_edit(self):
		response = self.client.post('/acls/add/', dict(self.DATA, _save_edit='1'))
		self.assertRedirectsTo(response, '/acls/%d/' % Acl.objects.get().id)

	def test_add_another(self):
		response = self.client.post('/acls/add/', dict(self.DATA, _save_add='1'))
		self.assertEqual(response.status_code, 200)
		self.assertFlash(response, 'You may add another.')

	def test_missing_fields(self):
		response = self.client.post('/acls/add/', {'action': Acl.ACTION_BLOCK, '_save_list': '1'})
		self.assertEqual(response.status_code, 200) # no redirect on errors
		self.assertFlash(response, 'Please, correct the fields below.')
		self.assertTrue('localim' in response.context['form'].errors)
		self.assertFalse(Acl.objects.exists())

	def test_duplicate(self):
		self.make_acl('alice@example.com', '*@example.org')
		response = self.client.post('/acls/add/', self.DATA)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(self.flash_messages(response)), 1)
		self.assertEqual(Acl.objects.count(), 1)

class AclEditTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.acl = self.make_acl('alice@example.com', '*@example.org', Acl.ACTION_ALLOW)

	def test_form(self):
		response = self.client.get('/acls/%d/' % self.acl.id)
		self.assertTemplateUsed(response, 'acls/edit.html')
		self.assertEqual(response.context['form'].instance, self.acl)
		self.assertContains(response, '/acls/%d/delete/' % self.acl.id)

	def test_edit(self):
		response = self.client.post('/acls/%d/' % self.acl.id,
			{'action': Acl.ACTION_BLOCK, 'localim': 'alice@example.com', 'remoteim': '*'})
		self.assertEqual(response.status_code, 200)
		self.assertFlash(response, 'The acl %d was changed successfully.' % self.acl.id)
		acl = Acl.objects.get(pk=self.acl.id)
		self.assertEqual((acl.action, acl.remoteim), (Acl.ACTION_BLOCK, '*'))

	def test_edit_and_list(self):
		response = self.client.post('/acls/%d/' % self.acl.id,
			{'action': Acl.ACTION_BLOCK, 'localim': 'a', 'remoteim': 'b', '_save_list': '1'})
		self.assertRedirectsTo(response, '/acls/')

	def test_edit_and_add(self):
		response = self.client.post('/acls/%d/' % self.acl.id,
			{'action': Acl.ACTION_BLOCK, 'localim': 'a', 'remoteim': 'b', '_save_add': '1'})
		self.assertRedirectsTo(response, '/acls/add/')

	def test_not_found(self):
		self.assertEqual(self.client.get('/acls/999999/').status_code, 404)

class AclDeleteTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.acl = self.make_acl('alice@example.com')
		self.other = self.make_acl('bob@example.com')

	def test_delete_from_link(self):
		response = self.client.get('/acls/%d/delete/' % self.acl.id)
		self.assertRedirectsTo(response, '/acls/')
		self.assertEqual(list(Acl.objects.all()), [self.other])

	def test_delete_from_ajax(self):
		response = self.client.post('/acls/%d/delete/' % self.acl.id)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(Acl.objects.all()), [self.other])

	def test_delete_not_found(self):
		self.assertEqual(self.client.get('/acls/999999/delete/').status_code, 404)

	def test_delete_many(self):
		third = self.make_acl('carol@example.com')
		response = self.client.post('/acls/delete/', {'selection': [self.acl.id, third.id]})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(Acl.objects.all()), [self.other])
