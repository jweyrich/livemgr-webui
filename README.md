## How to run?

	docker build -t . livemgr-webui:latest
	
	docker-compose up

	docker-compose run db "mysql -uroot --password=123456 < /docker-entrypoint-initdb.d/create_schema.sql"

	docker-compose run db "mysql -uroot --password=123456 < /docker-entrypoint-initdb.d/create_tables.sql"

	docker-compose run app /opt/envs/livemgr-webui/bin/python webui/manage.py syncdb --noinput --settings=settings_example