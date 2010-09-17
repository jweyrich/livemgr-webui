from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest, HttpResponseRedirect, \
	HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.framework import CustomPaginator
from webui.framework.decorators.rest import rest_multiple
from webui.framework.http import method
from webui.framework.utils import request_has_error, FormAction, flash_info, \
	InView, flash_success, flash_form_error
from webui.imdata.models import User
from webui.imdata.models.profile import Profile
from webui.imdata.models.usergroup import UserGroup
from webui.imdata.utils.formatters import format_boolean, format_user_status
import django_tables as tables

class UserTable(tables.ModelTable):
	class Meta:
		model = User
		exclude = []
		columns = ['username', 'status', 'isenabled', 'displayname',
			'psm', 'lastlogin', 'group', 'contacts']
	# Use ugettext_lazy because class definitions are evaluated once!
	id = tables.Column(visible=False)
	group = tables.Column(verbose_name=ugettext_lazy('group'), sortable=True)
	username = tables.Column(verbose_name=ugettext_lazy('username'), sortable=True)
	displayname = tables.Column(verbose_name=ugettext_lazy('display name'), sortable=True)
	psm = tables.Column(verbose_name=ugettext_lazy('personal message'), sortable=False)
	status = tables.Column(verbose_name=ugettext_lazy('status'), sortable=True)
	lastlogin = tables.Column(verbose_name=ugettext_lazy('last login'), sortable=True)
	isenabled = tables.Column(verbose_name=ugettext_lazy('enabled'), sortable=False)
	contacts =  tables.Column(verbose_name=ugettext_lazy('contacts'), sortable=False)
	def render_group(self, instance):
		return mark_safe('<a href="%s">%s</a>' % (
			reverse('imdata:groups-edit', args=[instance.group.id]),
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
		# TODO: don't execute an extra query per-result
		if instance.buddies.count():
			return mark_safe('<a href="%s">%s</a>' % (
				reverse('imdata:buddies-index', args=[instance.id]),
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
#	def clean_username(self):
#		return self.instance.username

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
@permission_required('imdata.see_user')
def index(request):
	if request.method == method.GET:
		qset = User.objects.all()
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_users = per_page)
			return HttpResponse()
		form = UserSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		qset = User.objects.all()
		if values['username']:
			qset = qset.filter(username__icontains = values['username'])
		if values['displayname']:
			qset = qset.filter(displayname__icontains = values['displayname'])
		if values['group']:
			qset = qset.filter(group = values['group'])
		if values['status']:
			qset = qset.filter(status = values['status'])
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', 'username')
	table = UserTable(qset, order_by = order_by)
	paginator = CustomPaginator(request, table.rows, profile.per_page_users)
	context_instance = RequestContext(request)
	template_name = 'users/list.html'
	extra_context = {
		'menu': 'users',
		'table': table,
		'paginator': paginator,
		'search_form': UserSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.change_user')
def edit(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(User, pk=object_id)
	if request.method == method.GET:
		form = UserForm(instance=model)
	elif request.method == method.POST:
		form = UserForm(request.POST, instance=model)
		if form.is_valid():
			model = form.save(True)
			flash_success(request,
				_('The user \'%s\' was changed successfully.') % model.username)
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.EDIT, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'users/edit.html'
	extra_context = {
		'menu': 'users',
		'form': form,
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.add_user')
def add(request):
	object_id = None
	if request.method == method.GET:
		form = UserForm()
	elif request.method == method.POST:
		form = UserForm(request.POST)
		if form.is_valid():
			model = form.save(False)
			model.status = 'FLN'
			model.save()
			object_id = model.id
			flash_success(request,
				_('The user \'%s\' was created successfully.') % model.username)
			form = UserForm()
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.ADD, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'users/add.html'
	extra_context = { 'menu': 'users', 'form': form }
	return render_to_response(template_name, extra_context, context_instance)

#@rest_post
#@login_required
#@permission_required('imdata.delete_user')
#def delete(request, object_id):
#	model = get_object_or_404(User, pk=object_id)
#	model.delete()
#	return HttpResponse()

#@rest_post
#@login_required
#@permission_required('imdata.delete_user')
#def delete_many(request):
#	selected = request.POST.getlist('selection')
#	User.objects.filter(pk__in=selected).delete()
#	return HttpResponse()
