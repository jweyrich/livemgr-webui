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
from webui.livemgr.tests.pdftext import read_pages, uncompressed

def conversation_ids(response):
	return [row.record.conversation_id for row in response.context['page'].object_list]

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
		self.assertEqual(response.content, b'Invalid search criteria')

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
		self.assertTrue(response.content.startswith(b'%PDF'))
		self.assertTrue(response.content.rstrip().endswith(b'%%EOF'))

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
		pages = response.content.count(b'/Type /Page') - response.content.count(b'/Type /Pages')
		self.assertTrue(pages > 1, pages)

	def test_not_found(self):
		response = self.client.get('/conversations/999999/report/pdf/')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, b'Conversation not found')

class ConversationReportContentTest(ConversationFixtures, LivemgrTestCase):
	"""
	What the PDF report shows. Each page has a 5-line header, the messages and
	a "Page x of y" footer.
	"""
	HEADER_LINES = 5

	def setUp(self):
		self.login_superuser()
		self.create_conversations()

	def report(self, conversation_id, **extra):
		with uncompressed():
			response = self.client.get('/conversations/%d/report/pdf/' % conversation_id, **extra)
		self.assertEqual(response.status_code, 200)
		return read_pages(response.content)

	def header(self, page):
		return [line.text for line in page[:self.HEADER_LINES]]

	def body(self, page):
		return [line.text for line in page[self.HEADER_LINES:-1]]

	def footer(self, page):
		return page[-1].text

	def color_of(self, page, text):
		colors = [color for line in page for fragment, color in line.fragments if fragment == text]
		self.assertTrue(colors, '%r not found' % text)
		return colors[0]

	def test_header(self):
		page, = self.report(self.first.id)
		self.assertEqual(self.header(page), [
			u'Conversation: #%d' % self.first.id,
			u'User: alice@example.com IP: 127.0.0.1',
			u'Buddy: bob@example.com',
			u'Started in: 05/17/2010 - 09:00:00 AM',
			u'Total messages: 3',
		])

	def test_messages(self):
		page, = self.report(self.first.id)
		self.assertEqual(self.body(page), [
			u'05/17/2010 09:00:00 AM - alice@example.com: hi bob',
			u'05/17/2010 09:00:05 AM - bob@example.com: hi alice', # inbound
			u'05/17/2010 09:00:09 AM - alice@example.com: [x] darn it', # filtered
		])

	def test_footer(self):
		page, = self.report(self.first.id)
		self.assertEqual(self.footer(page), u'Page 1 of 1')

	def test_colors(self):
		page, = self.report(self.first.id)
		self.assertEqual(self.color_of(page, u'alice@example.com'), '#7ca380')
		self.assertEqual(self.color_of(page, u'bob@example.com'), '#ad8282')
		self.assertEqual(self.color_of(page, u'[x]'), '#ff0000')
		self.assertEqual(self.color_of(page, u': hi bob'), '#000000')

	def test_user_and_buddy_colors_do_not_depend_on_who_spoke_first(self):
		conversation = self.make_conversation(self.alice)
		self.make_message(conversation.id, 'hi', at(2010, 5, 17, 9, 0, 0), inbound=True)
		self.make_message(conversation.id, 'hello', at(2010, 5, 17, 9, 0, 1))
		page, = self.report(conversation.id)
		self.assertEqual(self.color_of(page, u'alice@example.com'), '#7ca380')
		self.assertEqual(self.color_of(page, u'bob@example.com'), '#ad8282')

	def test_content_is_escaped_and_encoded(self):
		conversation = self.make_conversation(self.alice)
		self.make_message(conversation.id, u'olá <b>bold</b> & co (x) \\o/', at(2010, 5, 17, 9, 0, 0))
		page, = self.report(conversation.id)
		self.assertEqual(self.body(page),
			[u'05/17/2010 09:00:00 AM - alice@example.com: olá <b>bold</b> & co (x) \\o/'])

	def test_message_types(self):
		conversation = self.make_conversation(self.alice)
		labels = [
			(Message.Type.FILE, '2048 holiday photos.zip', u'File transfer: holiday photos.zip (2.0 KB)'),
			(Message.Type.WEBCAM, '', u'Video Call'),
			(Message.Type.REMOTEDESKTOP, '', u'Remote Desktop'),
			(Message.Type.APPLICATION, '', u'MSN Activity'),
			(Message.Type.EMOTICON, '', u'Custom emoticon'),
			(Message.Type.INK, '', u'Handwriting'),
			(Message.Type.NUDGE, '', u'Nudge'),
			(Message.Type.WINK, '', u'Wink'),
			(Message.Type.VOICECLIP, '', u'Voice clip'),
			(Message.Type.GAMES, '', u'MSN Game'),
			(Message.Type.PHOTO, '', u'Photo sharing'),
		]
		for second, (message_type, content, label) in enumerate(labels):
			self.make_message(conversation.id, content, at(2010, 5, 17, 9, 0, second), type=message_type)
		page, = self.report(conversation.id)
		self.assertEqual(self.body(page), [
			u'05/17/2010 09:00:%02d AM - alice@example.com: %s' % (second, label)
			for second, (message_type, content, label) in enumerate(labels)
		])

	def test_several_pages(self):
		conversation = self.make_conversation(self.alice)
		for i in range(120):
			self.make_message(conversation.id, u'message %03d' % i, at(2010, 5, 17, 10, i // 60, i % 60))
		pages = self.report(conversation.id)
		self.assertTrue(len(pages) > 1, len(pages))
		first_header = self.header(pages[0])
		self.assertEqual(first_header[-1], u'Total messages: 120')
		for number, page in enumerate(pages, 1):
			self.assertEqual(self.header(page), first_header) # repeated on every page
			self.assertEqual(self.footer(page), u'Page %d of %d' % (number, len(pages)))
		contents = [line.rsplit(': ', 1)[1] for page in pages for line in self.body(page)]
		self.assertEqual(contents, [u'message %03d' % i for i in range(120)])

	def test_long_message_wraps(self):
		conversation = self.make_conversation(self.alice)
		words = u' '.join(u'word%02d' % i for i in range(60))
		self.make_message(conversation.id, words, at(2010, 5, 17, 9, 0, 0))
		page, = self.report(conversation.id)
		body = self.body(page)
		self.assertTrue(len(body) > 1, body)
		self.assertEqual(u' '.join(line.strip() for line in body),
			u'05/17/2010 09:00:00 AM - alice@example.com: ' + words)

	def test_translated(self):
		page, = self.report(self.first.id, HTTP_ACCEPT_LANGUAGE='pt-br')
		self.assertEqual(self.header(page), [
			u'Conversa: #%d' % self.first.id,
			u'Usuário: alice@example.com IP: 127.0.0.1',
			u'Contato: bob@example.com',
			u'Iniciada em: 17/05/2010 - 09:00:00 AM',
			u'Total de mensagens: 3',
		])
		self.assertEqual(self.body(page)[0], u'17/05/2010 09:00:00 AM - alice@example.com: hi bob')
		self.assertEqual(self.footer(page), u'Página 1 de 1')

	def test_unsupported_message_types_crash(self):
		# KNOWN BUG, pinned on purpose: types without a formatter (unknown,
		# typing, caps) raise TypeError instead of being skipped.
		for message_type in (Message.Type.UNKNOWN, Message.Type.TYPING, Message.Type.CAPS):
			conversation = self.make_conversation(self.alice)
			self.make_message(conversation.id, 'x', type=message_type)
			self.assertRaises(TypeError, self.client.get,
				'/conversations/%d/report/pdf/' % conversation.id)
