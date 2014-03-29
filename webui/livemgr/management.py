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
from django.db.models import signals
from webui.livemgr import models as livemgr_models

def bla():
    permissions = [
                   'see_conversation',
                   'see_dashboard',
                   'see_message',
                   'change_message'
                  ]

    result = DjangoPermission.objects.filter(codename__in=permissions).values_list('id', flat=True).order_by('id')
    return result

def install(app, created_models, **kwargs):
    audit_group, created = DjangoGroup.objects.get_or_create(name='auditor')
    audit_group.permissions = bla()
    audit_group.save()

    try:
        DjangoUser.objects.get(username='admin')
    except DjangoUser.DoesNotExist:
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

signals.post_syncdb.connect(install, sender=livemgr_models)
