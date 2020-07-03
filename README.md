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

	docker build -t . livemgr-webui:latest
	
	docker-compose up

	docker-compose run db "mysql -uroot --password=123456 < /docker-entrypoint-initdb.d/create_schema.sql"

	docker-compose run db "mysql -uroot --password=123456 < /docker-entrypoint-initdb.d/create_tables.sql"

	docker-compose run app /opt/envs/livemgr-webui/bin/python webui/manage.py syncdb --noinput --settings=settings_example

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

