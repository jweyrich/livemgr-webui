from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

class License(models.Model):
	class Meta:
		app_label = 'imdata'
		db_table = 'license'
		managed = False
		#ordering = [id]
		verbose_name = _('license')
		verbose_name_plural = _('licenses')
		permissions = (
			("see_license", "Can see license"),
		)
	certificate = models.CharField(_("Certificate"), max_length=10000)
	hash = models.CharField(_("Hash"), max_length=40, unique=True)
	def __unicode__(self):
		return smart_unicode('%d %s' % (self.id, self.hash))

class LicenseAdmin(admin.ModelAdmin):
	pass
