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
from django.shortcuts import render
from django.utils.translation import gettext as _, gettext_lazy
from webui.common.decorators.rest import rest_multiple
from webui.common.http import method
from webui.common.utils import flash_success, flash_form_error, NoLabelSuffixMixin
from webui.livemgr.models.setting import Setting

class SettingsUpdateForm(NoLabelSuffixMixin, forms.Form):
	PROTOCOL_CHOICES = (
		(8, '8'),
		(9, '9'),
		(10, '10'),
		(11, '11'),
		(12, '12'),
		(13, '13'),
		(14, '14'),
		(15, '15'),
		(16, '16'),
		(17, '17'),
		(18, '18'),
	)
	min_protocol_version = forms.ChoiceField(choices=PROTOCOL_CHOICES, label=gettext_lazy("Minimum"), required=False)
	max_protocol_version = forms.ChoiceField(choices=PROTOCOL_CHOICES, label=gettext_lazy("Maximum"), required=False)
	allow_self_reg = forms.BooleanField(label=gettext_lazy("Allow self registration"), required=False)
	filtered_msg = forms.CharField(label=gettext_lazy("Filtered"), required=True)
	default_warning = forms.CharField(label=gettext_lazy("Disclaimer"), required=True)
	def __init__(self, *args, **kwargs):
		super(SettingsUpdateForm, self).__init__(*args, **kwargs)
		self.load()
	def load(self):
		self.fields['min_protocol_version'].initial = int(Setting.objects.get(name='min_protocol_version').value)
		self.fields['max_protocol_version'].initial = int(Setting.objects.get(name='max_protocol_version').value)
		self.fields['allow_self_reg'].initial = int(Setting.objects.get(name='allow_self_reg').value)
		self.fields['filtered_msg'].initial = Setting.objects.get(name='filtered_msg').value
		self.fields['default_warning'].initial = Setting.objects.get(name='default_warning').value
#		print 'min_protocol_version = %i' % self.fields['min_protocol_version'].initial
#		print 'max_protocol_version = %i' % self.fields['max_protocol_version'].initial
#		print 'allow_self_reg = %i' % self.fields['allow_self_reg'].initial
	def clean_filtered_msg(self):
		# Remove leading and trailing white-spaces
		value = self.cleaned_data['filtered_msg'].strip()
		if not value:
			raise forms.ValidationError(_("This field is required."))
		return value
	def clean_default_warning(self):
		# Remove leading and trailing white-spaces
		value = self.cleaned_data['default_warning'].strip()
		if not value:
			raise forms.ValidationError(_("This field is required."))
		return value
	def save(self):
		min_protocol_version = int(self.cleaned_data['min_protocol_version'])
		max_protocol_version = int(self.cleaned_data['max_protocol_version'])
		allow_self_reg = int(self.cleaned_data['allow_self_reg'])
		filtered_msg = self.cleaned_data['filtered_msg']
		default_warning = self.cleaned_data['default_warning']
		# Invert protocol version if necessary
		if min_protocol_version > max_protocol_version:
			min_protocol_version, max_protocol_version = max_protocol_version, min_protocol_version
		# Save everything
		Setting.objects.filter(name='min_protocol_version').update(value=min_protocol_version)
		Setting.objects.filter(name='max_protocol_version').update(value=max_protocol_version)
		Setting.objects.filter(name='allow_self_reg').update(value=allow_self_reg)
		Setting.objects.filter(name='filtered_msg').update(value=filtered_msg)
		Setting.objects.filter(name='default_warning').update(value=default_warning)
		return self

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.change_setting')
def update(request):
	if request.method == method.GET:
		form = SettingsUpdateForm()
	elif request.method == method.POST:
		form = SettingsUpdateForm(request.POST)
		if form.is_valid():
			form = form.save()
			flash_success(request, _('The settings were changed successfully.'))
		else:
			flash_form_error(request, form)
	template_name = 'settings/update.html'
	extra_context = {
		'menu': 'settings',
		'form': form
	}
	return render(request, template_name, extra_context)
