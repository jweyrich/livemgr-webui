// livemgr-license: issue a livemgr license certificate using sslpkix.
//
// The license is an X.509 client certificate signed by the licensing CA,
// carrying two custom extensions (aliased to nsComment, i.e. IA5String):
//   clientTokenIdentifier  1.2.3.4.5.31.33.71
//   usersLimit             1.2.3.4.5.31.33.72
// The output bundle (certificate + unencrypted private key) is what
// livemgr-webui expects in settings.LICENSE_FILE, since it is also used as
// the client certificate for the KeyServer connection.

#include "sslpkix/sslpkix.h"
#include "sslpkix/iosink.h"
#include "sslpkix/x509/cert.h"
#include "sslpkix/x509/cert_name.h"
#include "sslpkix/x509/digest.h"
#include "sslpkix/x509/key.h"
// Newer sslpkix moved the key factory out of key.h
#if __has_include("sslpkix/x509/key_factory.h")
#  include "sslpkix/x509/key_factory.h"
#endif

#include <openssl/bn.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/x509v3.h>

#include <sys/stat.h>

#include <cstdio>
#include <cstring>
#include <iostream>
#include <map>
#include <memory>
#include <string>

using namespace sslpkix;

static const char * const OID_clientToken = "1.2.3.4.5.31.33.71";
static const char * const SN_clientToken = "clientTokenIdentifier";
static const char * const LN_clientToken = "Client Token Identifier";

static const char * const OID_usersLimit = "1.2.3.4.5.31.33.72";
static const char * const SN_usersLimit = "usersLimit";
static const char * const LN_usersLimit = "Users Limit";

static void usage(const char *prog) {
	std::cerr <<
		"Usage: " << prog << " --org NAME --users N [options]\n"
		"       " << prog << " --server-name HOST [options]\n"
		"  --org NAME          Licensee organization (subject O, shown as Licensee)\n"
		"  --users N           usersLimit extension value\n"
		"  --cn NAME           Subject CN (default: livemgr)\n"
		"  --country CC        Subject C (optional)\n"
		"  --state ST          Subject ST (optional)\n"
		"  --locality L        Subject L (optional)\n"
		"  --email ADDR        Subject emailAddress (optional)\n"
		"  --token VALUE       clientTokenIdentifier value (default: random 40 hex chars)\n"
		"  --days N            Validity in days (default: 365)\n"
		"  --serial HEX        Serial number (default: random 64-bit)\n"
		"  --bits N            RSA key size (default: 2048)\n"
		"  --ca-cert FILE      Licensing CA certificate (PEM)\n"
		"  --ca-key FILE       Licensing CA private key (PEM)\n"
		"  --ca-pass PASS      Passphrase for --ca-key (if encrypted)\n"
		"  --new-ca DIR        Create a new licensing CA in DIR instead (ca.crt, ca.key)\n"
		"  --out FILE          Output bundle: certificate + private key (default: cert.pem)\n"
		"  --server-name HOST  Issue a KeyServer TLS certificate for HOST instead of a license\n";
}

static std::string random_hex(size_t bytes) {
	std::string buf(bytes, '\0');
	if (RAND_bytes(reinterpret_cast<unsigned char *>(&buf[0]), static_cast<int>(bytes)) != 1)
		throw std::runtime_error("RAND_bytes failed");
	static const char digits[] = "0123456789abcdef";
	std::string out;
	for (unsigned char c : buf) {
		out += digits[c >> 4];
		out += digits[c & 0xf];
	}
	return out;
}

static void set_serial_hex(Certificate &cert, const std::string &hex) {
	BIGNUM *bn = nullptr;
	if (!BN_hex2bn(&bn, hex.c_str()))
		throw std::runtime_error("Invalid serial: " + hex);
	ASN1_INTEGER *ok = BN_to_ASN1_INTEGER(bn, X509_get_serialNumber(cert.handle()));
	BN_free(bn);
	if (!ok)
		throw std::runtime_error("Failed to set serial");
}

// Add an extension whose config value may reference the issuer (e.g. authorityKeyIdentifier).
static void add_ext(Certificate &cert, X509 *issuer, int nid, const char *value) {
	X509V3_CTX ctx;
	X509V3_set_ctx_nodb(&ctx);
	X509V3_set_ctx(&ctx, issuer, cert.handle(), nullptr, nullptr, 0);
	X509_EXTENSION *ext = X509V3_EXT_conf_nid(nullptr, &ctx, nid, const_cast<char *>(value));
	if (!ext)
		throw std::runtime_error(std::string("Failed to create extension ") + OBJ_nid2sn(nid));
	std::unique_ptr<X509_EXTENSION, decltype(&X509_EXTENSION_free)> guard(ext, &X509_EXTENSION_free);
	cert.add_extension(ext);
}

static void write_file(const std::string &path, const Certificate *cert, const PrivateKey *key) {
	FileSink sink;
	sink.open(path, "w");
	// The private key is written unencrypted, so keep it private to the owner
	if (key && chmod(path.c_str(), S_IRUSR | S_IWUSR) != 0)
		throw std::runtime_error("Failed to restrict permissions of " + path);
	if (cert && !PEM_write_bio_X509(sink.handle(), const_cast<X509 *>(cert->handle())))
		throw std::runtime_error("Failed to write certificate to " + path);
	if (key)
		key->save(sink);
}

static void create_ca(const std::string &dir, std::unique_ptr<Certificate> &ca_cert, std::unique_ptr<PrivateKey> &ca_key) {
	ca_key = std::make_unique<PrivateKey>(factory::generate_key_rsa(4096), ResourceOwnership::Transfer);
	ca_cert = std::make_unique<Certificate>();
	CertificateName name;
	name.set_organization("livemgr");
	name.set_common_name("livemgr Licensing CA");
	ca_cert->set_version(Certificate::Version::v3);
	set_serial_hex(*ca_cert, random_hex(8));
	ca_cert->set_valid_since(0);
	ca_cert->set_valid_until(3650);
	ca_cert->set_subject(name);
	ca_cert->set_issuer(name);
	ca_cert->set_pubkey(*ca_key);
	add_ext(*ca_cert, ca_cert->handle(), NID_basic_constraints, "critical,CA:TRUE");
	add_ext(*ca_cert, ca_cert->handle(), NID_key_usage, "critical,keyCertSign,cRLSign");
	add_ext(*ca_cert, ca_cert->handle(), NID_subject_key_identifier, "hash");
	ca_cert->sign(*ca_key, Digest::TYPE_SHA256);
	write_file(dir + "/ca.crt", ca_cert.get(), nullptr);
	write_file(dir + "/ca.key", nullptr, ca_key.get());
	std::cerr << "Created licensing CA: " << dir << "/ca.crt, " << dir << "/ca.key\n";
}

int main(int argc, char *argv[]) {
	std::map<std::string, std::string> opt = {
		{"cn", "livemgr"}, {"days", "365"}, {"bits", "2048"}, {"out", "cert.pem"},
	};
	for (int i = 1; i < argc; i += 2) {
		if (std::strncmp(argv[i], "--", 2) != 0 || i + 1 >= argc) {
			usage(argv[0]);
			return 2;
		}
		opt[argv[i] + 2] = argv[i + 1];
	}
	const bool server = opt.count("server-name") > 0;
	if ((!server && (!opt.count("org") || !opt.count("users")))
		|| (opt.count("new-ca") == (opt.count("ca-cert") && opt.count("ca-key")))) {
		usage(argv[0]);
		return 2;
	}

	try {
		initialize();
		seed_prng();

		int nid_clientToken = add_custom_object(OID_clientToken, SN_clientToken, LN_clientToken);
		int nid_usersLimit = add_custom_object(OID_usersLimit, SN_usersLimit, LN_usersLimit);

		std::unique_ptr<Certificate> ca_cert;
		std::unique_ptr<PrivateKey> ca_key;
		if (opt.count("new-ca")) {
			create_ca(opt["new-ca"], ca_cert, ca_key);
		} else {
			FileSink cert_sink;
			cert_sink.open(opt["ca-cert"], "r");
			ca_cert = std::make_unique<Certificate>();
			ca_cert->load(cert_sink);
			FileSink key_sink;
			key_sink.open(opt["ca-key"], "r");
			ca_key = std::make_unique<PrivateKey>(key_sink, opt.count("ca-pass") ? opt["ca-pass"].c_str() : nullptr);
			if (X509_check_private_key(ca_cert->handle(), ca_key->handle()) != 1)
				throw std::runtime_error("CA key does not match CA certificate");
		}

		PrivateKey key(factory::generate_key_rsa(std::stoi(opt["bits"])), ResourceOwnership::Transfer);

		CertificateName subject;
		if (opt.count("country")) subject.set_country(opt["country"]);
		if (opt.count("state")) subject.set_state(opt["state"]);
		if (opt.count("locality")) subject.set_locality(opt["locality"]);
		if (opt.count("org")) subject.set_organization(opt["org"]);
		subject.set_common_name(server ? opt["server-name"] : opt["cn"]);
		if (opt.count("email")) subject.set_email(opt["email"]);

		Certificate cert;
		cert.set_version(Certificate::Version::v3);
		set_serial_hex(cert, opt.count("serial") ? opt["serial"] : random_hex(8));
		cert.set_valid_since(0);
		cert.set_valid_until(std::stoi(opt["days"]));
		cert.set_subject(subject);
		cert.set_issuer(ca_cert->subject());
		cert.set_pubkey(key);

		X509 *issuer = ca_cert->handle();
		add_ext(cert, issuer, NID_basic_constraints, "CA:FALSE");
		add_ext(cert, issuer, NID_key_usage, "digitalSignature,nonRepudiation,keyEncipherment");
		add_ext(cert, issuer, NID_ext_key_usage, server ? "serverAuth" : "clientAuth");
		add_ext(cert, issuer, NID_subject_key_identifier, "hash");
		add_ext(cert, issuer, NID_authority_key_identifier, "keyid,issuer");

		if (server) {
			const std::string san = "DNS:" + opt["server-name"];
			add_ext(cert, issuer, NID_subject_alt_name, san.c_str());
		} else {
			const std::string token = opt.count("token") ? opt["token"] : random_hex(20);
			cert.add_extension(nid_clientToken, token.c_str());
			cert.add_extension(nid_usersLimit, opt["users"].c_str());
		}

		cert.sign(*ca_key, Digest::TYPE_SHA256);

		write_file(opt["out"], &cert, &key);
		std::cerr << (server ? "Wrote KeyServer bundle: " : "Wrote license bundle: ") << opt["out"] << "\n";
	} catch (const std::exception &ex) {
		std::cerr << "Error: " << ex.what() << "\n";
		ERR_print_errors_fp(stderr);
		return 1;
	}
	return 0;
}
