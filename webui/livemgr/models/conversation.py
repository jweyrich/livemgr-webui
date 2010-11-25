from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from webui.livemgr.models.user import User

class Conversation(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'conversations'
		managed = False
		#ordering = ['user', '-timestamp', 'buddy']
		verbose_name = _('conversation')
		verbose_name_plural = _('conversations')
		permissions = (
			("see_conversation", "Can see conversation"),
		)
	user = models.ForeignKey(User, db_column='user_id', verbose_name=_("user"))
	timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
	status = models.PositiveSmallIntegerField(db_column='status', verbose_name=_("Status"))
	def __unicode__(self):
		return smart_unicode('%d %s %s %i' % (self.id, self.user, self.timestamp,
			self.status))

class ConversationAdmin(admin.ModelAdmin):
	pass
