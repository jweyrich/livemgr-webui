from django.db import models
from django.utils.translation import ugettext_lazy as _
from webui.common.auth.auth_user_profile import AuthUserProfileModel

class Profile(AuthUserProfileModel):
	class Meta:
		app_label = 'livemgr'
		db_table = 'auth_user_profile'
		managed = True
	language = models.CharField(_('language'), max_length=5, default='en')
	debug = models.BooleanField(_("enable debug"), default=False)
	per_page_acls = models.PositiveSmallIntegerField(default=10)
	per_page_users = models.PositiveSmallIntegerField(default=10)
	per_page_usergroups = models.PositiveSmallIntegerField(default=10)
	per_page_conversations = models.PositiveSmallIntegerField(default=10)
	per_page_badwords = models.PositiveSmallIntegerField(default=10)
	per_page_buddies = models.PositiveSmallIntegerField(default=10)
