from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

"""
	Based on: http://djangosnippets.org/snippets/1469/
	Author: willhardy
	Posted: April 28, 2009

	Convenience parent class for UserProfile model
"""
class AuthUserProfileBase(models.base.ModelBase):
	# _prepare is not part of the public API and may change
	def _prepare(self):
		super(AuthUserProfileBase, self)._prepare()
		def on_save(sender, instance, created, **kwargs):
			if created:
				self.objects.create(user=instance)
		# Automatically link profile when a new user is created
		post_save.connect(on_save, sender=User, weak=False)

class AuthUserProfileModel(models.Model):
	class Meta:
		abstract = True
	__metaclass__ = AuthUserProfileBase
	user = models.OneToOneField(User, db_column='auth_user_id',
		primary_key=True, parent_link=True)
