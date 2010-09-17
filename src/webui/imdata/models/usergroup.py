from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from webui.imdata.models.rule import Rule

class UserGroup(models.Model):
	class Meta:
		app_label = 'imdata'
		db_table = 'usergroups'
		managed = False
		#ordering = ['groupname']
		verbose_name = _('usergroup')
		verbose_name_plural = _('usergroups')
		permissions = (
			("see_usergroup", "Can see usergroup"),
		)
	groupname = models.CharField(_("name"), max_length=64, unique=True)
	isactive = models.BooleanField(_("active"), default=True)
	isbuiltin = models.BooleanField(_("built-in"), default=False)
	description = models.TextField(_("description"), max_length=512, blank=True, default='')
	rules = models.ManyToManyField(Rule, through='GroupRule')
	user_count = lambda self: self.users.count()
	def __unicode__(self):
		return smart_unicode(self.groupname)

class UserGroupAdmin(admin.ModelAdmin):
	pass
