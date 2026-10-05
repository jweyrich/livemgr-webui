# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# The backend's tables, owned by bootstrap/db/create_tables.sql. The models are
# `managed = False`, so migrating only records their state. Not part of
# 0001_initial, because Dashboard and Support have no table, which would keep
# Django from faking it on existing installs.
class Migration(migrations.Migration):

    dependencies = [
        ('livemgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('localim', models.CharField(max_length=128, verbose_name='user')),
                ('remoteim', models.CharField(max_length=128, verbose_name='buddy')),
                ('action', models.PositiveSmallIntegerField(verbose_name='action', choices=[(1, 'Allow'), (2, 'Block')])),
            ],
            options={
                'managed': False,
                'verbose_name_plural': 'acls',
                'db_table': 'acls',
                'verbose_name': 'acl',
                'permissions': (('see_acl', 'Can see acl'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Badword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('badword', models.CharField(unique=True, max_length=128, verbose_name='badword')),
                ('isregex', models.BooleanField(default=False, verbose_name='regular expression')),
                ('isenabled', models.BooleanField(default=True, verbose_name='enabled')),
            ],
            options={
                'verbose_name': 'badword',
                'db_table': 'badwords',
                'managed': False,
                'verbose_name_plural': 'badwords',
                'permissions': (('see_badword', 'Can see badword'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Buddy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=128, verbose_name='username')),
                ('displayname', models.CharField(default='', max_length=130, verbose_name='display name', blank=True)),
                ('psm', models.CharField(default='', max_length=130, verbose_name='status message', blank=True)),
                ('status', models.CharField(max_length=3, verbose_name='status', choices=[('NLN', 'Online'), ('BSY', 'Busy'), ('IDL', 'Idle'), ('AWY', 'Away'), ('BRB', 'Be right back'), ('PHN', 'On the phone'), ('LUN', 'Out to lunch'), ('HDN', 'Invisible'), ('FLN', 'Offline')])),
                ('isblocked', models.BooleanField(default=False, verbose_name='blocked')),
            ],
            options={
                'managed': False,
                'verbose_name_plural': 'buddies',
                'db_table': 'buddies',
                'verbose_name': 'buddy',
                'permissions': (('see_buddy', 'Can see buddy'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('status', models.PositiveSmallIntegerField(verbose_name='Status', db_column='status')),
            ],
            options={
                'verbose_name': 'conversation',
                'db_table': 'conversations',
                'managed': False,
                'verbose_name_plural': 'conversations',
                'permissions': (('see_conversation', 'Can see conversation'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'dashboard',
                'db_table': '',
                'managed': False,
                'permissions': (('see_dashboard', 'Can see dashboard'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'grouprules',
                'verbose_name': 'grouprule',
                'verbose_name_plural': 'grouprules',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('conversation_id', models.IntegerField(verbose_name='conversation #')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('clientip', models.IntegerField(verbose_name='client IP')),
                ('inbound', models.BooleanField(default=False, verbose_name='inbound')),
                ('type', models.IntegerField(verbose_name='type', choices=[(0, 'unknown'), (1, 'msg'), (2, 'file'), (3, 'typing'), (4, 'caps'), (5, 'webcam'), (6, 'remotedesktop'), (7, 'application'), (8, 'emoticon'), (9, 'ink'), (10, 'nudge'), (11, 'wink'), (12, 'voiceclip'), (13, 'games'), (14, 'photo')])),
                ('localim', models.CharField(max_length=128, verbose_name='user')),
                ('remoteim', models.CharField(max_length=128, verbose_name='buddy')),
                ('filtered', models.BooleanField(default=False, verbose_name='filtered')),
                ('content', models.TextField(max_length=2000, verbose_name='content')),
            ],
            options={
                'verbose_name': 'message',
                'db_table': 'messages',
                'managed': False,
                'verbose_name_plural': 'messages',
                'permissions': (('see_message', 'Can see message'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rulename', models.CharField(unique=True, max_length=128, verbose_name='name')),
                ('description', models.TextField(max_length=512, verbose_name='description')),
            ],
            options={
                'verbose_name': 'rule',
                'db_table': 'rules',
                'managed': False,
                'verbose_name_plural': 'rules',
                'permissions': (('see_rule', 'Can see rule'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64, verbose_name='name')),
                ('value', models.CharField(max_length=255, null=True, verbose_name='value', blank=True)),
            ],
            options={
                'verbose_name': 'setting',
                'db_table': 'settings',
                'managed': False,
                'verbose_name_plural': 'settings',
                'permissions': (('see_setting', 'Can see setting'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'support',
                'db_table': '',
                'managed': False,
                'permissions': (('see_support', 'Can see support'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=128, verbose_name='username')),
                ('displayname', models.CharField(default='', max_length=130, verbose_name='display name', blank=True)),
                ('psm', models.CharField(default='', max_length=130, verbose_name='status message', blank=True)),
                ('status', models.CharField(max_length=3, verbose_name='status', choices=[('NLN', 'Online'), ('BSY', 'Busy'), ('IDL', 'Idle'), ('AWY', 'Away'), ('BRB', 'Be right back'), ('PHN', 'On the phone'), ('LUN', 'Out to lunch'), ('HDN', 'Invisible'), ('FLN', 'Offline')])),
                ('lastlogin', models.DateTimeField(verbose_name='last login')),
                ('isenabled', models.BooleanField(default=True, verbose_name='enabled')),
            ],
            options={
                'verbose_name': 'user',
                'db_table': 'users',
                'managed': False,
                'verbose_name_plural': 'users',
                'permissions': (('see_user', 'Can see user'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('groupname', models.CharField(unique=True, max_length=64, verbose_name='name')),
                ('isactive', models.BooleanField(default=True, verbose_name='active')),
                ('isbuiltin', models.BooleanField(default=False, verbose_name='built-in')),
                ('description', models.TextField(default='', max_length=512, verbose_name='description', blank=True)),
            ],
            options={
                'verbose_name': 'usergroup',
                'db_table': 'usergroups',
                'managed': False,
                'verbose_name_plural': 'usergroups',
                'permissions': (('see_usergroup', 'Can see usergroup'),),
            },
            bases=(models.Model,),
        ),
    ]
