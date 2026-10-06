# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Jardel Weyrich
#
# This file is part of livemgr-webui.
#
# livemgr-webui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# livemgr-webui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jardel Weyrich <jweyrich@gmail.com>

from __future__ import print_function
from M2Crypto import X509
from M2Crypto.ASN1 import UTC
from M2Crypto.X509 import X509Error
from datetime import datetime
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.utils.six.moves import http_client
from django.utils.six.moves.urllib.parse import urlencode
from django.utils.translation import ugettext as _, ugettext_lazy
from webui.common.decorators.rest import rest_get
from webui.common.utils import flash_error
import errno
import json
import os
import socket
import ssl
import stat
import sys

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
		print('Exception:', sys.exc_info()[0])
		return False

def fetch_license_details(cert_path):
	try:
		if settings.KEYSERVER_USE_SSL:
			# Python 3.6 deprecates key_file and cert_file, and 3.12 removes
			# them: load the client certificate into the context they built.
			context = ssl.create_default_context()
			context.load_cert_chain(cert_path)
			conn = http_client.HTTPSConnection(
				settings.KEYSERVER_HOST,
				settings.KEYSERVER_PORT,
				context=context,
				timeout=settings.KEYSERVER_TIMEOUT)
		else:
			conn = http_client.HTTPConnection(
				settings.KEYSERVER_HOST,
				settings.KEYSERVER_PORT,
				timeout=settings.KEYSERVER_TIMEOUT)
		params = urlencode({'version': '1.0'})
		conn.request("POST", '/details', params)
		response = conn.getresponse()
		data = response.read()
		conn.close()
		if response.status != 200:
			raise Exception(_("Server returned %(status)i %(reason)s") %
				{'status': response.status, 'reason': response.reason})
		# json.loads() accepts bytes only from Python 3.6 on
		return LicenseDetails.from_json(data.decode('utf-8'))
	except socket.error as ex:
		print('Exception:', ex)
		#print os.strerror(ex.errno)
		if ex.errno in [
			errno.ECONNREFUSED, errno.ECONNRESET, errno.ETIMEDOUT,
			errno.EHOSTDOWN, errno.EHOSTUNREACH, errno.ENETUNREACH] \
			or str(ex) == 'timed out':
			raise ConnectionProblem
		else:
			raise InvalidLicense
	except:
		raise Exception('Unexpected exception: %s' % sys.exc_info()[0])

@rest_get
@login_required
@permission_required('livemgr.see_license')
def index(request):
	license = None
	try:
		cert_path = settings.LICENSE_FILE
		cert = X509.load_cert(cert_path, X509.FORMAT_PEM)
		# Get details from KeyServer
		license_details = fetch_license_details(cert_path)
		now = datetime.now(UTC)
		class LicensePresenter:
			#issuer = cert.get_issuer()
			#fingerprint = cert.get_fingerprint()
			#issued_by = issuer.CN
			valid_since = cert.get_not_before().get_datetime()
			valid_until = cert.get_not_after().get_datetime()
			serial = '%X' % cert.get_serial_number()
			subject = cert.get_subject()
			licensee = subject.O
			max_users = license_details.max_users
			status = _('Valid') if now >= valid_since \
				and now <= valid_until else _('Expired')
		license = LicensePresenter()
	except IOError:
		flash_error(request, _('Please, place your license file in %s.') % cert_path)
	except (InvalidLicense, ValueError, X509Error):
		print("Exception:", sys.exc_info()[0])
		flash_error(request, _('Please, inform a valid license.'))
	except ConnectionProblem:
		flash_error(request, _('Connection problem. Try again in few minutes.'))
	template_name = 'license/index.html'
	extra_context = {
		'menu': 'license',
		'license': license,
	}
	return render(request, template_name, extra_context)
