from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from webui.livemgr.models.rule import Rule
from webui.livemgr.models.usergroup import UserGroup

class GroupRule(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'grouprules'
		managed = False
		unique_together = ('rule', 'group')
		#ordering = ['rule', 'group']
		verbose_name = _('grouprule')
		verbose_name_plural = _('grouprules')
	rule = models.ForeignKey(Rule, db_column='rule_id', verbose_name=_("rule"))
	group = models.ForeignKey(UserGroup, db_column='group_id', verbose_name=_("group"))
	def __unicode__(self):
		return smart_unicode('%d %s %s' % (self.id, self.rule, self.group))

class GroupRuleAdmin(admin.ModelAdmin):
	pass
