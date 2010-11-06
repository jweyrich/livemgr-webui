from django.shortcuts import render_to_response
from django.template import RequestContext
from webui import settings

def error_500(request):
	template = '500.html'
	data = {
		'EMAIL_SUPPORT': settings.EMAIL_SUPPORT
	}
	return render_to_response(template, data,
		context_instance=RequestContext(request))
