from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.db.utils import IntegrityError
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, \
	HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple, rest_get
from webui.common.http import method
from webui.common.utils import FormAction, flash_info, InView, flash_success, flash_form_error, \
	flash_error, request_has_error
from webui.livemgr.models import User
from webui.livemgr.models.profile import Profile
from webui.livemgr.models.usergroup import UserGroup
from webui.livemgr.utils.formatters import format_boolean, format_user_status
import django_tables as tables

class UserTable(tables.ModelTable):
	class Meta:
		model = User
		exclude = []
		columns = ['username', 'status', 'isenabled', 'displayname',
			'psm', 'lastlogin', 'group', 'contacts']
	# Use ugettext_lazy because class definitions are evaluated once!
	id = tables.Column(visible=False)
	psm = tables.Column(verbose_name=ugettext_lazy('personal message'), sortable=False)
	contacts = tables.Column(verbose_name=ugettext_lazy('contacts'), sortable=False)
	def render_group(self, instance):
		return mark_safe('<a href="%s">%s</a>' % (
			reverse('livemgr:groups-edit', args=[instance.group.id]),
			instance.group.groupname))
	def render_status(self, instance):
		return format_user_status(instance.status)
	def render_lastlogin(self, instance):
		if not instance.lastlogin:
			return mark_safe(_('Never logged'))
		return mark_safe(instance.lastlogin)
	def render_isenabled(self, instance):
		return format_boolean(instance.isenabled)
	def render_contacts(self, instance):
		# TODO(jweyrich): Avoid executing an extra query per user
		#if instance.buddies.count():
		if instance.buddy_count:
			return mark_safe('<a href="%s">%s</a>' % (
				reverse('livemgr:buddies-index', args=[instance.id]),
				_('Manage')))
		else:
			return mark_safe(_('None'))

class UserForm(ModelForm):
#	id = forms.IntegerField(widget=forms.HiddenInput())
	class Meta:
		model = User
		#fields = ('id', 'username', 'group', 'isenabled')
		fields = ('username', 'group', 'isenabled')
	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		instance = getattr(self, 'instance', None)
		if instance and instance.id:
			#self.fields['id'] = forms.IntegerField(widget=forms.HiddenInput())
			if not instance.lastlogin == None:
				self.fields['username'].widget.attrs['readonly'] = True
	def clean(self):
		cleaned_data = self.cleaned_data
		username = cleaned_data.get('username')
		if not username:
			return cleaned_data
		username = username.strip().lower()
		if self.instance.lastlogin:
			if self.instance.username != username:
				msg = _('Changing the username for a user that already logged in is not permitted.')
				self._errors['username'] = self.error_class([msg])
				del cleaned_data['username']
		cleaned_data['username'] = username
		return cleaned_data

class UserSearchForm(forms.Form):
	username = forms.CharField(required=False, label=ugettext_lazy("username"))
	displayname = forms.CharField(required=False, label=ugettext_lazy("display name"))
	group = forms.ModelChoiceField(queryset=UserGroup.objects.all(), required=False, label=ugettext_lazy("group"))
	status = forms.ChoiceField(User.CHOICES_STATUS, required=False, label=ugettext_lazy("status"))
	def __init__(self, *args, **kwargs):
		super(UserSearchForm, self).__init__(*args, **kwargs)
		self.fields['status'].choices = [('', '----------')] + self.fields['status'].choices

def _redirect_if_needed(request, action, object_id=None):
	if not request_has_error(request):
		if request.POST.get(FormAction.SAVE_AND_LIST):
			return HttpResponseRedirect(reverse('webui:users-index'))
		elif request.POST.get(FormAction.SAVE_AND_ADD):
			flash_info(request, _('You may add another.'))
			if action != InView.ADD:
				return HttpResponseRedirect(reverse('webui:users-add'))
		elif request.POST.get(FormAction.SAVE_AND_EDIT):
			if action != InView.EDIT:
				return HttpResponseRedirect(reverse('webui:users-edit', args=[object_id]))
	return None

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.see_user')
def index(request):
	if request.method == method.GET:
		qset = User.objects.all()
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_users=per_page)
			return HttpResponse()
		form = UserSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		qset = User.objects.all()
		if values['username']:
			qset = qset.filter(username__icontains=values['username'])
		if values['displayname']:
			qset = qset.filter(displayname__icontains=values['displayname'])
		if values['group']:
			qset = qset.filter(group=values['group'])
		if values['status']:
			qset = qset.filter(status=values['status'])
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', 'username')
	qset2 = qset.select_related('group', 'buddy').annotate(buddy_count=Count('buddies'))
	result = CustomPaginator(qset) \
		.instantiate(UserTable, qset2, order_by=order_by) \
		.with_request(request) \
		.with_count(qset.count())
	page = result.page(None, profile.per_page_users)
	context_instance = RequestContext(request)
	template_name = 'users/list.html'
	extra_context = {
		'menu': 'users',
		'table': result.instance,
		'page': page,
		'search_form': UserSearchForm(),
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.change_user')
def edit(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(User, pk=object_id)
	can_delete = model.lastlogin == None
	if request.method == method.GET:
		form = UserForm(instance=model)
	elif request.method == method.POST:
		form = UserForm(request.POST, instance=model)
		if form.is_valid():
			try:
				model = form.save(True)
				flash_success(request,
					_('The user \'%s\' was changed successfully.') % model.username)
			except IntegrityError:
				flash_error(request,
					_('The user \'%s\' already exists.') % form.cleaned_data['username'].strip().lower())
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.EDIT, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'users/edit.html'
	extra_context = {
		'menu': 'users',
		'form': form,
		'model':  model,
		'can_delete': can_delete,
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.add_user')
def add(request):
	object_id = None
	if request.method == method.GET:
		form = UserForm()
	elif request.method == method.POST:
		form = UserForm(request.POST)
		if form.is_valid():
			try:
				model = form.save(False)
				model.status = 'FLN'
				model.save()
				object_id = model.id
				flash_success(request,
					_('The user \'%s\' was created successfully.') % model.username)
				form = UserForm()
			except IntegrityError:
				flash_error(request,
					_('The user \'%s\' already exists.') % form.cleaned_data['username'].strip().lower())
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.ADD, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'users/add.html'
	extra_context = { 'menu': 'users', 'form': form }
	return render_to_response(template_name, extra_context, context_instance)

@rest_get
@login_required
@permission_required('livemgr.delete_user')
def delete(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(User, pk=object_id)
	if model.lastlogin:
		message = _('Deleting a user that already logged in is not permitted.')
		if request.method == method.POST:
			return HttpResponseForbidden(message)
		else:
			flash_error(request, message)
			return HttpResponseRedirect(reverse('webui:users-edit', args=[object_id]))
	model.delete()
	if request.method == method.POST:
		return HttpResponse()
	else:
		return HttpResponseRedirect(reverse('webui:users-index'))

#@rest_post
#@login_required
#@permission_required('livemgr.delete_user')
#def delete_many(request):
#	selected = request.POST.getlist('selection')
#	User.objects.filter(pk__in=selected).delete()
#	return HttpResponse()
