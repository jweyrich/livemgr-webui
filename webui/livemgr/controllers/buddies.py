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
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.query_utils import Q
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple, rest_post
from webui.common.http import method
from webui.livemgr.models import User
from webui.livemgr.models.buddy import Buddy
from webui.livemgr.models.profile import Profile
from webui.livemgr.utils.formatters import format_boolean, format_user_status
import django_tables as tables

class BuddyTable(tables.ModelTable):
	class Meta:
		model = Buddy
		exclude = ['user']
		columns = ['username', 'status', 'isblocked', 'displayname', 'psm']
	# Use ugettext_lazy because class definitions are evaluated once!
	id = tables.Column(visible=False)
	psm = tables.Column(verbose_name=ugettext_lazy('personal message'), sortable=False)
	def render_status(self, instance):
		return format_user_status(instance.status)
	def render_isblocked(self, instance):
		return format_boolean(instance.isblocked)

class BuddySearchForm(forms.Form):
	username = forms.CharField(required=False, label=ugettext_lazy("username"))
	displayname = forms.CharField(required=False, label=ugettext_lazy("display name"))
	status = forms.ChoiceField(User.CHOICES_STATUS, required=False, label=ugettext_lazy("status"))
	def __init__(self, *args, **kwargs):
		super(BuddySearchForm, self).__init__(*args, **kwargs)
		self.fields['status'].choices = [('', '----------')] + self.fields['status'].choices

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.see_buddy')
def index(request, user_id):
	user_id = long(user_id)
	from_user = get_object_or_404(User, pk=user_id)
	if request.method == method.GET:
		qset = Buddy.objects.filter(user=user_id)
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_buddies=per_page)
			return HttpResponse()
		form = BuddySearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		qset = Buddy.objects.filter(user=user_id)
		if values['username']:
			qset = qset.filter(username__icontains=values['username'])
		if values['displayname']:
			qset = qset.filter(displayname__icontains=values['displayname'])
		if values['status']:
			qset = qset.filter(status=values['status'])
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', 'username')
	result = CustomPaginator(qset) \
		.instantiate(BuddyTable, qset, order_by=order_by) \
		.with_request(request)
	page = result.page(None, profile.per_page_buddies)
	context_instance = RequestContext(request)
	template_name = 'buddies/list.html'
	extra_context = {
		'menu': 'users',
		'table': result.instance,
		'page': page,
		'from_user': from_user,
		'search_form': BuddySearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_post
@login_required
@permission_required('livemgr.change_buddy')
def block(request, user_id):
	user_id = long(user_id)
	selected = request.POST.getlist('selection')
	Buddy.objects.filter(Q(user=user_id) & Q(pk__in=selected)) \
		.update(isblocked=True)
	return HttpResponse()

@rest_post
@login_required
@permission_required('livemgr.change_buddy')
def unblock(request, user_id):
	user_id = long(user_id)
	selected = request.POST.getlist('selection')
	Buddy.objects.filter(Q(user=user_id) & Q(pk__in=selected)) \
		.update(isblocked=False)
	return HttpResponse()
