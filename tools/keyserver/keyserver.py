#!/usr/bin/env python3
#
# Development stand-in for the livemgr KeyServer (the real one is part of the
# closed-source backend). It answers the webui's license queries:
#
#   POST /details  ->  {"max_users": N}
#
# Clients authenticate with their license certificate (mutual TLS): the
# handshake fails unless it is signed by the licensing CA and not expired, and
# N is read from the certificate's usersLimit extension.
#
# Usage: keyserver.py --cert keyserver.pem --ca-file ca.crt [--host H] [--port P]

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
import ssl

# DER encoding of the usersLimit OID (1.2.3.4.5.31.33.72)
OID_USERS_LIMIT = bytes.fromhex('06072a0304051f2148')

def der_length(data, pos):
	"""Returns (length, position of the contents) for the length at pos."""
	length = data[pos]
	if length < 0x80:
		return length, pos + 1
	count = length & 0x7f
	return int.from_bytes(data[pos + 1:pos + 1 + count], 'big'), pos + 1 + count

def users_limit(cert_der):
	"""Returns the usersLimit extension value of a DER certificate, or None."""
	pos = cert_der.find(OID_USERS_LIMIT)
	if pos == -1:
		return None
	pos += len(OID_USERS_LIMIT)
	if cert_der[pos] == 0x01: # Optional critical flag
		pos += 3
	if cert_der[pos] != 0x04: # extnValue OCTET STRING
		return None
	_, pos = der_length(cert_der, pos + 1)
	if cert_der[pos] != 0x16: # IA5String, since the extension is aliased to nsComment
		return None
	length, pos = der_length(cert_der, pos + 1)
	return int(cert_der[pos:pos + length].decode('ascii'))

class Handler(BaseHTTPRequestHandler):
	def do_POST(self):
		self.rfile.read(int(self.headers.get('Content-Length') or 0))
		if self.path != '/details':
			self.send_error(404)
			return
		max_users = users_limit(self.connection.getpeercert(binary_form=True))
		if max_users is None:
			self.send_error(403, 'License has no usersLimit')
			return
		body = json.dumps({'max_users': max_users}).encode('utf-8')
		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self.send_header('Content-Length', str(len(body)))
		self.end_headers()
		self.wfile.write(body)

def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--cert', required=True, help='Server certificate + private key (PEM)')
	parser.add_argument('--ca-file', required=True, help='Licensing CA certificate (PEM)')
	parser.add_argument('--host', default='0.0.0.0')
	parser.add_argument('--port', type=int, default=443)
	args = parser.parse_args()

	context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	context.load_cert_chain(args.cert)
	context.load_verify_locations(args.ca_file)
	context.verify_mode = ssl.CERT_REQUIRED

	server = ThreadingHTTPServer((args.host, args.port), Handler)
	server.socket = context.wrap_socket(server.socket, server_side=True)
	print('KeyServer listening on %s:%d' % (args.host, args.port), flush=True)
	server.serve_forever()

if __name__ == '__main__':
	main()
