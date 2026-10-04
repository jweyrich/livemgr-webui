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
	URL routing, authentication, authorization and error pages.
"""

from django.contrib.auth.models import AnonymousUser, Group
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from webui.controllers.handlers import error_500
from webui.livemgr.models import Acl
from webui.livemgr.tests.base import LivemgrTestCase

ROUTES = [
	('index', [], '/'),
	('dashboard-index', [], '/dashboard/'),
	('dashboard-query', [], '/dashboard/query/'),
	('acls-index', [], '/acls/'),
	('acls-add', [], '/acls/add/'),
	('acls-delete-many', [], '/acls/delete/'),
	('acls-edit', [7], '/acls/7/'),
	('acls-delete', [7], '/acls/7/delete/'),
	('users-index', [], '/users/'),
	('users-add', [], '/users/add/'),
	('users-edit', [7], '/users/7/'),
	('users-delete', [7], '/users/7/delete/'),
	('buddies-index', [7], '/users/7/contacts/'),
	('buddies-block-many', [7], '/users/7/block/'),
	('buddies-unblock-many', [7], '/users/7/unblock/'),
	('groups-index', [], '/groups/'),
	('groups-add', [], '/groups/add/'),
	('groups-delete-many', [], '/groups/delete/'),
	('groups-edit', [7], '/groups/7/'),
	('groups-delete', [7], '/groups/7/delete/'),
	('conversations-index', [], '/conversations/'),
	('conversations-show', [7], '/conversations/7/'),
	('conversations-report-pdf', [7], '/conversations/7/report/pdf/'),
	('badwords-index', [], '/badwords/'),
	('badwords-add', [], '/badwords/add/'),
	('badwords-delete-many', [], '/badwords/delete/'),
	('badwords-disable-many', [], '/badwords/disable/'),
	('badwords-enable-many', [], '/badwords/enable/'),
	('badwords-edit', [7], '/badwords/7/'),
	('badwords-delete', [7], '/badwords/7/delete/'),
	('settings-update', [], '/settings/'),
	('license-index', [], '/license/'),
	('profiles-login', [], '/login/'),
	('profiles-logout', [], '/logout/'),
	('profiles-update', [], '/profile/update/'),
]

# (method, path) of every view that requires an authenticated user,
# using a method the view accepts.
PROTECTED = [
	('get', '/'),
	('get', '/dashboard/'),
	('post', '/dashboard/query/'),
	('get', '/acls/'),
	('get', '/acls/add/'),
	('post', '/acls/delete/'),
	('get', '/acls/1/'),
	('get', '/acls/1/delete/'),
	('get', '/users/'),
	('get', '/users/add/'),
	('get', '/users/1/'),
	('get', '/users/1/delete/'),
	('get', '/users/1/contacts/'),
	('post', '/users/1/block/'),
	('post', '/users/1/unblock/'),
	('get', '/groups/'),
	('get', '/groups/add/'),
	('post', '/groups/delete/'),
	('get', '/groups/1/'),
	('get', '/groups/1/delete/'),
	('get', '/conversations/'),
	('get', '/conversations/1/'),
	('get', '/conversations/1/report/pdf/'),
	('get', '/badwords/'),
	('get', '/badwords/add/'),
	('post', '/badwords/delete/'),
	('post', '/badwords/disable/'),
	('post', '/badwords/enable/'),
	('get', '/badwords/1/'),
	('get', '/badwords/1/delete/'),
	('get', '/settings/'),
	('get', '/license/'),
]

# Every page a superuser can open from the menu, and the template it renders.
PAGES = [
	('/', 'dashboard/index.html'),
	('/dashboard/', 'dashboard/index.html'),
	('/acls/', 'acls/list.html'),
	('/acls/add/', 'acls/add.html'),
	('/users/', 'users/list.html'),
	('/users/add/', 'users/add.html'),
	('/groups/', 'groups/list.html'),
	('/groups/add/', 'groups/add.html'),
	('/groups/1/', 'groups/edit.html'),
	('/conversations/', 'conversations/list.html'),
	('/badwords/', 'badwords/list.html'),
	('/badwords/add/', 'badwords/add.html'),
	('/settings/', 'settings/update.html'),
	('/license/', 'license/index.html'),
	('/profile/update/', 'profiles/update.html'),
]

class RoutingTest(LivemgrTestCase):
	def test_named_routes(self):
		for name, args, path in ROUTES:
			self.assertEqual(reverse('webui:%s' % name, args=args), path)

	def test_application_namespace(self):
		# UserTable renders links with the 'livemgr' application namespace.
		for name, args, path in ROUTES:
			self.assertEqual(reverse('livemgr:%s' % name, args=args), path)

class AuthenticationTest(LivemgrTestCase):
	def test_anonymous_users_are_sent_to_login(self):
		for method, path in PROTECTED:
			response = getattr(self.client, method)(path)
			self.assertRedirectsToLogin(response)

	def test_anonymous_redirect_ends_on_the_login_page(self):
		response = self.client.get('/acls/', follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'profiles/login.html')

	def test_anonymous_users_cannot_change_data(self):
		acl = self.make_acl()
		self.client.post('/acls/delete/', {'selection': [acl.id]})
		self.client.get('/acls/%d/delete/' % acl.id)
		self.assertTrue(Acl.objects.filter(pk=acl.id).exists())

	def test_login_page(self):
		response = self.client.get('/login/')
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'profiles/login.html')

	def test_login_redirects_to_the_dashboard(self):
		self.create_account('operator')
		response = self.client.post('/login/', {'username': 'operator', 'password': self.PASSWORD})
		self.assertRedirectsTo(response, '/dashboard')
		self.assertTrue('_auth_user_id' in self.client.session)

	def test_login_honors_next(self):
		self.create_account('operator')
		response = self.client.post('/login/',
			{'username': 'operator', 'password': self.PASSWORD, 'next': '/acls/'})
		self.assertRedirectsTo(response, '/acls/')

	def test_login_with_wrong_password(self):
		self.create_account('operator')
		response = self.client.post('/login/', {'username': 'operator', 'password': 'wrong'})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)
		self.assertFalse('_auth_user_id' in self.client.session)

	def test_logout(self):
		self.login(self.create_account('operator'))
		response = self.client.get('/logout/')
		self.assertRedirectsTo(response, '/login/')
		self.assertFalse('_auth_user_id' in self.client.session)

	def test_inactive_accounts_cannot_log_in(self):
		account = self.create_account('operator')
		account.is_active = False
		account.save()
		self.assertFalse(self.client.login(username='operator', password=self.PASSWORD))

class AuthorizationTest(LivemgrTestCase):
	def test_users_without_permissions_are_sent_to_login(self):
		self.login(self.create_account('nobody'))
		for method, path in PROTECTED:
			if path == '/':
				continue # same view as /dashboard/
			response = getattr(self.client, method)(path)
			self.assertRedirectsToLogin(response)

	def test_superuser_can_open_every_page(self):
		self.login_superuser()
		for path, template in PAGES:
			response = self.client.get(path)
			self.assertEqual(response.status_code, 200, path)
			self.assertTemplateUsed(response, template)

	def test_profile_page_only_requires_login(self):
		self.login(self.create_account('nobody'))
		self.assertEqual(self.client.get('/profile/update/').status_code, 200)

	def test_license_requires_a_superuser(self):
		self.login(self.create_account('operator', permissions=['see_dashboard']))
		self.assertRedirectsToLogin(self.client.get('/license/'))

	def test_auditor_group(self):
		account = self.create_account('watcher')
		account.groups.add(Group.objects.get(name='auditor'))
		self.login(account)
		for path in ['/', '/dashboard/', '/conversations/']:
			self.assertEqual(self.client.get(path).status_code, 200, path)
		for path in ['/acls/', '/users/', '/groups/', '/badwords/', '/settings/', '/license/']:
			self.assertRedirectsToLogin(self.client.get(path))

	def test_menu_only_shows_permitted_sections(self):
		account = self.create_account('watcher')
		account.groups.add(Group.objects.get(name='auditor'))
		self.login(account)
		response = self.client.get('/dashboard/')
		self.assertContains(response, 'href="/conversations/"')
		self.assertContains(response, 'Welcome, watcher')
		for path in ['/acls/', '/users/', '/groups/', '/badwords/', '/settings/', '/license/']:
			self.assertNotContains(response, 'href="%s"' % path)

	def test_menu_for_superuser(self):
		self.login_superuser()
		response = self.client.get('/dashboard/')
		for path in ['/acls/', '/users/', '/groups/', '/conversations/', '/badwords/',
				'/settings/', '/license/']:
			self.assertContains(response, 'href="%s"' % path)

class HttpMethodTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()

	def test_post_only_views_reject_get(self):
		for path in ['/acls/delete/', '/groups/delete/', '/badwords/delete/',
				'/badwords/disable/', '/badwords/enable/', '/users/1/block/', '/users/1/unblock/']:
			self.assertEqual(self.client.get(path).status_code, 400, path)

	def test_get_only_views_reject_post(self):
		user = self.make_user()
		for path in ['/dashboard/', '/conversations/1/', '/conversations/1/report/pdf/',
				'/license/', '/users/%d/delete/' % user.id]:
			self.assertEqual(self.client.post(path).status_code, 400, path)

class DjangoInstallationTest(LivemgrTestCase):
	"""
	Django 1.2 and 1.3 install their data files with a setup.py trick that breaks when
	pip builds a wheel (see requirements.txt): translations and the admin
	templates silently go missing.
	"""
	def test_django_translations_are_installed(self):
		from django.utils.translation import check_for_language
		self.assertTrue(check_for_language('pt-br'))

	def test_admin_site(self):
		self.login_superuser()
		response = self.client.get('/admin/')
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'admin/index.html')

class ErrorPagesTest(LivemgrTestCase):
	def test_404(self):
		self.login_superuser()
		response = self.client.get('/acls/999999/')
		self.assertEqual(response.status_code, 404)
		self.assertTemplateUsed(response, '404.html')

	def test_unknown_url(self):
		response = self.client.get('/no-such-page/')
		self.assertEqual(response.status_code, 404)
		self.assertContains(response, "/no-such-page/ doesn't exist.", status_code=404)

	def test_500_handler(self):
		request = HttpRequest()
		request.user = AnonymousUser()
		response = error_500(request)
		self.assertEqual(response.status_code, 200) # returned as-is by the handler
		self.assertEqual(response.content.strip(), 'Internal error.')

	def test_csrf_failure_view(self):
		from django.test.client import Client
		client = Client(enforce_csrf_checks=True)
		response = client.post('/login/', {'username': 'x', 'password': 'y'})
		self.assertTemplateUsed(response, 'profiles/no_cookie.html')

class AjaxCsrfTest(LivemgrTestCase):
	"""
	Since Django 1.2.5 AJAX requests go through the CSRF check too. The layout
	makes jQuery send the token in the X-CSRFToken header.
	"""
	def setUp(self):
		from django.test.client import Client
		self.client = Client(enforce_csrf_checks=True)
		self.account = self.login_superuser()

	def csrf_token(self):
		response = self.client.get('/dashboard/')
		token = self.client.cookies['csrftoken'].value
		self.assertContains(response, "xhr.setRequestHeader('X-CSRFToken', '%s')" % token)
		return token

	def test_dashboard_query(self):
		response = self.client.post('/dashboard/query/', {'period': 'month'},
			HTTP_X_CSRFTOKEN=self.csrf_token(), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response['Content-Type'], 'application/json')

	def test_change_page_size(self):
		self.client.post('/acls/', {'per_page': '50'},
			HTTP_X_CSRFTOKEN=self.csrf_token(), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(self.profile_of(self.account).per_page_acls, 50)

	def test_without_the_header(self):
		self.csrf_token()
		response = self.client.post('/dashboard/query/', {'period': 'month'},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertTemplateUsed(response, 'profiles/no_cookie.html')
