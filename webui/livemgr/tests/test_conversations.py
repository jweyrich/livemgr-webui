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

from webui.livemgr.models import Message
from webui.livemgr.tests.base import LivemgrTestCase, at

def conversation_ids(response):
	return [row.data.conversation_id for row in response.context['page'].object_list]

class ConversationFixtures(object):
	def create_conversations(self):
		self.alice = self.make_user('alice@example.com')
		self.first = self.make_conversation(self.alice)
		self.make_message(self.first.id, 'hi bob', at(2010, 5, 17, 9, 0, 0))
		self.make_message(self.first.id, 'hi alice', at(2010, 5, 17, 9, 0, 5), inbound=True)
		self.make_message(self.first.id, 'darn it', at(2010, 5, 17, 9, 0, 9), filtered=True)
		self.second = self.make_conversation(self.alice)
		self.make_message(self.second.id, 'hello carol', at(2010, 5, 20, 15, 30, 0),
			remoteim='carol@example.org')
		self.make_message(self.second.id, 'bye carol', at(2010, 5, 20, 15, 31, 0),
			remoteim='carol@example.org')

class ConversationListTest(ConversationFixtures, LivemgrTestCase):
	def setUp(self):
		self.account = self.login_superuser()
		self.create_conversations()

	def test_one_row_per_conversation(self):
		response = self.client.get('/conversations/')
		self.assertEqual(sorted(conversation_ids(response)), sorted([self.first.id, self.second.id]))
		self.assertEqual(response.context['page'].paginator.count, 2)
		self.assertContains(response, '05/20/2010 - 03:3') # MessageTable.render_timestamp

	def test_pagination_counts_conversations(self):
		for i in range(11):
			conversation = self.make_conversation(self.alice)
			self.make_message(conversation.id)
			self.make_message(conversation.id)
		response = self.client.get('/conversations/')
		self.assertEqual(response.context['page'].paginator.count, 13)
		self.assertEqual(response.context['page'].paginator.num_pages, 2)
		self.assertEqual(len(conversation_ids(response)), 10)
		self.assertEqual(len(conversation_ids(self.client.get('/conversations/?page=2'))), 3)

	def test_search_by_content(self):
		response = self.client.post('/conversations/', {'message': 'CAROL'})
		self.assertEqual(conversation_ids(response), [self.second.id])

	def test_search_by_participants(self):
		self.assertEqual(conversation_ids(self.client.post('/conversations/', {'remoteim': 'example.org'})),
			[self.second.id])
		self.assertEqual(len(conversation_ids(self.client.post('/conversations/', {'localim': 'alice'}))), 2)

	def test_search_filtered(self):
		self.assertEqual(conversation_ids(self.client.post('/conversations/', {'filtered': 'on'})),
			[self.first.id])

	def test_search_by_date(self):
		post = lambda **data: conversation_ids(self.client.post('/conversations/', data))
		self.assertEqual(post(from_date='05/18/2010'), [self.second.id])
		self.assertEqual(post(to_date='05/17/2010'), [self.first.id]) # inclusive, whole day
		self.assertEqual(post(from_date='05/18/2010', to_date='05/19/2010'), [])
		self.assertEqual(post(from_date='2010-05-20'), [self.second.id])

	def test_invalid_date(self):
		response = self.client.post('/conversations/', {'from_date': '31/31/2010'})
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, 'Invalid search criteria')

	def test_change_page_size(self):
		self.client.post('/conversations/', {'per_page': '40'})
		self.assertEqual(self.profile_of(self.account).per_page_conversations, 40)

class ConversationShowTest(ConversationFixtures, LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.create_conversations()

	def test_show(self):
		response = self.client.get('/conversations/%d/' % self.first.id)
		self.assertTemplateUsed(response, 'conversations/show.html')
		self.assertEqual([m.content for m in response.context['messages']],
			['hi bob', 'hi alice', 'darn it'])
		first = response.context['first_message']
		self.assertEqual(first.clientip, '127.0.0.1')
		self.assertContains(response, '<b>IP</b>: 127.0.0.1')
		self.assertContains(response, '3 messages')
		self.assertContains(response, 'This message was filtered.', count=1)
		self.assertContains(response, '/conversations/%d/report/pdf/' % self.first.id)

	def test_participants_get_distinct_colors(self):
		response = self.client.get('/conversations/%d/' % self.first.id)
		self.assertContains(response, '<span style="color:#7ca380;">alice@example.com</span>')
		self.assertContains(response, '<span style="color:#ad8282;">bob@example.com</span>')

	def test_message_types(self):
		conversation = self.make_conversation(self.alice)
		self.make_message(conversation.id, '2048 holiday photos.zip', type=Message.Type.FILE)
		self.make_message(conversation.id, '', type=Message.Type.NUDGE)
		self.make_message(conversation.id, '', type=Message.Type.WEBCAM)
		self.make_message(conversation.id, '<script>x</script>')
		response = self.client.get('/conversations/%d/' % conversation.id)
		self.assertContains(response, 'File transfer')
		self.assertContains(response, 'holiday photos.zip')
		self.assertContains(response, '<b>Nudge</b>')
		self.assertContains(response, '<b>Video Call</b>')
		self.assertContains(response, '&lt;script&gt;x&lt;/script&gt;')
		self.assertNotContains(response, '<script>x</script>')

	def test_not_found(self):
		self.assertEqual(self.client.get('/conversations/999999/').status_code, 404)

class ConversationReportTest(ConversationFixtures, LivemgrTestCase):
	def setUp(self):
		self.login_superuser()
		self.create_conversations()

	def test_pdf(self):
		response = self.client.get('/conversations/%d/report/pdf/' % self.first.id)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'application/pdf')
		self.assertEqual(response['Content-Disposition'], 'attachment; filename=report-%d.pdf' % self.first.id)
		self.assertTrue(response.content.startswith('%PDF'))
		self.assertTrue(response.content.rstrip().endswith('%%EOF'))

	def test_pdf_with_every_supported_type_and_several_pages(self):
		conversation = self.make_conversation(self.alice)
		supported = [t for t, label in Message.CHOICES_TYPES if t not in
			(Message.Type.UNKNOWN, Message.Type.TYPING, Message.Type.CAPS)]
		for i in range(10):
			for message_type in supported:
				content = '1024 file.txt' if message_type == Message.Type.FILE else u'olá <b>%d</b> & co' % i
				self.make_message(conversation.id, content, type=message_type, inbound=bool(i % 2))
		response = self.client.get('/conversations/%d/report/pdf/' % conversation.id)
		self.assertEqual(response.status_code, 200)
		pages = response.content.count('/Type /Page') - response.content.count('/Type /Pages')
		self.assertTrue(pages > 1, pages)

	def test_not_found(self):
		response = self.client.get('/conversations/999999/report/pdf/')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, 'Conversation not found')
