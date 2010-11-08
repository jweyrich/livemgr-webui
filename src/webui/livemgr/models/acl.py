from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

class Acl(models.Model):
	ACTION_ALLOW = 1
	ACTION_BLOCK = 2
	CHOICES_ACTIONS = (
		(ACTION_ALLOW, _('Allow')),
		(ACTION_BLOCK, _('Block')),
	)
	class Meta:
		app_label = 'livemgr'
		db_table = 'acls'
		managed = False
		unique_together = ('localim', 'remoteim')
		#ordering = ['action', 'localim', 'remoteim']
		verbose_name = _('acl')
		verbose_name_plural = _('acls')
		permissions = (
			("see_acl", "Can see acl"),
		)
	localim = models.CharField(_("user"), max_length=128)
	remoteim = models.CharField(_("buddy"), max_length=128)
	action = models.PositiveSmallIntegerField(_("action"), choices=CHOICES_ACTIONS)
	#action = models.CharField("Action", max_length=5, choices=CHOICES_ACTIONS)
	def __unicode__(self):
		return smart_unicode('%d %s %s %s' % (self.id, self.action,
			self.localim, self.remoteim))

class AclAdmin(admin.ModelAdmin):
	pass
