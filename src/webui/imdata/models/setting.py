from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

class Setting(models.Model):
	class Meta:
		app_label = 'imdata'
		db_table = 'settings'
		managed = False
		#ordering = ['name']
		verbose_name = _('setting')
		verbose_name_plural = _('settings')
		permissions = (
			("see_setting", "Can see setting"),
		)
	name = models.CharField(_("name"), max_length=64, unique=True)
	value = models.CharField(_("value"), max_length=255, null=True, blank=True)
	def __unicode__(self):
		return smart_unicode(self.name)

class SettingAdmin(admin.ModelAdmin):
	pass
