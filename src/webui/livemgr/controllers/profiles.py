from django import forms
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.utils.translation import gettext as _, ugettext_lazy, check_for_language
from django.views.i18n import set_language
from webui import settings
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple
from webui.common.http import method
from webui.common.utils import flash_success, flash_form_error
from webui.livemgr.models.profile import Profile
from webui.livemgr.utils.formatters import format_boolean
import django_tables as tables

class ProfileTable(tables.ModelTable):
	class Meta:
		model = User
		columns = ['username', 'email', 'is_active',
				'last_login', 'date_joined', 'groups']
	# Use ugettext_lazy because class definitions are evaluated once!
	id = tables.Column(visible=False)
	email = tables.Column(verbose_name=ugettext_lazy('email'), sortable=True)
	groups = tables.Column(verbose_name=ugettext_lazy('groups'), sortable=False)
	def render_is_active(self, instance):
		return format_boolean(instance.is_active)
	def render_groups(self, instance):
		return ', '.join([g.name for g in instance.groups.all()])

class UserUpdateForm(ModelForm): # Do NOT use PasswordChangeForm
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')
	old_password = forms.CharField(label=ugettext_lazy('Current password'), widget=forms.PasswordInput, required=False)
	new_password1 = forms.CharField(label=ugettext_lazy('New password'), widget=forms.PasswordInput, required=False)
	new_password2 = forms.CharField(label=ugettext_lazy('New password confirmation'), widget=forms.PasswordInput, required=False)
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

class ProfileUpdateForm(ModelForm):
	class Meta:
		model = Profile
		fields = ['language', 'debug']
	language = forms.ChoiceField(settings.LANGUAGES, label=ugettext_lazy('Language'), required=False)
	debug = forms.BooleanField(label=ugettext_lazy('Enable debug'), required=False)

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
	context_instance = RequestContext(request)
	template_name = 'profiles/list.html'
	extra_context = {
		'menu': 'profiles',
		'table': result.table,
		'page': page,
		'search_form': ProfileSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

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
	context_instance = RequestContext(request)
	template_name = 'profiles/update.html'
	extra_context = {
		'menu': '',
		'form_user': form_user,
		'form_profile': form_profile,
		'show_debug': 'debug' in request.GET
	}
	return render_to_response(template_name, extra_context, context_instance)

def set_language_local(request, response, lang_code):
	if lang_code and check_for_language(lang_code):
		if hasattr(request, 'session'):
			request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
		else:
			response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
	return response

def login(request, *args, **kwargs):
	response = views.login(request, *args, **kwargs)
	if hasattr(request.user, 'get_profile'):
		set_language_local(request, response, request.user.get_profile().language)
	return response

def no_cookie(request, *args, **kwargs):
	context_instance = RequestContext(request)
	template_name = 'profiles/no_cookie.html'
	extra_context = {}
	return render_to_response(template_name, extra_context, context_instance)
