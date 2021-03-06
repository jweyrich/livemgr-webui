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
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple, rest_post
from webui.common.http import method
from webui.common.utils import request_has_error, FormAction, flash_info, InView, flash_success, \
	flash_form_error
from webui.livemgr.models import Acl
from webui.livemgr.models.profile import Profile
from webui.livemgr.utils.formatters import format_acl_action
import django_tables as tables

class AclTable(tables.ModelTable):
	class Meta:
		model = Acl
		exclude = []
		columns = ['action', 'localim', 'remoteim']
	id = tables.Column(visible=False)
	def render_action(self, instance):
		return format_acl_action(instance.action)

class AclForm(ModelForm):
	class Meta:
		model = Acl
		fields = ('action', 'localim', 'remoteim')
	def __init__(self, *args, **kwargs):
		super(AclForm, self).__init__(*args, **kwargs)
		self.fields['localim'].widget.attrs = \
			{'title':_('You can use the asterisk as a wildcard character. '
					'Example:<br/><i>*@example.com</i>')}
		self.fields['remoteim'].widget.attrs = \
			{'title':_('You can use the asterisk as a wildcard character. '
					'Example:<br/><i>*@example.com</i>')}

class AclSearchForm(forms.Form):
	acl = forms.CharField(required=False)
	action = forms.ChoiceField(Acl.CHOICES_ACTIONS, required=False, label=ugettext_lazy('action'))
	localim = forms.CharField(required=False, label=ugettext_lazy('user'))
	remoteim = forms.CharField(required=False, label=ugettext_lazy('buddy'))
	def __init__(self, *args, **kwargs):
		super(AclSearchForm, self).__init__(*args, **kwargs)
		self.fields['action'].choices = [('', '----------')] + self.fields['action'].choices

def _redirect_if_needed(request, action, object_id=None):
	if not request_has_error(request):
		if request.POST.get(FormAction.SAVE_AND_LIST):
			return HttpResponseRedirect(reverse('webui:acls-index'))
		elif request.POST.get(FormAction.SAVE_AND_ADD):
			flash_info(request, _('You may add another.'))
			if action != InView.ADD:
				return HttpResponseRedirect(reverse('webui:acls-add'))
		elif request.POST.get(FormAction.SAVE_AND_EDIT):
			if action != InView.EDIT:
				return HttpResponseRedirect(reverse('webui:acls-edit', args=[object_id]))
	return None

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.see_acl')
def index(request):
	if request.method == method.GET:
		qset = Acl.objects.all()
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_acls=per_page)
			return HttpResponse()
		form = AclSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		qset = Acl.objects.all()
		if values['acl']:
			qset = qset.filter(
				Q(localim__icontains=values['acl']) |
				Q(remoteim__icontains=values['acl'])
			)
		if values['action']:
			qset = qset.filter(action=values['action'])
		if values['localim']:
			qset = qset.filter(localim__icontains=values['localim'])
		if values['remoteim']:
			qset = qset.filter(remoteim__icontains=values['remoteim'])
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', 'localim')
	result = CustomPaginator(qset) \
		.instantiate(AclTable, qset, order_by=order_by) \
		.with_request(request)
	page = result.page(None, profile.per_page_acls)
	context_instance = RequestContext(request)
	template_name = 'acls/list.html'
	extra_context = {
		'menu': 'acls',
		'table': result.instance,
		'page': page,
		'search_form': AclSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.change_acl')
def edit(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(Acl, pk=object_id)
	if request.method == method.GET:
		form = AclForm(instance=model)
	elif request.method == method.POST:
		form = AclForm(request.POST, instance=model)
		if form.is_valid():
			model = form.save(True)
			flash_success(request,
				_('The acl %d was changed successfully.') % object_id)
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.EDIT, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'acls/edit.html'
	extra_context = {
		'menu': 'acls',
		'form': form,
		'model':  model,
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.add_acl')
def add(request):
	object_id = None
	if request.method == method.GET:
		form = AclForm()
	elif request.method == method.POST:
		form = AclForm(request.POST)
		if form.is_valid():
			model = form.save(True)
			object_id = model.id
			flash_success(request,
				_('The acl %d was created successfully.') % object_id)
			form = AclForm()
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.ADD, object_id)
		if redir != None: return redir
	#print form.errors['__all__'][0]
	context_instance = RequestContext(request)
	template_name = 'acls/add.html'
	extra_context = { 'menu': 'acls', 'form': form }
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.delete_acl')
def delete(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(Acl, pk=object_id)
	model.delete()
	if request.method == method.POST:
		return HttpResponse()
	else:
		return HttpResponseRedirect(reverse('webui:acls-index'))

@rest_post
@login_required
@permission_required('livemgr.delete_acl')
def delete_many(request):
	selected = request.POST.getlist('selection')
	Acl.objects.filter(pk__in=selected).delete()
	return HttpResponse()
