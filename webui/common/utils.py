from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

#__all__ = (
#	'get_order', 'get_order_raw',
#	'clear_queries', 'dump_queries',
#	'flash_debug', 'flash_info', 'flash_success',
#	'flash_warning', 'flash_error', 'request_has_error',
#	'InView', 'FormAction'
#)

def get_order(request, default_field):
	#from django.template import RequestContext
	return request.GET.get('sort', default_field)

def get_order_raw(request, default_field):
	order_by = get_order(request, default_field)
	if order_by.startswith('-'):
		return order_by[1:] + ' DESC'
	else:
		return order_by

def clear_queries():
	from django.db import connection
	connection.queries = []
#def dump_queries():
#	from django.db import connection
#	for q in connection.queries:
#		print q['sql']
#	pass

def flash_debug(request, msg):
	messages.debug(request, msg)
def flash_info(request, msg):
	messages.info(request, msg)
def flash_success(request, msg):
	messages.success(request, msg)
def flash_warning(request, msg):
	messages.warning(request, msg)
def flash_error(request, msg):
	if not hasattr(request, '_errors'):
		request._errors = 0
	request._errors += 1
	messages.error(request, msg)
def flash_form_error(request, form):
	if '__all__' in form.errors and len(form.errors['__all__']) > 0:
		flash_error(request, form.errors['__all__'].pop())
	else:
		flash_error(request, _('Please, correct the fields below.'))

def request_has_error(request):
	if not hasattr(request, '_errors'):
		return False
	return request._errors > 0

class InView:
	EDIT	 = 0
	ADD		 = 1

class FormAction:
	SAVE_AND_ADD	 = '_save_add'
	SAVE_AND_EDIT	 = '_save_edit'
	SAVE_AND_LIST	 = '_save_list'
