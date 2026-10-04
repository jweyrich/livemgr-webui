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

from M2Crypto import ASN1, EVP, RSA, X509
from datetime import datetime
from django.conf import settings
from webui.livemgr.controllers import license
from webui.livemgr.controllers.license import ConnectionProblem, LicenseDetails
from webui.livemgr.tests.base import LivemgrTestCase
import os
import shutil
import socket
import tempfile

def write_certificate(path, not_before, not_after, organization='ACME Corp', serial=0x1A2B3C):
	"""
	Write a self-signed license bundle (certificate + private key): the key
	server connection uses the license file as its client certificate.
	"""
	rsa = RSA.gen_key(2048, 65537, lambda *args: None)
	key = EVP.PKey()
	key.assign_rsa(rsa)
	name = X509.X509_Name()
	name.O = organization
	name.CN = 'livemgr'
	cert = X509.X509()
	cert.set_version(2)
	cert.set_serial_number(serial)
	cert.set_subject(name)
	cert.set_issuer(name)
	cert.set_pubkey(key)
	for setter, value in [(cert.set_not_before, not_before), (cert.set_not_after, not_after)]:
		time = ASN1.ASN1_TIME()
		time.set_datetime(value.replace(tzinfo=ASN1.UTC))
		setter(time)
	cert.sign(key, 'sha256')
	bundle = open(path, 'w')
	bundle.write(cert.as_pem())
	bundle.write(key.as_pem(cipher=None))
	bundle.close()

def closed_port():
	sock = socket.socket()
	sock.bind(('127.0.0.1', 0))
	port = sock.getsockname()[1]
	sock.close()
	return port

class LicenseTest(LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.tmpdir = tempfile.mkdtemp()
		self.cert_path = os.path.join(self.tmpdir, 'cert.pem')
		self.saved_settings = (settings.LICENSE_FILE, settings.KEYSERVER_PORT)
		self.saved_fetch = license.fetch_license_details
		settings.LICENSE_FILE = self.cert_path

	def tearDown(self):
		settings.LICENSE_FILE, settings.KEYSERVER_PORT = self.saved_settings
		license.fetch_license_details = self.saved_fetch
		shutil.rmtree(self.tmpdir)

	def fake_keyserver(self, **details):
		calls = []
		def fetch(cert_path):
			calls.append(cert_path)
			return LicenseDetails(**details)
		license.fetch_license_details = fetch
		return calls

	def test_valid_license(self):
		write_certificate(self.cert_path, datetime(2010, 1, 1), datetime(2100, 1, 1))
		calls = self.fake_keyserver(max_users=50)
		response = self.client.get('/license/')
		self.assertEqual(calls, [self.cert_path])
		presenter = response.context['license']
		self.assertEqual(presenter.licensee, 'ACME Corp')
		self.assertEqual(presenter.serial, '1A2B3C')
		self.assertEqual(presenter.max_users, 50)
		self.assertEqual(presenter.status, 'Valid')
		self.assertEqual(presenter.valid_since.date(), datetime(2010, 1, 1).date())
		self.assertEqual(presenter.valid_until.date(), datetime(2100, 1, 1).date())
		self.assertContains(response, 'ACME Corp')
		self.assertContains(response, '1A2B3C')

	def test_expired_license(self):
		write_certificate(self.cert_path, datetime(2010, 1, 1), datetime(2011, 1, 1))
		self.fake_keyserver(max_users=50)
		self.assertEqual(self.client.get('/license/').context['license'].status, 'Expired')

	def test_missing_license_file(self):
		# M2Crypto raises BIOError (a ValueError), not IOError, so the
		# "place your license file" message is never shown.
		response = self.client.get('/license/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['license'], None)
		self.assertFlash(response, 'Please, inform a valid license.')

	def test_corrupt_license_file(self):
		open(self.cert_path, 'w').write('not a certificate')
		response = self.client.get('/license/')
		self.assertEqual(response.context['license'], None)
		self.assertFlash(response, 'Please, inform a valid license.')

	def test_keyserver_unreachable(self):
		write_certificate(self.cert_path, datetime(2010, 1, 1), datetime(2100, 1, 1))
		settings.KEYSERVER_PORT = closed_port()
		self.assertRaises(ConnectionProblem, license.fetch_license_details, self.cert_path)
		response = self.client.get('/license/')
		self.assertEqual(response.context['license'], None)
		self.assertFlash(response, 'Connection problem. Try again in few minutes.')

class LicenseDetailsTest(LivemgrTestCase):
	def test_from_json(self):
		details = LicenseDetails.from_json('{"max_users": 50, "product": "livemgr"}')
		self.assertEqual((details.max_users, details.product), (50, 'livemgr'))
