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
