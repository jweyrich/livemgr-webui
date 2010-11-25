from django.db import models
from django.utils.translation import ugettext_lazy as _

class Dashboard(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = ''
		managed = False
		verbose_name = _('dashboard')
		permissions = (
			("see_dashboard", "Can see dashboard"),
		)

class Support(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = ''
		managed = False
		verbose_name = _('support')
		permissions = (
			("see_support", "Can see support"),
		)
