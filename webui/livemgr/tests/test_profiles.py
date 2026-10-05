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

from django.contrib.auth.models import User as AuthUser
from django.test import Client
from webui.livemgr.tests.base import LivemgrTestCase

class ProfileUpdateTest(LivemgrTestCase):
	def setUp(self):
		self.account = self.login(self.create_account('operator', permissions=['see_dashboard']))

	def post(self, **data):
		data.setdefault('language', 'en')
		return self.client.post('/profile/update/', data)

	def reload(self):
		return AuthUser.objects.get(pk=self.account.pk)

	def test_form(self):
		response = self.client.get('/profile/update/')
		self.assertEqual(response.context['form_user'].instance, self.account)
		self.assertEqual(response.context['form_profile'].instance, self.profile_of(self.account))
		self.assertFalse(response.context['show_debug'])
		self.assertTrue(self.client.get('/profile/update/?debug').context['show_debug'])

	def test_update_personal_data(self):
		response = self.post(first_name='Op', last_name='Erator', email='op@example.com',
			next='/acls/')
		self.assertRedirectsTo(response, '/acls/') # via django.views.i18n.set_language
		account = self.reload()
		self.assertEqual((account.first_name, account.last_name, account.email),
			('Op', 'Erator', 'op@example.com'))
		self.assertTrue(account.check_password(self.PASSWORD)) # untouched

	def test_update_flashes_success(self):
		response = self.client.post('/profile/update/',
			{'language': 'en', 'next': '/profile/update/'}, follow=True)
		self.assertFlash(response, 'Your profile was updated successfully.')

	def test_update_preferences(self):
		self.post(language='pt-br', debug='on')
		profile = self.profile_of(self.account)
		self.assertEqual(profile.language, 'pt-br')
		self.assertTrue(profile.debug)

	def test_language_switch_applies_immediately(self):
		self.post(language='pt-br')
		response = self.client.get('/dashboard/')
		self.assertContains(response, 'Sair') # "Logout"
		self.assertContains(response, 'Perfil') # "Profile"

	def test_language_switch_applies_to_javascript(self):
		self.post(language='pt-br')
		self.assertContains(self.client.get('/jsi18n/'), 'Hoje') # "Today", from LOCALE_PATHS

	def test_change_password(self):
		self.post(old_password=self.PASSWORD, new_password1='n3w', new_password2='n3w')
		self.assertTrue(self.reload().check_password('n3w'))

	def test_change_password_keeps_this_session(self):
		self.post(old_password=self.PASSWORD, new_password1='n3w', new_password2='n3w')
		self.assertEqual(self.client.get('/dashboard/').status_code, 200)

	def test_change_password_ends_other_sessions(self):
		other = Client()
		self.assertTrue(other.login(username='operator', password=self.PASSWORD))
		self.post(old_password=self.PASSWORD, new_password1='n3w', new_password2='n3w')
		self.assertRedirectsToLogin(other.get('/dashboard/'))

	def test_passwords_stay_readable_by_django_1_3(self):
		# Logging in and changing the password must not switch to PBKDF2 yet
		# (see PASSWORD_HASHERS).
		self.assertTrue(self.reload().password.startswith('sha1$'))
		self.post(old_password=self.PASSWORD, new_password1='n3w', new_password2='n3w')
		self.assertTrue(self.reload().password.startswith('sha1$'))

	def test_wrong_current_password(self):
		response = self.post(old_password='wrong', new_password1='n3w', new_password2='n3w')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['form_user'].errors['old_password'],
			['Your current password is incorrect. Please type it again.'])
		self.assertTrue(self.reload().check_password(self.PASSWORD))

	def test_password_confirmation_mismatch(self):
		response = self.post(old_password=self.PASSWORD, new_password1='n3w', new_password2='other')
		self.assertEqual(response.context['form_user'].errors['new_password2'],
			["The two password fields don't match."])
		self.assertTrue(self.reload().check_password(self.PASSWORD))

	def test_new_password_without_the_current_one(self):
		# Pinned behavior: the current password is only checked when given.
		self.post(new_password1='n3w', new_password2='n3w')
		self.assertTrue(self.reload().check_password('n3w'))

	def test_unknown_language(self):
		response = self.post(language='xx')
		self.assertTrue('language' in response.context['form_profile'].errors)

class LoginLanguageTest(LivemgrTestCase):
	def test_login_applies_the_profile_language(self):
		account = self.create_account('operator', permissions=['see_dashboard'])
		profile = self.profile_of(account)
		profile.language = 'pt-br'
		profile.save()
		self.client.post('/login/', {'username': 'operator', 'password': self.PASSWORD})
		response = self.client.get('/dashboard/')
		self.assertContains(response, 'Sair')
		self.assertContains(response, 'Painel') # "Dashboard"

	def test_default_language(self):
		self.login(self.create_account('operator', permissions=['see_dashboard']))
		response = self.client.get('/dashboard/')
		self.assertContains(response, 'Logout')
