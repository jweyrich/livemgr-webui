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

from webui.livemgr.models import Setting
from webui.livemgr.tests.base import LivemgrTestCase

class SettingsTest(LivemgrTestCase):
	VALID = {
		'min_protocol_version': '9',
		'max_protocol_version': '15',
		'allow_self_reg': 'on',
		'filtered_msg': '  Blocked!  ',
		'default_warning': 'Monitored',
	}

	def setUp(self):
		self.login_superuser()

	def stored(self):
		return dict(Setting.objects.values_list('name', 'value'))

	def test_form_shows_the_stored_values(self):
		form = self.client.get('/settings/').context['form']
		self.assertEqual(form.fields['min_protocol_version'].initial, 8)
		self.assertEqual(form.fields['max_protocol_version'].initial, 18)
		self.assertEqual(form.fields['allow_self_reg'].initial, 1)
		self.assertEqual(form.fields['filtered_msg'].initial, 'Ouch...')
		self.assertEqual(form.fields['default_warning'].initial, 'Big Brother is watching you')

	def test_update(self):
		response = self.client.post('/settings/', self.VALID)
		self.assertFlash(response, 'The settings were changed successfully.')
		self.assertEqual(self.stored(), {
			'min_protocol_version': '9',
			'max_protocol_version': '15',
			'allow_self_reg': '1',
			'filtered_msg': 'Blocked!',
			'default_warning': 'Monitored',
		})

	def test_unchecked_self_registration(self):
		self.client.post('/settings/', dict(self.VALID, allow_self_reg=''))
		self.assertEqual(self.stored()['allow_self_reg'], '0')

	def test_protocol_versions_are_swapped_when_inverted(self):
		self.client.post('/settings/', dict(self.VALID, min_protocol_version='17', max_protocol_version='10'))
		stored = self.stored()
		self.assertEqual((stored['min_protocol_version'], stored['max_protocol_version']), ('10', '17'))

	def test_blank_messages_are_rejected(self):
		response = self.client.post('/settings/', dict(self.VALID, filtered_msg='   '))
		self.assertEqual(response.context['form'].errors['filtered_msg'], ['This field is required.'])
		self.assertFlash(response, 'Please, correct the fields below.')
		self.assertEqual(self.stored()['filtered_msg'], 'Ouch...')

	def test_unknown_protocol_version(self):
		response = self.client.post('/settings/', dict(self.VALID, min_protocol_version='7'))
		self.assertTrue('min_protocol_version' in response.context['form'].errors)
		self.assertEqual(self.stored()['min_protocol_version'], '8')
