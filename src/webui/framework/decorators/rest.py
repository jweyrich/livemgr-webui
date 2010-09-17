from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext as _
from webui.framework.http import method

def _clone_meta(target, source):
	pass
#	target.__name__ = source.__name__
#	target.__dict__ = source.__dict__
#	target.__doc__ = source.__doc__

def _rest_method(view, request, methods=[], *args, **kwargs):
	if not request.method in methods:
		return HttpResponseBadRequest(_('You don\'t have permission to access this.'))
	else:
		return view(request, *args, **kwargs)
	
def rest_multiple(methods=[]):
	"""
	Decorator to check whether a view accepts a HTTP method or not. If not, 
	returns a HttpResponseBadRequest response.
	"""
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return _rest_method(func, request, methods, *args, **kwargs)
		_clone_meta(view_decorator, func)
		return wrapper
	return view_decorator

def rest_get(function=None):
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return _rest_method(func, request, [method.GET], *args, **kwargs)
		_clone_meta(view_decorator, func)
		return wrapper
	return view_decorator(function)

def rest_post(function=None):
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return _rest_method(func, request, [method.POST], *args, **kwargs)
		_clone_meta(view_decorator, func)
		return wrapper
	return view_decorator(function)

def rest_put(function=None):
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return _rest_method(func, request, [method.PUT], *args, **kwargs)
		_clone_meta(view_decorator, func)
		return wrapper
	return view_decorator(function)

def rest_delete(function=None):
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return _rest_method(func, request, [method.DELETE], *args, **kwargs)
		_clone_meta(view_decorator, func)
		return wrapper
	return view_decorator(function)
