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

from django.contrib import admin
from webui.livemgr.models.acl import Acl, AclAdmin
from webui.livemgr.models.badword import Badword, BadwordAdmin
from webui.livemgr.models.buddy import Buddy, BuddyAdmin
from webui.livemgr.models.conversation import Conversation, ConversationAdmin
from webui.livemgr.models.grouprule import GroupRule, GroupRuleAdmin
from webui.livemgr.models.message import Message, MessageAdmin
from webui.livemgr.models.rule import Rule, RuleAdmin
from webui.livemgr.models.setting import Setting, SettingAdmin
from webui.livemgr.models.user import User, UserAdmin
from webui.livemgr.models.usergroup import UserGroup, UserGroupAdmin

admin.site.register(Acl, AclAdmin)
admin.site.register(Badword, BadwordAdmin)
admin.site.register(Buddy, BuddyAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(GroupRule, GroupRuleAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
