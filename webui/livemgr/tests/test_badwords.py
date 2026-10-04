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

from webui.livemgr.models import Badword
from webui.livemgr.tests.base import LivemgrTestCase

def listed(response):
	return [row.data for row in response.context['page'].object_list]

class BadwordListTest(LivemgrTestCase):
	def setUp(self):
		self.account = self.login_superuser()
		self.darn = self.make_badword('darn')
		self.heck = self.make_badword('he+ck', isregex=True, isenabled=False)

	def test_list(self):
		response = self.client.get('/badwords/')
		self.assertEqual(listed(response), [self.darn, self.heck])
		self.assertContains(response, "class='icon accept'")
		self.assertContains(response, "class='icon accept-gray'")

	def test_search(self):
		self.assertEqual(listed(self.client.post('/badwords/', {'badword': 'ar'})), [self.darn])

	def test_change_page_size(self):
		self.client.post('/badwords/', {'per_page': '25'})
		self.assertEqual(self.profile_of(self.account).per_page_badwords, 25)

class BadwordAddTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()

	def test_add_normalizes_the_word(self):
		response = self.client.post('/badwords/add/',
			{'badword': '  DaRn  ', 'isenabled': 'on'})
		badword = Badword.objects.get()
		self.assertEqual(badword.badword, 'darn')
		self.assertTrue(badword.isenabled)
		self.assertFalse(badword.isregex)
		self.assertFlash(response, "The badword 'darn' was created successfully.")

	def test_add_regex(self):
		self.client.post('/badwords/add/', {'badword': 'f+oo', 'isregex': 'on', 'isenabled': 'on'})
		self.assertTrue(Badword.objects.get(badword='f+oo').isregex)

	def test_invalid_regex(self):
		response = self.client.post('/badwords/add/', {'badword': '([', 'isregex': 'on'})
		self.assertEqual(response.context['form'].errors['badword'], ['Invalid regular expression'])
		self.assertFlash(response, 'Please, correct the fields below.')
		self.assertFalse(Badword.objects.exists())

	def test_invalid_regex_is_accepted_as_plain_text(self):
		self.client.post('/badwords/add/', {'badword': '(['})
		self.assertTrue(Badword.objects.filter(badword='([').exists())

	def test_duplicate_ignores_case(self):
		self.make_badword('darn')
		response = self.client.post('/badwords/add/', {'badword': 'DARN'})
		self.assertEqual(len(self.flash_messages(response)), 1)
		self.assertEqual(Badword.objects.count(), 1)

	def test_add_and_list(self):
		response = self.client.post('/badwords/add/', {'badword': 'darn', '_save_list': '1'})
		self.assertRedirectsTo(response, '/badwords/')

	def test_add_and_edit(self):
		response = self.client.post('/badwords/add/', {'badword': 'darn', '_save_edit': '1'})
		self.assertRedirectsTo(response, '/badwords/%d/' % Badword.objects.get().id)

class BadwordEditTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.badword = self.make_badword('darn')

	def test_form(self):
		response = self.client.get('/badwords/%d/' % self.badword.id)
		self.assertEqual(response.context['form'].instance, self.badword)

	def test_edit(self):
		response = self.client.post('/badwords/%d/' % self.badword.id,
			{'badword': 'Drat ', 'isenabled': ''})
		self.assertFlash(response, "The badword 'drat' was changed successfully.")
		badword = Badword.objects.get(pk=self.badword.id)
		self.assertEqual(badword.badword, 'drat')
		self.assertFalse(badword.isenabled)

	def test_edit_to_an_existing_word(self):
		self.make_badword('drat')
		self.client.post('/badwords/%d/' % self.badword.id, {'badword': 'drat'})
		self.assertEqual(Badword.objects.get(pk=self.badword.id).badword, 'darn')

class BadwordBulkActionsTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.darn = self.make_badword('darn')
		self.heck = self.make_badword('heck')
		self.drat = self.make_badword('drat')

	def enabled(self):
		return sorted(Badword.objects.filter(isenabled=True).values_list('badword', flat=True))

	def test_disable_and_enable(self):
		self.client.post('/badwords/disable/', {'selection': [self.darn.id, self.heck.id]})
		self.assertEqual(self.enabled(), ['drat'])
		self.client.post('/badwords/enable/', {'selection': [self.heck.id]})
		self.assertEqual(self.enabled(), ['drat', 'heck'])

	def test_delete(self):
		self.assertRedirectsTo(self.client.get('/badwords/%d/delete/' % self.darn.id), '/badwords/')
		self.assertEqual(self.client.post('/badwords/%d/delete/' % self.heck.id).status_code, 200)
		self.assertEqual(list(Badword.objects.all()), [self.drat])

	def test_delete_many(self):
		self.client.post('/badwords/delete/', {'selection': [self.darn.id, self.drat.id]})
		self.assertEqual(list(Badword.objects.all()), [self.heck])
