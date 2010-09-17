from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

class Badword(models.Model):
	class Meta:
		app_label = 'imdata'
		db_table = 'badwords'
		managed = False
		#ordering = ['badword']
		verbose_name = _('badword')
		verbose_name_plural = _('badwords')
		permissions = (
			("see_badword", "Can see badword"),
		)
	badword = models.CharField(_("badword"), max_length=128, unique=True)
	isregex = models.BooleanField(_("regular expression"), default=False)
	isenabled = models.BooleanField(_("enabled"), default=True)
	def __unicode__(self):
		return smart_unicode(self.badword)

class BadwordAdmin(admin.ModelAdmin):
	pass
