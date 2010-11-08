from django.db import models
from django.utils.encoding import smart_unicode

class ViewMessages(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'view_messages'
		managed = False
		#ordering = ['-timestamp']
	conversation_id = models.IntegerField()
	timestamp = models.DateTimeField()
	inbound = models.BooleanField()
	#localuser = models.ForeignKey(User, db_column='localuser')
	localuser_id = models.IntegerField()
	localim = models.CharField(max_length=128)
	remoteim = models.CharField(max_length=128)
	clientip = models.IntegerField()
	filtered = models.BooleanField()
	content = models.TextField()
	is_active = models.BooleanField()
	def __unicode__(self):
		return smart_unicode('%d %d %s %s %s %d' % (
			self.id, self.id_conversation, self.timestamp,
			self.localim, self.remoteim, self.is_active))
