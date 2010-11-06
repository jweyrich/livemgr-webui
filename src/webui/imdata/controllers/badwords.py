from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common import CustomPaginator
from webui.common.decorators.rest import rest_multiple, rest_post
from webui.common.http import method
from webui.common.utils import request_has_error, InView, FormAction, flash_success, flash_info, \
	flash_form_error, flash_error
from webui.imdata.models import Badword
from webui.imdata.models.profile import Profile
from webui.imdata.utils.formatters import format_boolean
import django_tables as tables
import re

class BadwordTable(tables.ModelTable):
	class Meta:
		model = Badword
		exclude = []
		columns = ['badword', 'isregex', 'isenabled']
	id = tables.Column(visible=False)
	def render_isregex(self, instance):
		return format_boolean(instance.isregex)
	def render_isenabled(self, instance):
		return format_boolean(instance.isenabled)

class BadwordForm(ModelForm):
	class Meta:
		model = Badword
		fields = ('badword', 'isregex', 'isenabled')
	def clean(self):
		cleaned_data = self.cleaned_data
		cleaned_data['badword'] = cleaned_data['badword'].strip().lower()
		if cleaned_data['isregex']:
			try:
				re.compile(cleaned_data['badword'], re.IGNORECASE)
			except:
				msg = _('Invalid regular expression')
				self._errors['badword'] = self.error_class([msg])
				del cleaned_data['badword']
		return cleaned_data

class BadwordSearchForm(forms.Form):
	badword = forms.CharField(required=False, label=ugettext_lazy("badword"))

def _redirect_if_needed(request, action, object_id=None):
	if not request_has_error(request):
		if request.POST.get(FormAction.SAVE_AND_LIST):
			return HttpResponseRedirect(reverse('webui:badwords-index'))
		elif request.POST.get(FormAction.SAVE_AND_ADD):
			flash_info(request, _('You may add another.'))
			if action != InView.ADD:
				return HttpResponseRedirect(reverse('webui:badwords-add'))
		elif request.POST.get(FormAction.SAVE_AND_EDIT):
			if action != InView.EDIT:
				return HttpResponseRedirect(reverse('webui:badwords-edit', args=[object_id]))
	return None

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.see_badword')
def index(request):
	if request.method == method.GET:
		qset = Badword.objects.all()
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_badwords=per_page)
			return HttpResponse()
		form = BadwordSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		qset = Badword.objects.all()
		if values['badword']:
			qset = qset.filter(badword__icontains=values['badword'])
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', 'badword')
	table = BadwordTable(qset, order_by=order_by)
	paginator = CustomPaginator(request, table.rows, profile.per_page_badwords)
	context_instance = RequestContext(request)
	template_name = 'badwords/list.html'
	extra_context = {
		'menu': 'badwords',
		'table': table,
		'paginator': paginator,
		'search_form': BadwordSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.change_badword')
def edit(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(Badword, pk=object_id)
	if request.method == method.GET:
		form = BadwordForm(instance=model)
	elif request.method == method.POST:
		object_id = None
		form = BadwordForm(request.POST, instance=model)
		if form.is_valid():
			try:
				model = form.save(True)
				object_id = model.id
				flash_success(request,
					_('The badword \'%s\' was changed successfully.') % model.badword)
			except IntegrityError:
				flash_error(request,
					_('The badword \'%s\' already exists.') % form.cleaned_data['badword'].strip().lower())
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.EDIT, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'badwords/edit.html'
	extra_context = {
		'menu': 'badwords',
		'form': form,
		'model':  model,
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.add_badword')
def add(request):
	if request.method == method.GET:
		form = BadwordForm()
	elif request.method == method.POST:
		object_id = None
		form = BadwordForm(request.POST)
		if form.is_valid():
			try:
				model = form.save(True)
				object_id = model.id
				flash_success(request,
					_('The badword \'%s\' was created successfully.') % model.badword)
				form = BadwordForm()
			except IntegrityError:
				flash_error(request,
					_('The badword \'%s\' already exists.') % form.cleaned_data['badword'].strip().lower())
		else:
			flash_form_error(request, form)
		redir = _redirect_if_needed(request, InView.ADD, object_id)
		if redir != None: return redir
	context_instance = RequestContext(request)
	template_name = 'badwords/add.html'
	extra_context = { 'menu': 'badwords', 'form': form }
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.delete_badword')
def delete(request, object_id):
	object_id = long(object_id)
	model = get_object_or_404(Badword, pk=object_id)
	model.delete()
	if request.method == method.POST:
		return HttpResponse()
	else:
		return HttpResponseRedirect(reverse('webui:badwords-index'))

@rest_post
@login_required
@permission_required('imdata.delete_badword')
def delete_many(request):
	selected = request.POST.getlist('selection')
	Badword.objects.filter(pk__in=selected).delete()
	return HttpResponse()

@rest_post
@login_required
@permission_required('imdata.change_badword')
def disable_many(request):
	selected = request.POST.getlist('selection')
	Badword.objects.filter(pk__in=selected).update(isenabled=False)
	return HttpResponse()

@rest_post
@login_required
@permission_required('imdata.change_badword')
def enable_many(request):
	selected = request.POST.getlist('selection')
	Badword.objects.filter(pk__in=selected).update(isenabled=True)
	return HttpResponse()
