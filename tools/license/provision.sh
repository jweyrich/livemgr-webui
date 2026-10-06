#!/bin/sh
#
# Provisions the licensing CA and a license certificate for local use:
#   conf/license-ca/ca.crt, ca.key   Licensing CA (never mounted into the app)
#   conf/certs/cert.pem              License (certificate + private key), LICENSE_FILE
#   conf/certs/ca.crt                Copy of the CA certificate
#   conf/keyserver/keyserver.pem     Development KeyServer's TLS certificate + key
#   conf/keyserver/ca.crt            Copy of the CA certificate
# Existing files are kept, so it is safe to run again. Requires Docker.
#
# Usage: tools/license/provision.sh [--org NAME] [--users N] [--days N] [--renew]
#   --org NAME   Licensee organization (default: livemgr Development)
#   --users N    Users limit (default: 50)
#   --days N     License validity in days (default: 365)
#   --renew      Issue a new license even if one exists (the CA is kept)

set -e

ORG="livemgr Development"
USERS=50
DAYS=365
RENEW=0

while [ $# -gt 0 ]; do
	case "$1" in
		--org) ORG="$2"; shift 2 ;;
		--users) USERS="$2"; shift 2 ;;
		--days) DAYS="$2"; shift 2 ;;
		--renew) RENEW=1; shift ;;
		*) sed -n '/^# Usage/,/^$/s/^# \{0,1\}//p' "$0" >&2; exit 2 ;;
	esac
done

TOOL_DIR=$(cd "$(dirname "$0")" && pwd)
CONF_DIR=$(cd "$TOOL_DIR/../../conf" && pwd)
IMAGE=livemgr-license

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
	echo "Building the $IMAGE image..."
	docker build -q -t "$IMAGE" "$TOOL_DIR" >/dev/null
fi

# Runs the generator with conf/ as its working directory
run() {
	docker run --rm --user "$(id -u):$(id -g)" -v "$CONF_DIR:/work" "$IMAGE" "$@"
}

generate() {
	run --org "$ORG" --users "$USERS" --days "$DAYS" --out certs/cert.pem "$@"
}

mkdir -p "$CONF_DIR/license-ca" "$CONF_DIR/certs" "$CONF_DIR/keyserver"

if [ ! -f "$CONF_DIR/license-ca/ca.key" ]; then
	# A license signed by a previous CA would no longer verify, so issue a new one too
	generate --new-ca license-ca
	rm -f "$CONF_DIR/keyserver/keyserver.pem"
elif [ ! -f "$CONF_DIR/certs/cert.pem" ] || [ "$RENEW" = 1 ]; then
	generate --ca-cert license-ca/ca.crt --ca-key license-ca/ca.key
else
	echo "License already exists: conf/certs/cert.pem (use --renew to issue a new one)"
fi

# The development KeyServer (tools/keyserver) is reached by its Compose service name
if [ ! -f "$CONF_DIR/keyserver/keyserver.pem" ]; then
	run --server-name keyserver --days 3650 --out keyserver/keyserver.pem \
		--ca-cert license-ca/ca.crt --ca-key license-ca/ca.key
fi

cp "$CONF_DIR/license-ca/ca.crt" "$CONF_DIR/certs/ca.crt"
cp "$CONF_DIR/license-ca/ca.crt" "$CONF_DIR/keyserver/ca.crt"

openssl x509 -in "$CONF_DIR/certs/cert.pem" -noout -subject -serial -enddate 2>/dev/null || true
