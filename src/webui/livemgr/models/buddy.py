from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from webui.livemgr.models.user import User

class Buddy(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'buddies'
		managed = False
		unique_together = ('user', 'username')
		#ordering = ['username', 'user']
		verbose_name = _('buddy')
		verbose_name_plural = _('buddies')
		permissions = (
			("see_buddy", "Can see buddy"),
		)
	username = models.CharField(_("username"), max_length=128)
	displayname = models.CharField(_("display name"), max_length=130, blank=True, default='')
	psm = models.CharField(_("status message"), max_length=130, blank=True, default='')
	#status = models.PositiveSmallIntegerField("status", choices=CHOICES_STATUS)
	status = models.CharField(_("status"), max_length=3, choices=User.CHOICES_STATUS)
	isblocked = models.BooleanField(_("blocked"), default=False)
	user = models.ForeignKey(User, db_column='user_id', verbose_name=_("user"), related_name="buddies")
	def __unicode__(self):
		return smart_unicode(self.username)

class BuddyAdmin(admin.ModelAdmin):
	pass
