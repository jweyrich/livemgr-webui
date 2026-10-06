[![Tests](https://github.com/jweyrich/livemgr-webui/actions/workflows/tests.yml/badge.svg)](https://github.com/jweyrich/livemgr-webui/actions/workflows/tests.yml)

## What is (was) it?

Live Manager was a complete corporate solution built to monitor and control all interactions over Microsoft MSN Messenger, which is now dead.

It allowed the administrator (the company) to define which users are allowed to use MSN in the coporate environment, which domains these users are allowed to exchange messages with, filter badwords, standardize status messages, allow or block any features supported by ALL versions of the MSN protocol, and so on.

The backend is still closed-source, but if you invite me for ☕  we can talk about it :-)

## What is included?

- ACLs: Restrict or allow a user or a group of users to talk to other specific users or domains.
- Users: Allow the admin to register users manually, and also support auto-registration so the administrator don't have to input all users manually. They register automatically during the first login on MSN.
- Groups: Group users to apply specific rules that permit or deny specific MSN functionalities like handwriting, file transfer, webcam, winks, voice clips, etc.
- Conversations: The history of all captured messages, shown in a very nice and usable user interface. It also supports exporting PDF reports for compliance.
- Badwords: Define which words are not welcome in conversations. The solution blocks any message being sent or received with these words, and warns the user that sent it.
- Settings: General configuration. See the attached screenshot.
- License: Since it was a commercial solution, the license depends on a digital certificate that controls how many concurrent users the solution is allowed to monitor.

## How to run?

```sh
tools/license/provision.sh
docker build . -t livemgr-webui:latest
docker-compose up
docker-compose run db "mysql -uroot --password=123456 < /mnt/initdb/create_schema.sql"
docker-compose run db "mysql -uroot --password=123456 < /mnt/initdb/create_tables.sql"
docker-compose run app /opt/envs/livemgr-webui/bin/python webui/manage.py migrate --noinput --settings=settings_example
````

## How to provision a license?

The License page reads `conf/certs/cert.pem`, an X.509 certificate signed by the licensing CA. Besides the licensee (subject O) and validity, it carries the `clientTokenIdentifier` (OID `1.2.3.4.5.31.33.71`) and `usersLimit` (OID `1.2.3.4.5.31.33.72`) extensions. The file also holds the certificate's private key, because the app uses it as the client certificate to reach the KeyServer.

To create a local licensing CA and license, run from the host (requires Docker):

```sh
tools/license/provision.sh [--org NAME] [--users N] [--days N] [--renew]
```

It writes the CA to `conf/license-ca/`, the license to `conf/certs/`, and the KeyServer's TLS certificate to `conf/keyserver/`. Existing files are kept, so it's safe to run again; pass `--renew` to issue a new license with the same CA. These directories are ignored by Git and by `docker build`, and `docker-compose.yml` mounts `conf/certs/` read-only into the app container. The devcontainer runs the script automatically before it starts. The generator itself is built with [sslpkix](https://github.com/jweyrich/sslpkix); see `tools/license/Dockerfile` for its other options.

The License page also asks the KeyServer, which is part of the closed-source backend, how many users the license allows. For development, both Compose setups run a stand-in (`tools/keyserver/keyserver.py`) as the `keyserver` service: it accepts only licenses signed by the licensing CA, and answers with the license's `usersLimit`. The app reaches it through the `LIVEMGR_KEYSERVER_HOST` and `LIVEMGR_KEYSERVER_CA_FILE` environment variables.

## How to develop?

Open the repository in VS Code and choose **Reopen in Container** (requires the Dev Containers extension and Docker). The database is created and seeded on first start, and the media files are built. Then, from the container's terminal:

```sh
python webui/manage.py runserver 0.0.0.0:8000 --settings=settings_example
```

## How to test?

From the devcontainer's terminal:

```sh
python webui/manage.py test --settings=settings_test
```

The test runner creates (and drops) a `test_livemgr` database on the `db` service and loads `bootstrap/db/create_tables.sql` into it, so the tests run against the same schema as production. To use another MySQL/MariaDB server, set `LIVEMGR_TEST_DB_HOST`, `LIVEMGR_TEST_DB_PORT`, `LIVEMGR_TEST_DB_USER` and `LIVEMGR_TEST_DB_PASSWORD`; the user must be allowed to create databases. To run a single test case, pass `livemgr.<TestCaseName>` (or `livemgr.<TestCaseName>.<test_method>`).

## How to access?

Navigate to http://127.0.0.1:8000

Use the following credentials:

	Username: admin
	Password: admin

## Screenshots

![Dashboard](/screenshots/dashboard.png?raw=true "Dashboard")
![Group Creation](/screenshots/groups-creation.png?raw=true "Group Creation")
![Settings](/screenshots/settings.png?raw=true "Settings")
![Users](/screenshots/users.png?raw=true "Users")

