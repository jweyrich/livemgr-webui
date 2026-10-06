# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Jardel Weyrich
#
# This file is part of livemgr-webui.
#
# livemgr-webui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# livemgr-webui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jardel Weyrich <jweyrich@gmail.com>

from django.contrib.auth.models import User as AuthUser
from django.db import connection
from webui.livemgr.models import Acl, Badword, Buddy, Conversation, GroupRule, \
	Message, Profile, Setting, User, UserGroup
from webui.livemgr.models.rule import LocalizedRules, Rule
from webui.livemgr.models.user import lookup_user_status
from webui.livemgr.tests.base import LivemgrTestCase, GUEST_GROUP_ID, at

class SchemaContractTest(LivemgrTestCase):
	"""
	The backend owns these tables. Every model field must map to an existing
	column, otherwise queries fail at runtime (not at startup).
	"""
	MODELS = [Acl, Badword, Buddy, Conversation, GroupRule, Message, Rule,
		Setting, User, UserGroup]

	def test_unmanaged_models_match_the_bootstrap_schema(self):
		cursor = connection.cursor()
		for model in self.MODELS:
			self.assertFalse(model._meta.managed, model)
			cursor.execute('SELECT * FROM %s LIMIT 0' % model._meta.db_table)
			columns = set(desc[0] for desc in cursor.description)
			for field in model._meta.local_fields:
				self.assertTrue(field.column in columns,
					'%s.%s is missing' % (model._meta.db_table, field.column))

	def test_reference_data_is_present(self):
		guest = UserGroup.objects.get(pk=GUEST_GROUP_ID)
		self.assertEqual(guest.groupname, 'guest')
		self.assertTrue(guest.isbuiltin)
		self.assertTrue(guest.isactive)
		self.assertEqual(Rule.objects.count(), 16)
		self.assertEqual(
			dict(Setting.objects.values_list('name', 'value')),
			{
				'allow_self_reg': '1',
				'min_protocol_version': '8',
				'max_protocol_version': '18',
				'filtered_msg': 'Ouch...',
				'default_warning': 'Big Brother is watching you',
			})

	def test_localized_rules_mirror_the_rules_table(self):
		stored = dict(Rule.objects.values_list('id', 'rulename'))
		localized = dict((r.id, str(r.rulename)) for r in LocalizedRules.RULES)
		self.assertEqual(stored, localized)

class ModelBehaviorTest(LivemgrTestCase):
	def test_unicode_representations(self):
		user = self.make_user('alice@example.com')
		self.assertEqual(str(user), u'alice@example.com')
		self.assertEqual(str(self.make_buddy(user, 'bob@example.com')), u'bob@example.com')
		self.assertEqual(str(self.make_badword('darn')), u'darn')
		self.assertEqual(str(UserGroup.objects.get(pk=GUEST_GROUP_ID)), u'guest')
		self.assertEqual(str(Setting.objects.get(name='filtered_msg')), u'filtered_msg')
		acl = self.make_acl('alice@example.com', '*@example.org', Acl.ACTION_BLOCK)
		self.assertEqual(str(acl), u'%d 2 alice@example.com *@example.org' % acl.id)

	def test_conversation_and_message_representations(self):
		user = self.make_user('alice@example.com')
		conversation = self.make_conversation(user, timestamp=at(2010, 5, 17, 9, 0, 0))
		self.assertEqual(str(conversation),
			u'%d alice@example.com 2010-05-17 09:00:00 1' % conversation.id)
		message = self.make_message(conversation.id, timestamp=at(2010, 5, 17, 9, 0, 5))
		self.assertEqual(str(message),
			u'%d 2010-05-17 09:00:05 %d alice@example.com bob@example.com' % (message.id, conversation.id))

	def test_unicode_round_trip(self):
		user = self.make_user(u'joão@example.com', displayname=u'João Ção')
		self.assertEqual(User.objects.get(pk=user.pk).displayname, u'João Ção')

	def test_group_user_count(self):
		group = self.make_group('sales')
		self.assertEqual(group.user_count(), 0)
		self.make_user('a@example.com', group_id=group.id)
		self.make_user('b@example.com', group_id=group.id)
		self.assertEqual(group.user_count(), 2)

	def test_group_rules_through_grouprule(self):
		group = self.make_group('sales')
		GroupRule.objects.create(group=group, rule_id=3)
		GroupRule.objects.create(group=group, rule_id=5)
		self.assertEqual(sorted(group.rules.values_list('id', flat=True)), [3, 5])

	def test_user_buddies_relation(self):
		user = self.make_user()
		self.make_buddy(user, 'b1@example.com')
		self.make_buddy(user, 'b2@example.com')
		self.assertEqual(user.buddies.count(), 2)

	def test_new_user_defaults(self):
		user = self.make_user()
		user = User.objects.get(pk=user.pk)
		self.assertTrue(user.isenabled)
		self.assertEqual(user.lastlogin, None)
		self.assertEqual(user.group_id, GUEST_GROUP_ID)

	def test_new_message_defaults(self):
		# Django 1.6 no longer defaults a BooleanField to False
		conversation = self.make_conversation(self.make_user())
		message = Message.objects.create(conversation_id=conversation.id, clientip=0,
			type=Message.Type.MSG, localim='alice@example.com', remoteim='bob@example.com',
			content='hello')
		message = Message.objects.get(pk=message.pk)
		self.assertEqual(message.inbound, False)
		self.assertEqual(message.filtered, False)

	def test_lookup_user_status(self):
		self.assertEqual(lookup_user_status('NLN')[0], 'NLN')
		self.assertEqual(str(lookup_user_status('NLN')[1]), u'Online')
		self.assertEqual(lookup_user_status('XXX'), None)

	def test_message_type_choices_cover_every_type(self):
		self.assertEqual([k for k, v in Message.CHOICES_TYPES], list(range(0, 15)))

class ProfileTest(LivemgrTestCase):
	"""
	Profile relies on a custom metaclass hooking ModelBase._prepare (private API),
	which may change across Django versions. The views reach it through the
	one-to-one relation (user.profile): Django 1.5 deprecates AUTH_PROFILE_MODULE
	and User.get_profile().
	"""
	def test_profile_is_created_with_the_account(self):
		account = AuthUser.objects.create(username='someone')
		profile = Profile.objects.get(user=account)
		self.assertEqual(profile.language, 'en')
		self.assertFalse(profile.debug)
		for field in ['per_page_acls', 'per_page_users', 'per_page_usergroups',
				'per_page_conversations', 'per_page_badwords', 'per_page_buddies']:
			self.assertEqual(getattr(profile, field), 10, field)

	def test_profile_is_not_duplicated_on_update(self):
		account = AuthUser.objects.create(username='someone')
		account.first_name = 'Some'
		account.save()
		self.assertEqual(Profile.objects.filter(user=account).count(), 1)

	def test_profile_relation(self):
		account = AuthUser.objects.create(username='someone')
		self.assertEqual(account.profile, Profile.objects.get(user=account))

	def test_profile_is_deleted_with_the_account(self):
		account = AuthUser.objects.create(username='someone')
		account.delete()
		self.assertEqual(Profile.objects.filter(user__username='someone').count(), 0)
