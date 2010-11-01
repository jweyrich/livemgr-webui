from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

class Message(models.Model):
	class Type:
		UNKNOWN = 0
		MSG = 1
		FILE = 2
		TYPING = 3
		CAPS = 4
		WEBCAM = 5
		REMOTEDESKTOP = 6
		APPLICATION = 7
		EMOTICON = 8
		INK = 9
		NUDGE = 10
		WINK = 11
		VOICECLIP = 12
		GAMES = 13
		PHOTO = 14
	CHOICES_TYPES = (
		(Type.UNKNOWN, _('unknown')),
		(Type.MSG, _('msg')),
		(Type.FILE, _('file')),
		(Type.TYPING, _('typing')),
		(Type.CAPS, _('caps')),
		(Type.WEBCAM, _('webcam')),
		(Type.REMOTEDESKTOP, _('remotedesktop')),
		(Type.APPLICATION, _('application')),
		(Type.EMOTICON, _('emoticon')),
		(Type.INK, _('ink')),
		(Type.NUDGE, _('nudge')),
		(Type.WINK, _('wink')),
		(Type.VOICECLIP, _('voiceclip')),
		(Type.GAMES, _('games')),
		(Type.PHOTO, _('photo')),
	)
	class Meta:
		app_label = 'imdata'
		db_table = 'messages'
		managed = False
		#ordering = ['-timestamp']
		verbose_name = _('message')
		verbose_name_plural = _('messages')
		permissions = (
			("see_message", "Can see message"),
		)
	conversation_id = models.IntegerField(_("conversation #"))
	timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
	#conversation = models.ForeignKey(Conversation, db_column='conversation_id',
	#								verbose_name="Conversation")
	# NOTE: Avoiding IPAddressField because it stores text instead of int
	clientip = models.IntegerField(_("client IP"))
	inbound = models.BooleanField(_("inbound"))
	type = models.IntegerField(_("type"), choices=CHOICES_TYPES)
	# NOTE: Avoiding EmailField because most protocols don't use email addresses
	localim = models.CharField(_("user"), max_length=128)
	remoteim = models.CharField(_("buddy"), max_length=128)
	filtered = models.BooleanField(_("filtered"))
	content = models.TextField(_("content"), max_length=2000)
	def __unicode__(self):
		return smart_unicode('%d %s %s %s' % (self.id, self.timestamp, self.localim,
										   self.remoteim))

class MessageAdmin(admin.ModelAdmin):
	pass
