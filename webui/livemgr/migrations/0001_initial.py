# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


# Only the web UI's own table. Django 1.7 fakes an initial migration whose
# tables all exist, which is the case on installs created by syncdb, so this
# one must not list the backend's tables (see 0002_backend_models).
class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(parent_link=True, primary_key=True, db_column='auth_user_id', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('language', models.CharField(default='en', max_length=5, verbose_name='language')),
                ('debug', models.BooleanField(default=False, verbose_name='enable debug')),
                ('per_page_acls', models.PositiveSmallIntegerField(default=10)),
                ('per_page_users', models.PositiveSmallIntegerField(default=10)),
                ('per_page_usergroups', models.PositiveSmallIntegerField(default=10)),
                ('per_page_conversations', models.PositiveSmallIntegerField(default=10)),
                ('per_page_badwords', models.PositiveSmallIntegerField(default=10)),
                ('per_page_buddies', models.PositiveSmallIntegerField(default=10)),
            ],
            options={
                'db_table': 'auth_user_profile',
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
