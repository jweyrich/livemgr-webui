from django.db import models
from django.utils.translation import ugettext_lazy as _
from webui.common.auth.auth_user_profile import AuthUserProfileModel

class Profile(AuthUserProfileModel):
	class Meta:
		app_label = 'imdata'
		db_table = 'auth_user_profile'
		managed = False
	language = models.CharField(_('language'), max_length=5, default='en')
	debug = models.BooleanField(_("enable debug"), default=False)
	per_page_acls = models.PositiveSmallIntegerField()
	per_page_users = models.PositiveSmallIntegerField()
	per_page_usergroups = models.PositiveSmallIntegerField()
	per_page_conversations = models.PositiveSmallIntegerField()
	per_page_badwords = models.PositiveSmallIntegerField()
	per_page_buddies = models.PositiveSmallIntegerField()
