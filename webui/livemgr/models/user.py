from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from webui.livemgr.models.usergroup import UserGroup

class User(models.Model):
	CHOICES_STATUS = (
		('NLN', _('Online')),
		('BSY', _('Busy')),
		('IDL', _('Idle')),
		('AWY', _('Away')),
		('BRB', _('Be right back')),
		('PHN', _('On the phone')),
		('LUN', _('Out to lunch')),
		('HDN', _('Invisible')),
		('FLN', _('Offline')),
	)
	class Meta:
		app_label = 'livemgr'
		db_table = 'users'
		managed = False
		#ordering = ['username']
		verbose_name = _('user')
		verbose_name_plural = _('users')
		permissions = (
			("see_user", "Can see user"),
		)
	group = models.ForeignKey(UserGroup, db_column='group_id', verbose_name=_("group"), related_name="users")
	username = models.CharField(_("username"), max_length=128, unique=True)
	displayname = models.CharField(_("display name"), max_length=130, blank=True, default='')
	psm = models.CharField(_("status message"), max_length=130, blank=True, default='')
	#status = models.PositiveSmallIntegerField("Status", choices=CHOICES_STATUS)
	status = models.CharField(_("status"), max_length=3, choices=CHOICES_STATUS)
	# NOTE: Do not use auto_now, auto_add_now or default properties
	lastlogin = models.DateTimeField(_("last login"))
	isenabled = models.BooleanField(_("enabled"), default=True)
	def __unicode__(self):
		return smart_unicode(self.username)

def lookup_user_status(value):
	status = [(k, v) for (k, v) in User.CHOICES_STATUS if k == value]
	if status:
		return status[0]
	else:
		return None

class UserAdmin(admin.ModelAdmin):
	pass
