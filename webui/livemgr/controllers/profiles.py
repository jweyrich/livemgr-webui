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

from django import forms
from django.conf import settings
from django.contrib.auth import update_session_auth_hash, views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils import translation
from django.utils.translation import gettext as _, ugettext_lazy, check_for_language
from django.views.i18n import set_language
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple
from webui.common.http import method
from webui.common.utils import flash_success, flash_form_error, NoLabelSuffixMixin
from webui.livemgr.models.profile import Profile
from webui.livemgr.utils.formatters import format_boolean
import django
import django_tables2 as tables

# Django 1.9 strips the whitespace around CharField values. Passwords keep it,
# as in django.contrib.auth's forms; older versions have no strip argument.
PASSWORD_FIELD_KWARGS = {'strip': False} if django.VERSION >= (1, 9) else {}

class ProfileTable(tables.Table):
	class Meta:
		model = User
		fields = ('username', 'email', 'is_active',
				'last_login', 'date_joined', 'groups')
		default = '' # Not '—' for empty values
	# Use ugettext_lazy because class definitions are evaluated once!
	id = tables.Column(visible=False)
	email = tables.Column(verbose_name=ugettext_lazy('email'), orderable=True)
	groups = tables.Column(verbose_name=ugettext_lazy('groups'), orderable=False)
	def render_is_active(self, record):
		return format_boolean(record.is_active)
	def render_groups(self, record):
		return ', '.join([g.name for g in record.groups.all()])

class UserUpdateForm(NoLabelSuffixMixin, ModelForm): # Do NOT use PasswordChangeForm
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')
	old_password = forms.CharField(label=ugettext_lazy('Current password'), widget=forms.PasswordInput, required=False,
		**PASSWORD_FIELD_KWARGS)
	new_password1 = forms.CharField(label=ugettext_lazy('New password'), widget=forms.PasswordInput, required=False,
		**PASSWORD_FIELD_KWARGS)
	new_password2 = forms.CharField(label=ugettext_lazy('New password confirmation'), widget=forms.PasswordInput, required=False,
		**PASSWORD_FIELD_KWARGS)
	def clean_old_password(self):
		old_password = self.cleaned_data['old_password']
		if old_password and not self.instance.check_password(old_password):
			raise forms.ValidationError(_('Your current password is incorrect. Please type it again.'))
		return old_password
	def clean_new_password2(self):
		password1 = self.cleaned_data.get('new_password1')
		password2 = self.cleaned_data.get('new_password2')
		if password1 or password2:
			if password1 != password2:
				raise forms.ValidationError(_("The two password fields don\'t match."))
		return password2
	def save(self, commit=True):
		new_password1 = self.cleaned_data['new_password1']
		if new_password1:
			self.instance.set_password(new_password1)
		if commit:
			self.instance.save()
		return self.instance

class ProfileUpdateForm(NoLabelSuffixMixin, ModelForm):
	class Meta:
		model = Profile
		fields = ['language', 'debug']
	language = forms.ChoiceField(choices=settings.LANGUAGES, label=ugettext_lazy('Language'), required=False)
	debug = forms.BooleanField(label=ugettext_lazy('Enable debug'), required=False)

class LoginForm(NoLabelSuffixMixin, AuthenticationForm):
	pass

class ProfileSearchForm(forms.Form):
	username = forms.CharField(required=False, label=ugettext_lazy('username'))
	email = forms.CharField(required=False, label=ugettext_lazy('email'))
	group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label=ugettext_lazy('group'))

@rest_multiple([method.GET, method.POST])
@login_required
#@permission_required('livemgr.see_profile')
def index(request):
	if request.method == method.GET:
		qset = User.objects.all()
	elif request.method == method.POST:
		form = ProfileSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		qset = User.objects.all()
		if values['username']:
			qset = qset.filter(username__icontains=values['username'])
		if values['email']:
			qset = qset.filter(email__icontains=values['email'])
		if values['group']:
			qset = qset.filter(groups=values['group'])
	order_by = request.GET.get('sort', 'username')
	result = CustomPaginator(qset) \
		.using_class(ProfileTable, qset, order_by=order_by) \
		.with_request(request)
	page = result.page(None, 5)
	template_name = 'profiles/list.html'
	extra_context = {
		'menu': 'profiles',
		'table': result.table,
		'page': page,
		'search_form': ProfileSearchForm()
	}
	return render(request, template_name, extra_context)

#@rest_multiple([method.GET, method.POST])
#@login_required
#@permission_required('livemgr.change_profile')
#def edit(request, object_id):
#	return HttpResponse()
#
#@rest_multiple([method.GET, method.POST])
#@login_required
#@permission_required('livemgr.change_profile')
#def add(request):
#	return HttpResponse()

@rest_multiple([method.GET, method.POST])
@login_required
def update(request):
	user = get_object_or_404(User, pk=request.user.id)
	profile = get_object_or_404(Profile, user=request.user.id)
	if request.method == method.GET:
		form_user = UserUpdateForm(instance=user)
		form_profile = ProfileUpdateForm(instance=profile)
	if request.method == method.POST:
		form_user = UserUpdateForm(request.POST.copy(), instance=user)
		form_profile = ProfileUpdateForm(request.POST.copy(), instance=profile)
		if form_user.is_valid() and form_profile.is_valid():
			user = form_user.save(True)
			if form_user.cleaned_data['new_password1']:
				# SessionAuthenticationMiddleware ends the sessions of a user
				# whose password changed; keep this one.
				update_session_auth_hash(request, user)
			form_user.data['old_password'] = ''
			form_user.data['new_password1'] = ''
			form_user.data['new_password2'] = ''
			profile = form_profile.save(True)
			flash_success(request, _('Your profile was updated successfully.'))
			return set_language(request)
		else:
			form_wrong = form_user if not form_user.is_valid() else form_profile
			flash_form_error(request, form_wrong)
	#print 'language = ' + repr(form.base_fields['language'].initial)
	template_name = 'profiles/update.html'
	extra_context = {
		'menu': '',
		'form_user': form_user,
		'form_profile': form_profile,
		'show_debug': 'debug' in request.GET
	}
	return render(request, template_name, extra_context)

# Django 1.7 stores the language under its own session key, the same one its
# set_language view uses. Older versions use the cookie name.
LANGUAGE_SESSION_KEY = getattr(translation, 'LANGUAGE_SESSION_KEY', settings.LANGUAGE_COOKIE_NAME)

def set_language_local(request, response, lang_code):
	if lang_code and check_for_language(lang_code):
		if hasattr(request, 'session'):
			request.session[LANGUAGE_SESSION_KEY] = lang_code
		else:
			response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
	return response

def login(request, *args, **kwargs):
	# Django 1.11 deprecates the login() view for LoginView, which names its
	# authentication_form option form_class.
	if django.VERSION >= (1, 11):
		kwargs.setdefault('form_class', LoginForm)
		response = views.LoginView.as_view(**kwargs)(request, *args)
	else:
		kwargs.setdefault('authentication_form', LoginForm)
		response = views.login(request, *args, **kwargs)
	if hasattr(request.user, 'profile'):
		set_language_local(request, response, request.user.profile.language)
	return response

def no_cookie(request, *args, **kwargs):
	template_name = 'profiles/no_cookie.html'
	extra_context = {}
	return render(request, template_name, extra_context)
