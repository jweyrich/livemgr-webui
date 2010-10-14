from M2Crypto import X509, m2
from M2Crypto.ASN1 import UTC
from M2Crypto.X509 import X509Error
from StringIO import StringIO
from datetime import datetime
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from hashlib import sha1
from webui import settings
from webui.common.decorators.rest import rest_multiple, rest_get
from webui.common.http import method
from webui.common.utils import flash_success, flash_form_error, flash_error
from webui.imdata.models.license import License
import os
import sys

OID_clientToken = '1.2.3.4.5.31.33.71'
SN_clientToken = 'clientTokenIdentifier'
LN_clientToken = 'Client Token Identifier'

OID_usersLimit = '1.2.3.4.5.31.33.72'
SN_usersLimit = 'usersLimit'
LN_usersLimit = 'Users Limit'

def add_custom_extension(oid, sn, ln):
	nid = X509.create_extension(oid, sn, ln)
	if nid <> 0: X509.alias_extension(nid, m2.NID_netscape_comment)

add_custom_extension(OID_clientToken, SN_clientToken, LN_clientToken)
add_custom_extension(OID_usersLimit, SN_usersLimit, LN_usersLimit)

class LicenseFileForm(forms.Form):
	file = forms.FileField(required=True, label=ugettext_lazy("Certificate"))

class LicenseValidator:
	def __init__(self, buffer):
		try:
			self._client_crt = X509.load_cert_string(buffer, X509.FORMAT_PEM)
			self._client_crt.save(self.get_filepath('license.crt'), X509.FORMAT_PEM)
			# get_fingerprint() get_subject()
			self._ca_crt = X509.load_cert(self.get_filepath('cacert.crt'), X509.FORMAT_PEM)
		except:
			file = open(self.get_filepath('license.crt'), 'w')
			file.truncate()
			file.close()
	def is_valid(self):
		try:
			result = True
			result = result and self._client_crt.get_ext(SN_clientToken)
			result = result and self._client_crt.get_ext(SN_usersLimit)
			result = result and self._client_crt.verify(self._ca_crt.get_pubkey())
			return result
		except: #LookupError:
			return False
#		result = False
#		pipe = os.popen('openssl verify -CAfile '+
#			self.get_filepath('cacert.crt')+' '+
#			self.get_filepath('license.crt'), 'r')
#		for line in pipe.readlines():
#			if line.endswith(': OK\n'):
#				result = True
#				break
#		pipe.close()
#		return result
	def get_filepath(self, filename):
		return os.path.join(settings.PROJECT_PATH, 'conf/certs/'+filename)
	def client_cert(self):
		return self._client_crt
	def ca_cert(self):
		return self._ca_cert

@rest_get
@login_required
@permission_required('imdata.see_license')
def index(request):
	cert = None
	try:
		license = License.objects.all().order_by('-id')[0]
		buffer = license.certificate.encode('latin-1')
		cert = X509.load_cert_string(buffer, X509.FORMAT_PEM)
		now = datetime.now(UTC)
		class CertPresenter:
			issuer = cert.get_issuer()
			fingerprint = cert.get_fingerprint()
			issued_by = issuer.CN
			valid_since = cert.get_not_before().get_datetime()
			valid_until = cert.get_not_after().get_datetime()
			serial = cert.get_serial_number()
			subject = cert.get_subject()
			subject_c = subject.C
			subject_st = subject.ST
			subject_l = subject.L
			subject_o = subject.O
			subject_cn = subject.CN
			users = cert.get_ext(SN_usersLimit).get_value()
			status = _('Valid') if now >= valid_since \
				and now <= valid_until else _('Expired')
		cert = CertPresenter()
	except IndexError:
		return HttpResponseRedirect(reverse('webui:license-edit'))
	except (ValueError, X509Error):
		print "Unexpected error:", sys.exc_info()[0]
		pass
	context_instance = RequestContext(request)
	template_name = 'license/index.html'
	extra_context = {
		'menu': 'license',
		'cert': cert,
	}
	return render_to_response(template_name, extra_context, context_instance)


@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.change_license')
def edit(request):
	if request.method == method.GET:
		form = LicenseFileForm()
	elif request.method == method.POST:
		form = LicenseFileForm(request.POST, request.FILES)
		if form.is_valid():
			file = form.cleaned_data['file']
			buffer = StringIO()
			while True:
				block = file.read(512)
				if not block:
					break
				buffer.write(block)
			license = License()
			license.certificate = buffer.getvalue()
			validator = LicenseValidator(license.certificate)
			if validator.is_valid():
				hash = sha1(license.certificate)
				license.hash = hash.hexdigest()
				try:
					license.save()
					License.objects.exclude(id = license.id).delete()
					flash_success(request, _('The license was changed successfully.'))
					return HttpResponseRedirect(reverse('imdata:license-index'))
				except IntegrityError:
					flash_error(request, _("The informed certificate is already in use."))
			else:
				flash_error(request, _("Please, inform a valid certificate."))
			buffer.close()
			file.close()
		else:
			flash_form_error(request, form)
	context_instance = RequestContext(request)
	template_name = 'license/edit.html'
	extra_context = {
		'menu': 'license',
		'form': form,
	}
	return render_to_response(template_name, extra_context, context_instance)
