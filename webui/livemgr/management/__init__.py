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

from django.contrib.auth.models import Permission as DjangoPermission
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.models import Group as DjangoGroup
from django.conf import settings
from django.db import transaction
from django.db.models import signals
import django
import sys

def bla():
    permissions = [
                   'see_conversation',
                   'see_dashboard',
                   'see_message',
                   'change_message'
                  ]

    result = DjangoPermission.objects.filter(codename__in=permissions).values_list('id', flat=True).order_by('id')
    return result

def install(**kwargs):
    audit_group, created = DjangoGroup.objects.get_or_create(name='auditor')
    # Django 1.9 adds set(); 1.10 deprecates assigning to a many-to-many
    # relation, which saves implicitly.
    if django.VERSION >= (1, 9):
        audit_group.permissions.set(bla())
    else:
        audit_group.permissions = bla()
    audit_group.save()

    first_run = False
    try:
        DjangoUser.objects.get(username='admin')
    except DjangoUser.DoesNotExist:
        first_run = True
        user = DjangoUser.objects.create(
            username='admin',
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        user.set_password('admin')
        user.save()

    try:
        DjangoUser.objects.get(username='auditor')
    except DjangoUser.DoesNotExist:
        user = DjangoUser.objects.create(
            username='auditor',
            is_active=True,
            is_superuser=False,
            is_staff=False
        )
        user.groups.add(audit_group)
        user.set_password('auditor')
        user.save()

    if first_run:
        offer_sample_data(kwargs.get('interactive', False), kwargs.get('verbosity', 1))

def offer_sample_data(interactive, verbosity):
    """
    On the first migrate, the one that creates the admin account, offers to
    load the sample data (see webui/livemgr/sample_data.py), as long as the
    livemgr tables exist and are empty.
    """
    from webui.livemgr import sample_data
    if not sample_data.tables_exist() or sample_data.existing_rows():
        return
    if interactive and sys.stdin.isatty():
        if ask_yes_no('\nWould you like to load sample data (users, groups, ACLs, '
                'badwords and conversations) to try out the web UI? (yes/no): '):
            with transaction.atomic():
                counts = sample_data.load()
            print('Loaded %s.' % sample_data.format_counts(counts))
            return
    if verbosity >= 1:
        print('\nTo load sample data to try out the web UI, run:\n'
            '  python webui/manage.py load_sample_data --settings=%s' % settings.SETTINGS_MODULE)

def ask_yes_no(question):
    while True:
        try:
            answer = input(question).strip().lower()
        except EOFError:
            return False
        if answer in ('yes', 'y'):
            return True
        if answer in ('no', 'n'):
            return False
        print("Please answer 'yes' or 'no'.")

# Django 1.7 replaces post_syncdb with post_migrate, whose sender is the app's
# AppConfig. migrate imports this module after django.contrib.auth's, so the
# permissions the hook assigns are created first. Django 1.9 still imports the
# apps' management modules; once a version stops, move the hook to an
# AppConfig.ready().
if django.VERSION >= (1, 7):
    from django.apps import apps
    signals.post_migrate.connect(install, sender=apps.get_app_config('livemgr'))
else:
    from webui.livemgr import models as livemgr_models
    signals.post_syncdb.connect(install, sender=livemgr_models)
