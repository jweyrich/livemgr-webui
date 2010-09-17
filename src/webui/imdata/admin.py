from django.contrib import admin
from webui.imdata.models.acl import Acl, AclAdmin
from webui.imdata.models.badword import Badword, BadwordAdmin
from webui.imdata.models.buddy import Buddy, BuddyAdmin
from webui.imdata.models.conversation import Conversation, ConversationAdmin
from webui.imdata.models.grouprule import GroupRule, GroupRuleAdmin
from webui.imdata.models.message import Message, MessageAdmin
from webui.imdata.models.rule import Rule, RuleAdmin
from webui.imdata.models.setting import Setting, SettingAdmin
from webui.imdata.models.user import User, UserAdmin
from webui.imdata.models.usergroup import UserGroup, UserGroupAdmin

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
