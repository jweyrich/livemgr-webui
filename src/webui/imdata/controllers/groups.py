from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.forms.models import ModelForm
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, \
	HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple, rest_post
from webui.common.http import method
from webui.common.utils import request_has_error, FormAction, flash_info, InView, flash_success, \
	flash_warning, flash_form_error, flash_error
from webui.imdata.models import UserGroup
from webui.imdata.models.grouprule import GroupRule
from webui.imdata.models.profile import Profile
from webui.imdata.models.rule import Rule
from webui.imdata.models.user import User
from webui.imdata.utils.formatters import format_boolean
import django_tables as tables

class GroupTable(tables.ModelTable):
	class Meta:
		model = UserGroup
		exclude = ['rules']
	id = tables.Column(visible=False)
	# Use ugettext_lazy because class definitions are evaluated once!
	groupname = tables.Column(verbose_name=ugettext_lazy('name'), sortable=True)
	isactive = tables.Column(verbose_name=ugettext_lazy('active'), sortable=True)
	isbuiltin = tables.Column(verbose_name=ugettext_lazy('built-in'), sortable=True, visible=False)
	description = tables.Column(verbose_name=ugettext_lazy('description'), sortable=False)
	user_count = tables.Column(verbose_name=ugettext_lazy('# of users'), sortable=False)
	def render_isactive(self, instance):
		return format_boolean(instance.isactive)

class GroupForm(ModelForm):
	class Meta:
		model = UserGroup
		fields = ('groupname', 'description', 'isactive')
	def __init__(self, *args, **kwargs):
		super(GroupForm, self).__init__(*args, **kwargs)
		self.fields['description'].widget.attrs = {'rows': '3'}
		#instance = getattr(self, 'instance', None)
		#if instance and instance.id:
		#	self.fields['description'].widget.attrs = {'rows': '3'}
	def clean(self):
		cleaned_data = self.cleaned_data
		cleaned_data['groupname'] = cleaned_data['groupname'].strip()
		return cleaned_data

class GroupSearchForm(forms.Form):
	groupname = forms.CharField(required=False, label=ugettext_lazy("name"))
	description = forms.CharField(required=False, label=ugettext_lazy("description"))

def _redirect_if_needed(request, action, object_id=None):
	if not request_has_error(request):
		if request.POST.get(FormAction.SAVE_AND_LIST):
			return HttpResponseRedirect(reverse('webui:groups-index'))
		elif request.POST.get(FormAction.SAVE_AND_ADD):
			flash_info(request, _('You may add another.'))
			if action != InView.ADD:
				return HttpResponseRedirect(reverse('webui:groups-add'))
		elif request.POST.get(FormAction.SAVE_AND_EDIT):
			if action != InView.EDIT:
				return HttpResponseRedirect(reverse('webui:groups-edit', args=[object_id]))
	return None

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.see_usergroup')
def index(request):
	if request.method == method.GET:
		qset = UserGroup.objects.all()
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_usergroups=per_page)
			return HttpResponse()
		form = GroupSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		qset = UserGroup.objects.all()
		if values['groupname']:
			qset = qset.filter(groupname__icontains=values['groupname'])
		if values['description']:
			qset = qset.filter(description__icontains=values['description'])
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', 'groupname')
	table = GroupTable(qset, order_by=order_by)
	paginator = CustomPaginator(request, table.rows, profile.per_page_usergroups)
	context_instance = RequestContext(request)
	template_name = 'groups/list.html'
	extra_context = {
		'menu': 'groups',
		'table': table,
		'paginator': paginator,
		'search_form': GroupSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.change_usergroup')
def edit(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(UserGroup, pk=object_id)
	can_delete = not model.isbuiltin
	if request.method == method.GET:
		form = GroupForm(instance=model)
	elif request.method == method.POST:
		form = GroupForm(request.POST, instance=model)
		if form.is_valid():
			class ChangedUsers:
				# Map submitted users to long
				submitted = map(long, request.POST.getlist('users'))
				# Select users that are currently part of the group
				current = list(User.objects \
					.filter(group=object_id) \
					.values_list('id', flat=True))
				added = list(set(submitted).difference(current))
				removed = list(set(current).difference(submitted))
				#print 'ChangedUsers.added = %s' % added
				#print 'ChangedUsers.removed = %s' % removed
			class ChangedRules:
				# Map submitted rules to long
				submitted = map(long, request.POST.getlist('rules'))
				# Select rules that are currently assigned to the group
				current = list(GroupRule.objects \
					.filter(group=object_id) \
					.values_list('rule_id', flat=True))
				added = list(set(submitted).difference(current))
				removed = list(set(current).difference(submitted))
				#print 'ChangedRules.added = %s' % added
				#print 'ChangedRules.removed = %s' % removed
			users = ChangedUsers()
			rules = ChangedRules()
			try:
				model = form.save(True)
				if users.added:
					User.objects.filter(pk__in=users.added).update(group=object_id)
				if users.removed:
					User.objects.filter(pk__in=users.removed).update(group=1L)
				if rules.added:
					for rule_id in rules.added:
						GroupRule(group_id=object_id, rule_id=rule_id).save()
				if rules.removed:
					GroupRule.objects.filter(rule__in=rules.removed).delete()
				flash_success(request,
					_('The group \'%s\' was changed successfully.') % model.groupname)
				if users.removed and object_id == 1L:
					flash_warning(request, _('However, the users weren\'t removed'
						' because they must belong to one group at least.'))
			except IntegrityError:
				flash_error(request,
					_('The group \'%s\' already exists.') % form.cleaned_data['groupname'].strip())
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.EDIT, object_id)
		if redir != None: return redir
	available_users = User.objects.exclude(group__id=object_id) \
		.order_by('group', 'username')
	# With sub-query:
	#	SELECT r.*
	#	FROM rules as r
	#	WHERE r.id NOT IN (
	#		SELECT gr.rule_id
	#		FROM grouprules as gr
	#		WHERE gr.group_id = 1
	#	)
	# Without sub-query:
	#	SELECT r.*
	#	FROM rules as r
	#	LEFT OUTER JOIN grouprules as gr ON gr.rule_id = r.id AND gr.group_id = 1
	#	WHERE gr.group_id IS NULL
	available_rules = Rule.objects.extra(where=['''
		rules.id NOT IN (
			SELECT rule_id FROM grouprules WHERE group_id = %d
		)
		''' % object_id]).order_by('id')
	context_instance = RequestContext(request)
	template_name = 'groups/edit.html'
	extra_context = {
		'menu': 'groups',
		'form': form,
		'model':  model,
		'can_delete': can_delete,
		'available_users': available_users,
		'available_rules': available_rules
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.add_usergroup')
def add(request):
	object_id = None
	if request.method == method.GET:
		form = GroupForm()
	elif request.method == method.POST:
		form = GroupForm(request.POST)
		if form.is_valid():
			users_added = map(long, request.POST.getlist('users'))
			rules_added = map(long, request.POST.getlist('rules'))
			try:
				model = form.save(True)
				object_id = model.id
				if users_added:
					User.objects.filter(pk__in=users_added).update(group=object_id)
				if rules_added:
					for rule_id in rules_added:
						GroupRule(group_id=object_id, rule_id=rule_id).save()
				flash_success(request,
					_('The group \'%s\' was created successfully.') % model.groupname)
				form = GroupForm()
			except IntegrityError:
				flash_error(request,
					_('The group \'%s\' already exists.') % form.cleaned_data['groupname'].strip())
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.ADD, object_id)
		if redir != None: return redir
	available_users = User.objects.all().order_by('group', 'username')
	available_rules = Rule.objects.all().order_by('id')
	context_instance = RequestContext(request)
	template_name = 'groups/add.html'
	extra_context = {
		'menu': 'groups',
		'form': form,
		'available_users': available_users,
		'available_rules': available_rules
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.delete_usergroup')
def delete(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(UserGroup, pk=object_id)
	if model.isbuiltin:
		message = _('Can\'t delete built-in groups.')
		if request.method == method.POST:
			return HttpResponseForbidden(message)
		else:
			flash_error(request, message)
			return HttpResponseRedirect(reverse('webui:groups-edit', args=[object_id]))
	# Move users to GUEST (built-in) group
	User.objects.filter(group=object_id).update(group=1L)
	model.delete()
	if request.method == method.POST:
		return HttpResponse()
	else:
		return HttpResponseRedirect(reverse('webui:groups-index'))

@rest_post
@login_required
@permission_required('imdata.delete_usergroup')
def delete_many(request):
	selected = request.POST.getlist('selection')
	# Move users to GUEST (built-in) group
	User.objects.filter(group__in=selected).update(group=1L)
	UserGroup.objects.filter(Q(pk__in=selected) & Q(isbuiltin=False)).delete()
	return HttpResponse()
