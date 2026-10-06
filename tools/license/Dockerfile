# Issues livemgr license certificates using sslpkix.
#
# Build (from this directory):
#   docker build -t livemgr-license .
#
# Run (files are read from and written to the mounted /work directory, and
# --user keeps them owned by you instead of root):
#   # Create a new licensing CA and issue a license
#   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" livemgr-license \
#       --new-ca . --org "ACME Corp" --users 50 --out cert.pem
#   # Issue a license with an existing CA
#   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" livemgr-license \
#       --ca-cert ca.crt --ca-key ca.key --org "ACME Corp" --users 50 --out cert.pem
#
# Run without arguments to list all options.

FROM debian:bookworm AS build

RUN apt-get -qq update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
		g++ \
		libssl-dev \
	&& rm -rf /var/lib/apt/lists/*

# sslpkix is pinned to a commit, so rebuilding the image gives the same tool
ARG SSLPKIX_REF=f8ad26de43a7c6125da586da050660fd0b690bcd

WORKDIR /src
RUN curl -fsSL https://github.com/jweyrich/sslpkix/archive/${SSLPKIX_REF}.tar.gz \
		| tar -xz --strip-components=1 -C /src \
	# exception.h calls get_error_string() without its sslpkix::error namespace
	&& sed -i 's/reason = get_error_string()/reason = error::get_error_string()/' \
		include/sslpkix/exception.h

COPY livemgr_license.cpp /src/tools/
# Compile the library sources straight into the tool: the CMake build also
# fetches Catch2 for the tests, which isn't needed here.
RUN g++ -std=c++20 -O2 -Iinclude \
		tools/livemgr_license.cpp $(find src -name '*.cpp' -o -name '*.c') \
		-lssl -lcrypto -o /usr/local/bin/livemgr-license

###

FROM debian:bookworm-slim
LABEL maintainer="jweyrich@gmail.com"

RUN apt-get -qq update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		libssl3 \
	&& rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bin/livemgr-license /usr/local/bin/livemgr-license

WORKDIR /work
ENTRYPOINT ["livemgr-license"]
