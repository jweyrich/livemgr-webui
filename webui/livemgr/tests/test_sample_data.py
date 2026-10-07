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

from datetime import datetime, timedelta
from django.contrib.auth.models import User as AuthUser
from django.core.management import call_command
from django.core.management.base import CommandError
from fnmatch import fnmatchcase
from io import StringIO
from unittest import mock
from webui.livemgr import sample_data
from webui.livemgr.controllers.dashboard import query_latest_conversations, \
	query_most_active_users, query_total_active_conversations, query_total_users_online
from webui.livemgr.management import install
from webui.livemgr.models import Acl, Badword, Buddy, Conversation, GroupRule, \
	Message, User, UserGroup
from webui.livemgr.tests.base import GUEST_GROUP_ID, LivemgrTestCase

DAYS = 21 # Enough for every page, and faster than the default

def group_rules():
	rules = {}
	for (group_id, rule_id) in GroupRule.objects.values_list('group_id', 'rule_id'):
		rules.setdefault(group_id, set()).add(rule_id)
	return rules

class SampleDataTest(LivemgrTestCase):
	@classmethod
	def setUpTestData(cls):
		cls.counts = dict(sample_data.load(days=DAYS))
		cls.now = datetime.now()

	def test_counts(self):
		self.assertEqual(self.counts, {
			'groups': UserGroup.objects.filter(isbuiltin=False).count(),
			'users': User.objects.count(),
			'buddies': Buddy.objects.count(),
			'acls': Acl.objects.count(),
			'badwords': Badword.objects.count(),
			'conversations': Conversation.objects.count(),
			'messages': Message.objects.count(),
		})
		self.assertEqual(self.counts['groups'], len(sample_data.GROUPS))
		self.assertEqual(self.counts['users'], len(sample_data.EMPLOYEES))
		# More than a page of each
		for name in ('users', 'acls', 'badwords', 'conversations'):
			self.assertTrue(self.counts[name] > 10, name)

	def test_users(self):
		self.assertTrue(User.objects.filter(group_id=GUEST_GROUP_ID).exists())
		self.assertTrue(User.objects.filter(isenabled=False).exists())
		self.assertTrue(User.objects.filter(lastlogin=None).exists())
		self.assertTrue(UserGroup.objects.filter(isactive=False).exists())
		self.assertEqual(User.objects.get(username='zoe.laurent@example.com').displayname, 'Zoë')

	def test_buddies(self):
		for user in User.objects.all():
			self.assertTrue(user.buddies.exists(), user)
		# Coworkers show up as they are, except the invisible ones
		for buddy in Buddy.objects.filter(username__endswith='@example.com'):
			user = User.objects.get(username=buddy.username)
			self.assertEqual(buddy.displayname, user.displayname)
			self.assertEqual(buddy.status, 'FLN' if user.status == 'HDN' else user.status)
		self.assertTrue(Buddy.objects.filter(isblocked=True).exists())

	def test_conversations_follow_the_group_rules(self):
		rules = group_rules()
		users = dict((u.id, u) for u in User.objects.all())
		types = {}
		for (conversation_id, type) in Message.objects.values_list('conversation_id', 'type'):
			types.setdefault(conversation_id, set()).add(type)
		for conversation in Conversation.objects.all():
			rules_of_group = rules.get(users[conversation.user_id].group_id, set())
			self.assertTrue(sample_data.RULE_HISTORY in rules_of_group, conversation)
			for type in types[conversation.id]:
				self.assertFalse(sample_data.BLOCKING_RULES.get(type) in rules_of_group,
					(conversation, type))
		# Executives have no history
		self.assertFalse(Conversation.objects.filter(user__group__groupname=sample_data.EXECUTIVES).exists())

	def test_messages_are_between_the_user_and_a_buddy(self):
		users = dict((u.id, u) for u in User.objects.all())
		conversations = dict((c.id, users[c.user_id]) for c in Conversation.objects.all())
		buddies = set(Buddy.objects.filter(isblocked=False).values_list('user__username', 'username'))
		acls = list(Acl.objects.filter(action=Acl.ACTION_BLOCK).values_list('localim', 'remoteim'))
		pairs = set()
		for message in Message.objects.all():
			self.assertEqual(message.localim, conversations[message.conversation_id].username)
			pairs.add((message.localim, message.remoteim))
		for (localim, remoteim) in pairs:
			self.assertTrue((localim, remoteim) in buddies, (localim, remoteim))
			for (l, r) in acls:
				self.assertFalse(fnmatchcase(localim, l) and fnmatchcase(remoteim, r),
					(localim, remoteim, l, r))

	def test_filtered_messages_have_badwords(self):
		patterns = sample_data.badword_patterns(
			Badword.objects.values_list('badword', 'isregex', 'isenabled'))
		rules = group_rules()
		groups = dict(User.objects.values_list('username', 'group_id'))
		for message in Message.objects.all():
			expected = message.type == Message.Type.MSG \
				and sample_data.RULE_BADWORDS in rules.get(groups[message.localim], ()) \
				and any(p.search(message.content) for p in patterns)
			self.assertEqual(message.filtered, expected, message.content)
		self.assertTrue(Message.objects.filter(filtered=True).exists())
		# The regular expressions match too
		self.assertTrue(Message.objects.filter(filtered=True, content__contains='4111 1111').exists())

	def test_timeline(self):
		first_day = datetime.combine((self.now - timedelta(days=DAYS)).date(), datetime.min.time())
		today = datetime.combine(self.now.date(), datetime.min.time())
		for conversation in Conversation.objects.all():
			timestamps = list(Message.objects.filter(conversation_id=conversation.id)
				.order_by('id').values_list('timestamp', flat=True))
			self.assertTrue(timestamps, conversation)
			self.assertEqual(timestamps, sorted(timestamps))
			self.assertEqual(conversation.timestamp, timestamps[0])
			self.assertTrue(first_day <= timestamps[0] and timestamps[-1] <= self.now, conversation)
			if conversation.status:
				self.assertTrue(timestamps[0] >= today, conversation)
				self.assertNotEqual(conversation.user.status, 'FLN')
		self.assertTrue(Conversation.objects.filter(status=1).exists())

	def test_logins(self):
		today = datetime.combine(self.now.date(), datetime.min.time())
		for user in User.objects.all():
			if user.status != 'FLN':
				self.assertTrue(today <= user.lastlogin <= self.now, user)
			if user.lastlogin is None:
				self.assertFalse(Conversation.objects.filter(user=user).exists())
				continue
			# Nobody talks after their last login's day, nor before logging in that day
			last_day = datetime.combine(user.lastlogin.date(), datetime.min.time())
			conversations = Conversation.objects.filter(user=user)
			self.assertFalse(conversations.filter(timestamp__gte=last_day + timedelta(days=1)).exists())
			self.assertFalse(conversations.filter(timestamp__gte=last_day,
				timestamp__lt=user.lastlogin).exists(), user)

	def test_dashboard(self):
		self.assertTrue(query_total_users_online() > 0)
		self.assertTrue(query_total_active_conversations() > 0)
		self.assertTrue(query_latest_conversations(5))
		ten_days_ago = self.now - timedelta(days=10)
		for period in ('month', 'year'):
			totals = [u.total for u in query_most_active_users(5, period, ten_days_ago)]
			self.assertEqual(len(totals), 5)
			self.assertEqual(totals, sorted(totals, reverse=True))

	def test_pages(self):
		self.login_superuser()
		user = User.objects.filter(buddies__isnull=False).first()
		file_transfer = Message.objects.filter(type=Message.Type.FILE).first()
		for path in ('/', '/users/', '/users/?page=2', '/users/%d/contacts/' % user.id,
				'/groups/', '/groups/%d/' % UserGroup.objects.get(groupname='Sales').id,
				'/acls/', '/badwords/', '/conversations/', '/conversations/?page=2',
				'/conversations/%d/' % file_transfer.conversation_id):
			response = self.client.get(path)
			self.assertEqual(response.status_code, 200, path)
		response = self.client.get('/conversations/%d/report/pdf/' % file_transfer.conversation_id)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'application/pdf')

class SampleDataSeedTest(LivemgrTestCase):
	def test_same_seed_same_data(self):
		now = datetime(2010, 5, 20, 15, 30)
		def messages():
			return list(Message.objects.order_by('id').values_list('timestamp', 'localim',
				'remoteim', 'type', 'filtered', 'content'))
		sample_data.load(days=3, now=now)
		first = messages()
		sample_data.flush()
		sample_data.load(days=3, now=now)
		self.assertEqual(messages(), first)
		sample_data.flush()
		sample_data.load(days=3, seed=1, now=now)
		self.assertNotEqual(messages(), first)

class LoadSampleDataCommandTest(LivemgrTestCase):
	def call(self, **options):
		out = StringIO()
		options.setdefault('days', 1)
		call_command('load_sample_data', stdout=out, **options)
		return out.getvalue()

	def test_load(self):
		self.assertTrue(self.call().startswith('Loaded 6 groups, 40 users, '))
		self.assertEqual(User.objects.count(), 40)

	def test_refuses_to_add_to_existing_data(self):
		self.make_badword('darn')
		with self.assertRaisesRegex(CommandError, r'already has 1 badwords\. Run with --flush'):
			self.call()
		self.assertEqual(list(Badword.objects.values_list('badword', flat=True)), ['darn'])
		self.assertFalse(User.objects.exists())

	def test_flush(self):
		self.make_user('someone@example.org', group_id=self.make_group('old').id)
		self.call(flush=True, interactive=False)
		self.assertFalse(User.objects.filter(username='someone@example.org').exists())
		self.assertFalse(UserGroup.objects.filter(groupname='old').exists())
		self.assertTrue(UserGroup.objects.filter(pk=GUEST_GROUP_ID, isbuiltin=True).exists())
		self.assertEqual(User.objects.count(), 40)

	def test_flush_asks_first(self):
		self.make_user('someone@example.org')
		with mock.patch('builtins.input', return_value='no') as prompt:
			with self.assertRaisesRegex(CommandError, 'Cancelled'):
				self.call(flush=True)
		self.assertTrue('This deletes 1 users.' in prompt.call_args[0][0])
		self.assertEqual(list(User.objects.values_list('username', flat=True)), ['someone@example.org'])
		with mock.patch('builtins.input', return_value='yes'):
			self.call(flush=True)
		self.assertEqual(User.objects.count(), 40)

	def test_flush_on_empty_tables_doesnt_ask(self):
		with mock.patch('builtins.input') as prompt:
			self.call(flush=True)
		self.assertFalse(prompt.called)

	def test_negative_days(self):
		with self.assertRaisesRegex(CommandError, '--days'):
			self.call(days=-1)

class FirstRunTest(LivemgrTestCase):
	"""The install hook offers the sample data when it creates the admin account."""
	def migrate(self, answer=None, interactive=True, tty=True, verbosity=1):
		out = StringIO()
		with mock.patch('builtins.input', return_value=answer) as prompt, \
				mock.patch('sys.stdin') as stdin, mock.patch('sys.stdout', out):
			stdin.isatty.return_value = tty
			install(interactive=interactive, verbosity=verbosity)
		return prompt, out.getvalue()

	def test_yes(self):
		AuthUser.objects.filter(username='admin').delete()
		prompt, out = self.migrate('yes')
		self.assertTrue('load sample data' in prompt.call_args[0][0])
		self.assertTrue('Loaded 6 groups, 40 users, ' in out)
		self.assertTrue(AuthUser.objects.filter(username='admin').exists())
		self.assertEqual(User.objects.count(), 40)

	def test_no(self):
		AuthUser.objects.filter(username='admin').delete()
		prompt, out = self.migrate('no')
		self.assertTrue(prompt.called)
		self.assertTrue('manage.py load_sample_data --settings=settings_test' in out)
		self.assertFalse(User.objects.exists())

	def test_asks_again_on_other_answers(self):
		AuthUser.objects.filter(username='admin').delete()
		out = StringIO()
		with mock.patch('builtins.input', side_effect=['maybe', 'n']) as prompt, \
				mock.patch('sys.stdin') as stdin, mock.patch('sys.stdout', out):
			stdin.isatty.return_value = True
			install(interactive=True, verbosity=1)
		self.assertEqual(prompt.call_count, 2)
		self.assertTrue("Please answer 'yes' or 'no'." in out.getvalue())

	def test_noinput(self):
		AuthUser.objects.filter(username='admin').delete()
		prompt, out = self.migrate(interactive=False)
		self.assertFalse(prompt.called)
		self.assertTrue('manage.py load_sample_data' in out)
		self.assertFalse(User.objects.exists())

	def test_noinput_quiet(self):
		AuthUser.objects.filter(username='admin').delete()
		prompt, out = self.migrate(interactive=False, verbosity=0)
		self.assertEqual(out, '')

	def test_no_terminal(self):
		AuthUser.objects.filter(username='admin').delete()
		prompt, out = self.migrate('yes', tty=False)
		self.assertFalse(prompt.called)
		self.assertFalse(User.objects.exists())

	def test_only_on_the_first_run(self):
		prompt, out = self.migrate('yes')
		self.assertFalse(prompt.called)
		self.assertEqual(out, '')

	def test_not_over_existing_data(self):
		AuthUser.objects.filter(username='admin').delete()
		self.make_badword('darn')
		prompt, out = self.migrate('yes')
		self.assertFalse(prompt.called)
		self.assertFalse(User.objects.exists())
