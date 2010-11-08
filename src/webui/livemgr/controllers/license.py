from M2Crypto import X509
from M2Crypto.ASN1 import UTC
from M2Crypto.X509 import X509Error
from datetime import datetime
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from webui import settings
from webui.common.decorators.rest import rest_multiple, rest_get
from webui.common.http import method
from webui.common.utils import flash_success, flash_form_error, flash_error
import errno
import httplib
import json
import os
import socket
import stat
import sys
import urllib

class InvalidLicense(Exception):
	pass

class ConnectionProblem(Exception):
	pass

class LicenseFileForm(forms.Form):
	file = forms.FileField(required=True, label=ugettext_lazy("License"))

class LicenseDetails:
	def __init__(self, **entries):
		self.__dict__.update(entries)
	@classmethod
	def from_json(self, data):
		#print 'LicenseDetails: ' + data
		dict = json.loads(data)
		return LicenseDetails(**dict)

def save_uploaded_license(path, uploaded_file):
	try:
		file = open(path, 'wb+')
		for chunk in uploaded_file.chunks():
			file.write(chunk)
		file.close()
		os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
		return True
	except: # IOError:
		print 'Exception:', sys.exc_info()[0]
		return False

def fetch_license_details(cert_path):
	try:
		if settings.PROJECT_KEYSERVER_SSL:
			conn = httplib.HTTPSConnection(
				settings.PROJECT_KEYSERVER_HOST,
				settings.PROJECT_KEYSERVER_PORT,
				cert_path, cert_path,
				timeout=settings.PROJECT_KEYSERVER_TIMEOUT)
		else:
			conn = httplib.HTTPConnection(
				settings.PROJECT_KEYSERVER_HOST,
				settings.PROJECT_KEYSERVER_PORT,
				timeout=settings.PROJECT_KEYSERVER_TIMEOUT)
		params = urllib.urlencode({'version': '1.0'})
		conn.request("POST", settings.PROJECT_KEYSERVER_URI, params)
		response = conn.getresponse()
		data = response.read()
		conn.close()
		if response.status != 200:
			raise Exception, _("Server returned %(status)i %(reason)s") % \
				{'status': response.status, 'reason': response.reason}
		return LicenseDetails.from_json(data)
	except socket.error as ex:
		print 'Exception:', ex
		#print os.strerror(ex.errno)
		if ex.errno in [
			errno.ECONNREFUSED, errno.ECONNRESET, errno.ETIMEDOUT,
			errno.EHOSTDOWN, errno.EHOSTUNREACH, errno.ENETUNREACH] \
			or str(ex) == 'timed out':
			raise ConnectionProblem
		else:
			raise InvalidLicense
	except:
		raise Exception, 'Unexpected exception:', sys.exc_info()[0]

@rest_get
@login_required
@permission_required('livemgr.see_license')
def index(request):
	license = None
	try:
		cert_path = settings.PROJECT_KEYSERVER_CERT_FILE
		# Get details from KeyServer
		license_details = fetch_license_details(cert_path)
		now = datetime.now(UTC)
		cert = X509.load_cert(cert_path, X509.FORMAT_PEM)
		class LicensePresenter:
			#issuer = cert.get_issuer()
			#fingerprint = cert.get_fingerprint()
			#issued_by = issuer.CN
			valid_since = cert.get_not_before().get_datetime()
			valid_until = cert.get_not_after().get_datetime()
			serial = hex(cert.get_serial_number())[2:-1].upper()
			subject = cert.get_subject()
			licensee = subject.O
			max_users = license_details.max_users
			status = _('Valid') if now >= valid_since \
				and now <= valid_until else _('Expired')
		license = LicensePresenter()
	except (ValueError, X509Error):
		print "Exception:", sys.exc_info()[0]
		flash_error(request, _('Please, inform a valid license.'))
		return HttpResponseRedirect(reverse('webui:license-edit'))
	except InvalidLicense:
		flash_error(request, _('Please, inform a valid license.'))
		return HttpResponseRedirect(reverse('webui:license-edit'))
	except ConnectionProblem:
		flash_error(request, _('Connection problem. Try again in few minutes.'))
	context_instance = RequestContext(request)
	template_name = 'license/index.html'
	extra_context = {
		'menu': 'license',
		'license': license,
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.change_license')
def edit(request):
	if request.method == method.GET:
		form = LicenseFileForm()
	elif request.method == method.POST:
		form = LicenseFileForm(request.POST, request.FILES)
		while True: # Shame on me :-)
			if not form.is_valid():
				flash_form_error(request, form)
				break
			uploaded_file = form.cleaned_data['file']
			cert_path = settings.PROJECT_KEYSERVER_CERT_FILE
			# Save certificate file
			if not save_uploaded_license(cert_path, uploaded_file):
				flash_error(request, _('Unable to save the uploaded file. '
					'Please, report this to your administrator.'))
				break
			# Validate locally
			try:
				X509.load_cert(cert_path, X509.FORMAT_PEM)
			except (ValueError, X509Error):
				print 'Exception:', sys.exc_info()[0]
				flash_error(request, _('Please, inform a valid license.'))
				break
			# Validate on KeyServer
			try:
				license = fetch_license_details(cert_path)
			except InvalidLicense:
				flash_error(request, _('Please, inform a valid license.'))
				break
			except ConnectionProblem:
				flash_error(request, _('Connection problem. Try again in few minutes.'))
				break
			flash_success(request, _('The license was changed successfully.'))
			return HttpResponseRedirect(reverse('livemgr:license-index'))
	context_instance = RequestContext(request)
	template_name = 'license/edit.html'
	extra_context = {
		'menu': 'license',
		'form': form,
	}
	return render_to_response(template_name, extra_context, context_instance)
