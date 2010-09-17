from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

class Rule(models.Model):
	class Meta:
		app_label = 'imdata'
		db_table = 'rules'
		managed = False
		#ordering = ['rulename']
		verbose_name = _('rule')
		verbose_name_plural = _('rules')
		permissions = (
			("see_rule", "Can see rule"),
		)
	rulename = models.CharField(_("name"), max_length=128, unique=True)
	description = models.TextField(_("description"), max_length=512)
	def __unicode__(self):
		return smart_unicode(self.rulename)
	
class RuleAdmin(admin.ModelAdmin):
	pass

class LocalizedRules():
	alert = Rule(1, _('alert'), '')
	application = Rule(2, _('application'), '')
	caps = Rule(3, _('caps'), '')
	crypt = Rule(4, _('crypt'), '')
	emoticons = Rule(5, _('emoticons'), '')
	filetransfer = Rule(6, _('filetransfer'), '')
	filter = Rule(7, _('filter'), '')
	ink = Rule(8, _('ink'), '')
	log = Rule(9, _('log'), '')
	nudge = Rule(10, _('nudge'), '')
	remotedesktop = Rule(11, _('remotedesktop'), '')
	voiceclip = Rule(12, _('voiceclip'), '')
	webcam = Rule(13, _('webcam'), '')
	wink = Rule(14, _('wink'), '')
	games = Rule(15, _('games'), '')
	photo = Rule(16, _('photo'), '')
	
# TODO mudar ordem e adicionar GAMES e PHOTO