from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common.decorators.rest import rest_multiple
from webui.common.http import method
from webui.common.utils import flash_success, flash_form_error
from webui.imdata.models.setting import Setting

class SettingsUpdateForm(forms.Form):
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
	min_protocol_version = forms.ChoiceField(PROTOCOL_CHOICES, label=ugettext_lazy("Minimum"), required=False)
	max_protocol_version = forms.ChoiceField(PROTOCOL_CHOICES, label=ugettext_lazy("Maximum"), required=False)
	allow_self_reg = forms.BooleanField(label=ugettext_lazy("Allow self registration"), required=False)
	filtered_msg = forms.CharField(label=ugettext_lazy("Filtered"), required=True)
	default_warning = forms.CharField(label=ugettext_lazy("Disclaimer"), required=True)
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
@permission_required('imdata.change_setting')
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
	context_instance = RequestContext(request)
	template_name = 'settings/update.html'
	extra_context = {
		'menu': 'settings',
		'form': form
	}
	return render_to_response(template_name, extra_context, context_instance)
