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

"""
	Sample data to try out the web UI.

	Fills the tables the backend owns (see bootstrap/db/create_tables.sql) with
	a fictitious company, Example Corp, that monitors its employees on MSN:
	user groups and their rules, users and their buddies, ACLs, badwords, and
	some months of conversations that end at the current time, so the dashboard
	has data for today, this week, this month and this year.

	The data agrees with itself, as if the backend had captured it:
	- Only the groups with the 'Conversation history' rule have conversations.
	- A conversation never has a feature (file transfer, webcam...) that the
	  group's rules block.
	- Nobody talks to a contact that an ACL blocks.
	- A message is filtered when the group has the 'Badword filtering' rule and
	  the message has an enabled badword.
	- Users who aren't offline logged in today, and only they have active
	  conversations.

	Run it with `python webui/manage.py load_sample_data`.
"""

from datetime import datetime, time, timedelta
from django.db import connection
from fnmatch import fnmatchcase
from webui.livemgr.models import Acl, Badword, Buddy, Conversation, GroupRule, \
	Message, User, UserGroup
from webui.livemgr.utils.formatters import ip_str_to_long
import math
import random
import re
import unicodedata

DOMAIN = 'example.com'
# How many days of conversations to create, besides today's
DAYS = 90
SEED = 2010

# The tables load() fills, which bootstrap/db/create_tables.sql creates
TABLES = ('usergroups', 'rules', 'grouprules', 'users', 'buddies', 'acls',
	'badwords', 'conversations', 'messages')

# Rules, as bootstrap/db/create_tables.sql numbers them
RULE_HISTORY = 1
RULE_DISCLAIMER = 2
RULE_BADWORDS = 14
# The rule that blocks each feature
BLOCKING_RULES = {
	Message.Type.FILE: 3,
	Message.Type.WEBCAM: 5,
	Message.Type.REMOTEDESKTOP: 6,
	Message.Type.APPLICATION: 7,
	Message.Type.EMOTICON: 8,
	Message.Type.INK: 9,
	Message.Type.NUDGE: 10,
	Message.Type.WINK: 11,
	Message.Type.VOICECLIP: 12,
	Message.Type.GAMES: 15,
	Message.Type.PHOTO: 16,
}

#
# Groups
#
GUEST = 'guest' # Built-in: self-registered users land here
ENGINEERING = 'Engineering'
SALES = 'Sales'
SUPPORT = 'Customer Support'
FINANCE = 'Finance'
EXECUTIVES = 'Executives'
INTERNS = 'Interns'

GROUPS = (
	# name, active, description, rules
	(ENGINEERING, True, 'Developers and IT staff',
		(1, 2, 11, 14, 15)),
	(SALES, True, 'Account managers and pre-sales',
		(1, 2, 9, 11, 14, 15)),
	(SUPPORT, True, 'Help desk. They talk to customers all day, so most features are blocked',
		(1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16)),
	(FINANCE, True, 'Accounting, payroll and purchasing',
		(1, 2, 3, 13, 14, 15, 16)),
	(EXECUTIVES, True, 'Board and directors. Their conversations are not saved',
		(2, 13)),
	(INTERNS, False, 'Summer interns. Disabled until the next program starts',
		(1, 2, 3, 5, 6, 7, 12, 14, 15, 16)),
)
GUEST_RULES = (1, 2, 3, 14)

#
# Users
#
EMPLOYEES = (
	# first name, last name, group, conversations per weekday
	('Alice', 'Johnson', ENGINEERING, 1.2),
	('Bruno', 'Carvalho', ENGINEERING, 0.8),
	('Wei', 'Chen', ENGINEERING, 0.5),
	('Priya', 'Natarajan', ENGINEERING, 1.0),
	('Marcus', 'Oliveira', ENGINEERING, 0.6),
	('Sofia', 'Rossi', ENGINEERING, 0.9),
	('Tomás', 'Herrera', ENGINEERING, 0.4),
	('Hannah', 'Becker', ENGINEERING, 0.7),
	('Kenji', 'Watanabe', ENGINEERING, 0.3),
	('Laura', 'Mendes', SALES, 2.0),
	('Daniel', 'Kowalski', SALES, 1.6),
	('Fernanda', 'Lima', SALES, 1.4),
	('Omar', 'Haddad', SALES, 1.1),
	('Grace', 'Okafor', SALES, 1.3),
	('Lucas', 'Martin', SALES, 0.9),
	('Isabela', 'Rocha', SALES, 1.0),
	('Peter', 'Lindqvist', SALES, 0.8),
	('Mariana', 'Souza', SUPPORT, 1.8),
	('Jake', 'Turner', SUPPORT, 1.5),
	('Aisha', 'Bello', SUPPORT, 1.2),
	('Rafael', 'Costa', SUPPORT, 1.0),
	('Emily', 'Clarke', SUPPORT, 1.1),
	('Nikolai', 'Petrov', SUPPORT, 0.7),
	('Camila', 'Duarte', SUPPORT, 0.9),
	('Sean', 'Murphy', SUPPORT, 0.6),
	('Helen', 'Fischer', FINANCE, 0.6),
	('Gustavo', 'Pereira', FINANCE, 0.5),
	('Olivia', 'Bennett', FINANCE, 0.4),
	('Raj', 'Patel', FINANCE, 0.7),
	('Zoë', 'Laurent', FINANCE, 0.5),
	('Richard', 'Hale', EXECUTIVES, 0.5),
	('Beatriz', 'Andrade', EXECUTIVES, 0.4),
	('Victor', 'Novak', EXECUTIVES, 0.3),
	('Leo', 'Santos', INTERNS, 1.0),
	('Mia', 'Kim', INTERNS, 1.2),
	('Noah', 'Schmidt', INTERNS, 0.8),
	# Self-registered: the backend creates them without a name
	('Ana', 'Ribeiro', GUEST, 0.4),
	('Paulo', 'Vieira', GUEST, 0.3),
	('', 'it.helpdesk', GUEST, 0.2),
	('', 'temp01', GUEST, 0.2),
)
# Users who left the company: the administrator disabled them
DISABLED = ('peter.lindqvist', 'noah.schmidt', 'temp01')
# Registered by the administrator, but never logged in
NEVER_LOGGED_IN = ('olivia.bennett',)
# Display names people chose, instead of their full names
DISPLAY_NAMES = {
	'bruno.carvalho': 'Bruno | Engineering',
	'sofia.rossi': '~ Sofia ~',
	'laura.mendes': 'Laura Mendes - Sales',
	'jake.turner': 'Jake (help desk)',
	'zoe.laurent': 'Zoë',
	'mia.kim': 'Mia :)',
	'paulo.vieira': 'paulo',
	'it.helpdesk': '',
	'temp01': '',
}
PERSONAL_MESSAGES = (
	'In a meeting until 3pm',
	'Working from home today',
	'Coffee first',
	'On call this week',
	'Back on Monday',
	'Quarter close, please call instead',
	'Vacation in 5 days!',
	'♪ Listening to the radio',
	'Deadline Friday',
	'Go team!',
)
# Weights of each status for users who are online
ONLINE_STATUSES = ('NLN',) * 6 + ('BSY', 'BSY', 'AWY', 'AWY', 'IDL', 'BRB',
	'PHN', 'LUN', 'HDN')

#
# Contacts outside the company
#
COWORKER = 'coworker'
CUSTOMER = 'customer'
SUPPLIER = 'supplier'
PERSONAL = 'personal'
SPAM = 'spam'

CONTACTS = (
	# username, display name, first name, kind
	('mark.evans@example.org', 'Mark Evans', 'Mark', CUSTOMER),
	('purchasing@example.org', 'Purchasing (Carol)', 'Carol', CUSTOMER),
	('julia.weber@example.org', 'Julia Weber', 'Julia', CUSTOMER),
	('tom.baker@example.org', 'Tom Baker', 'Tom', CUSTOMER),
	('ana.lopez@example.org', 'Ana López', 'Ana', CUSTOMER),
	('kevin.ng@example.org', 'Kevin Ng', 'Kevin', CUSTOMER),
	('orders@example.net', 'Orders desk (Rita)', 'Rita', SUPPLIER),
	('paul.meyer@example.net', 'Paul Meyer', 'Paul', SUPPLIER),
	('sandra.ito@example.net', 'Sandra Ito', 'Sandra', SUPPLIER),
	('logistics@example.net', 'Logistics - Example Net', 'Igor', SUPPLIER),
	('jen.f@hotmail.com', 'Jen', 'Jen', PERSONAL),
	('mike.the.man@hotmail.com', 'Mike ~ the man ~', 'Mike', PERSONAL),
	('lu.martins@hotmail.com', 'Lu', 'Lu', PERSONAL),
	('dave_r@live.com', 'Dave R.', 'Dave', PERSONAL),
	('carla.b@live.com', 'Carla', 'Carla', PERSONAL),
	('the.parkers@msn.com', 'The Parkers', 'Sue', PERSONAL),
	('nina.k@msn.com', 'Nina', 'Nina', PERSONAL),
	('gabi.costa@hotmail.com', 'Gabi :)', 'Gabi', PERSONAL),
	('mom.and.dad@msn.com', 'Mom & Dad', 'Mom', PERSONAL),
	('free.prizes.4u@hotmail.com', 'FREE PRIZES - click here', '', SPAM),
	('recruiter.jobs@live.com', 'Tech Recruiter', '', SPAM),
)
EXTERNAL_PSMS = ('', '', '', 'Busy week', 'Out of office until Monday',
	'Happy Friday!', 'Call me on the mobile', 'At the airport')
# How many contacts of each kind a member of each group has: (min, max)
BUDDIES = {
	ENGINEERING: {SUPPLIER: (0, 2), PERSONAL: (1, 4)},
	SALES: {CUSTOMER: (3, 6), PERSONAL: (1, 3)},
	SUPPORT: {CUSTOMER: (3, 6), PERSONAL: (1, 2)},
	FINANCE: {SUPPLIER: (2, 4), PERSONAL: (1, 3)},
	EXECUTIVES: {CUSTOMER: (1, 3), SUPPLIER: (0, 1), PERSONAL: (1, 3)},
	INTERNS: {PERSONAL: (2, 4)},
	GUEST: {PERSONAL: (0, 2)},
}
# How often each kind of buddy is the one people talk to
CHAT_WEIGHTS = {COWORKER: 3, CUSTOMER: 4, SUPPLIER: 2, PERSONAL: 1}

#
# ACLs
#
ACLS = [
	# user, buddy, action
	('*@' + DOMAIN, '*@' + DOMAIN, Acl.ACTION_ALLOW),
	('*@' + DOMAIN, '*@example.org', Acl.ACTION_ALLOW),
	('*@' + DOMAIN, '*@example.net', Acl.ACTION_ALLOW),
	('*@' + DOMAIN, 'free.prizes.4u@hotmail.com', Acl.ACTION_BLOCK),
	('daniel.kowalski@' + DOMAIN, 'recruiter.jobs@live.com', Acl.ACTION_BLOCK),
	('richard.hale@' + DOMAIN, 'recruiter.jobs@live.com', Acl.ACTION_BLOCK),
]
# Interns can't talk to customers
ACLS += [('%s@%s' % (u, DOMAIN), '*@example.org', Acl.ACTION_BLOCK)
	for u in ('leo.santos', 'mia.kim', 'noah.schmidt')]
# Customer Support can't talk to personal accounts. See also _create_acls().
PERSONAL_DOMAINS = ('*@hotmail.com', '*@live.com', '*@msn.com')

#
# Badwords
#
BADWORDS = (
	# badword, regex, enabled
	('damn', False, True),
	('crap', False, True),
	('idiot', False, True),
	('stupid', False, True),
	('sucks', False, True),
	('wtf', False, True),
	('hell', False, False),
	('confidential', False, True),
	('layoff', False, True),
	('salary', False, True),
	('Globex', False, True),
	('torrent', False, True),
	('poker', False, True),
	('casino', False, False),
	# Credit card numbers
	(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b', True, True),
	# Social security numbers
	(r'\b\d{3}-\d{2}-\d{4}\b', True, True),
	# Passwords
	(r'\bpass(word|wd)?\s*[:=]', True, True),
	(r'\bv[i1!]agra\b', True, False),
)

#
# Conversations
#
# Each line starts with who sends it: L, the monitored user, or R, the buddy.
# {me} and {you} are their first names. '!feature' lines are not text
# messages: '!file' is followed by the file's size and name.
EVENTS = {
	'file': Message.Type.FILE,
	'webcam': Message.Type.WEBCAM,
	'remotedesktop': Message.Type.REMOTEDESKTOP,
	'application': Message.Type.APPLICATION,
	'emoticon': Message.Type.EMOTICON,
	'ink': Message.Type.INK,
	'nudge': Message.Type.NUDGE,
	'wink': Message.Type.WINK,
	'voiceclip': Message.Type.VOICECLIP,
	'games': Message.Type.GAMES,
	'photo': Message.Type.PHOTO,
}

SCRIPTS = (
	# kind, groups (None for any), lines
	(COWORKER, None, """
		L Hi {you}, are you joining the 2pm meeting?
		R Hey {me}! Wasn't it moved to 3?
		L Oh, really? Nobody told me
		R Check your inbox, it was updated this morning
		L Found it. Thanks!
		R np, see you there
	"""),
	(COWORKER, None, """
		L {you}, do you have the latest numbers for the monthly report?
		R Almost done, just double-checking a few figures
		R !file 482304 monthly report - draft.xlsx
		L Got it, thanks. Can I share it with the team already?
		R Better wait until I finish the review, it should be ready by the end of the day
		L ok, I'll wait then
	"""),
	(COWORKER, None, """
		R lunch?
		L sure, where?
		R that new place around the corner
		L the Italian one? I heard it's good
		R yep. 12:30 at the lobby?
		L deal
	"""),
	(COWORKER, None, """
		L is the printer on the 3rd floor working for you?
		R nope, it's been jammed since yesterday
		L damn, I need to print the contracts before 4
		R try the one next to the kitchen
		L thanks, will do
	"""),
	(COWORKER, None, """
		R Hi {me}, I'm off next week. Could you cover my tickets?
		L Sure, anything urgent?
		R Just two follow-ups, I'll leave notes in each ticket
		L ok, no problem
		R You're the best! I'll bring you something from the beach
		L haha, deal
		R !wink
	"""),
	(COWORKER, None, """
		L !nudge
		L coffee?
		R give me 5 minutes
		L ok, meet you at the kitchen
	"""),
	(COWORKER, None, """
		L quick question: where do I find the guest wifi details?
		R on the board at the reception
		L ah, thanks
	"""),
	(COWORKER, None, """
		R did you hear the rumors about a layoff?
		L what? where did you hear that?
		R someone mentioned it at lunch
		L I doubt it, we just hired 3 people
		R I hope you're right
		L let's not spread it, ok? if it's true it's confidential
		R sure
	"""),
	(COWORKER, None, """
		L this new expense system is crap
		R haha, what happened?
		L it lost my receipts. twice.
		R wtf, mine worked fine
		L lucky you. I'll call the help desk
		R good luck!
	"""),
	(COWORKER, None, """
		R hey {me}, can you log in to the reporting tool for me? my account is locked
		L you shouldn't use my account...
		R just this once, please
		L fine. password: Sunshine#42 and don't tell anyone
		R thanks! I owe you one
		L and ask IT to unlock yours today
	"""),
	(COWORKER, None, """
		R {me}, can you help me with a spreadsheet formula?
		L sure, what's the problem?
		R it keeps showing #REF!
		L let me take a look
		L !remotedesktop
		L there you go, one of the columns was deleted
		R wow, thanks!
	"""),
	(COWORKER, None, """
		L Morning {you}. Can we do a quick status call?
		R sure, give me a sec to find my headset
		L !webcam
		R That was quick, thanks
		L I'll send the minutes later today
	"""),
	(COWORKER, None, """
		R there's cake in the kitchen, it's somebody's birthday
		L !emoticon
		L on my way!
	"""),
	(COWORKER, None, """
		L !ink
		R haha, is that supposed to be me?
		L it's art, don't judge
		R lol
	"""),
	(COWORKER, None, """
		R want to plan the offsite agenda together?
		L sure, let's use the shared whiteboard
		L !application
		R looks good, I'll send it to everyone
	"""),
	(COWORKER, None, """
		R did you get the email about the salary review?
		L yes, the meetings start next week
		R fingers crossed
		L !emoticon
	"""),
	(COWORKER, None, """
		L leaving now, see you tomorrow
		R bye, have a good evening
	"""),
	(COWORKER, None, """
		R Hi {me}! I'm the new hire, they told me you could help me get set up
		L Welcome! Sure, what do you need?
		R I still don't have access to the shared drive
		L You need to open a ticket with IT, I'll send you the link
		L https://helpdesk.example.com/new
		R Thanks! And where do people usually have lunch?
		L There's a cafeteria on the ground floor, but most of us go out
		L We usually leave around 12:15, you're welcome to join
		R That would be great
		R One more thing: who approves vacation requests?
		L Your manager, through the HR portal
		R Got it. Thanks for all the help!
		L Anytime :)
	"""),
	(COWORKER, (ENGINEERING,), """
		R the staging build is failing again
		L which test?
		R the integration tests for the billing module
		L ugh, probably my change. looking at it now
		L fixed, it was a missing migration
		R thanks, triggering a new build
		R green now
	"""),
	(COWORKER, (ENGINEERING,), """
		L can you review my pull request when you have a minute?
		R sure, link?
		L it's the one about the login timeout
		R left a few comments, mostly naming
		L thanks, I'll fix them after lunch
	"""),
	(COWORKER, (SALES, EXECUTIVES), """
		L how's the pipeline looking for this quarter?
		R good, 3 deals should close this month
		L great, the board will be happy
		R don't jinx it!
	"""),
	(COWORKER, (FINANCE,), """
		R {me}, the auditors want the bank statements by Wednesday
		L all of them? since January?
		R yes, all accounts
		L !file 3145728 bank statements.zip
		L here they are, the password for the zip is in your email
		R thanks, that saves me a lot of time
	"""),
	(CUSTOMER, None, """
		R Hello {me}, any news about our order?
		L Hi {you}! It shipped yesterday, you should receive it by Thursday
		R Great, can you send me the tracking number?
		L Sure: BR482915736
		R Thanks a lot
		L You're welcome, let me know if you need anything else
	"""),
	(CUSTOMER, None, """
		R Hi {me}, could you send me a quote for 50 more licenses?
		L Of course. Same terms as the last order?
		R Yes, please
		L !file 96256 quote 2231 - 50 licenses.pdf
		L Here it is. It's valid for 30 days
		R Perfect, I'll forward it to our purchasing team
	"""),
	(CUSTOMER, None, """
		R Hi, I'd like to pay the invoice by credit card
		L Sure, our finance team will send you a secure link
		R Can't I just give it to you here? It's 4111 1111 1111 1111, exp 12/29
		L Please don't share card numbers over chat, it's not safe
		L I'll ask finance to send you the link today
		R Oh, sorry about that. Thanks
	"""),
	(CUSTOMER, None, """
		R your product sucks, the export crashed again!
		L I'm sorry to hear that, {you}. Which version are you using?
		R the one you sent last month
		L Could you send me the error message?
		R !file 183420 error screenshot.png
		L Thanks. I've opened a ticket with our engineers, I'll keep you posted
		R please hurry, we have a deadline on Friday
	"""),
	(CUSTOMER, None, """
		L Hi {you}, ready for the demo?
		R Yes, starting the call
		L !webcam
		R Very impressive. Can you send me the slides?
		L !file 2318336 product demo.pptx
		R Thanks, I'll talk to my team and get back to you
	"""),
	(CUSTOMER, None, """
		R honestly, Globex offered us a better price
		L I understand. What if we include the training at no cost?
		R that could work. send me a new proposal?
		L I'll have it ready by tomorrow morning
	"""),
	(CUSTOMER, None, """
		L Hi {you}, do you have some time next week to talk about the training?
		R Hi {me}! Tuesday or Wednesday morning works for me
		L Wednesday at 10?
		R Perfect. How many people can attend?
		L Up to 12 per session
		R We'll have 9, I'll send you the names
		L Great, I'll book the room
	"""),
	(CUSTOMER, None, """
		R {me}, our team has been asking for a feature
		L Sure, tell me
		R They'd like to schedule the reports to run every Monday morning
		L That's a good one. Today you can only run them by hand, right?
		R Exactly. We waste an hour every week on it
		L I'll write it up for the product team. Can I mention your company as interested?
		R Of course
		L Thanks, I'll let you know when it's on the roadmap
		R Thanks, have a good day
	"""),
	(CUSTOMER, None, """
		R Good morning! Did you get my email about the renewal?
		L Good morning {you}! Yes, I'm preparing the paperwork
		R Will the price stay the same?
		L Yes, for another 12 months
		R Excellent
		R Can we add two more users to the contract?
		L Sure, I'll include them. You'll get the new contract by Friday
		R Thank you
		L !file 248112 renewal contract.pdf
		L Here's the draft in the meantime
		R Great, I'll forward it to our lawyers
	"""),
	(CUSTOMER, None, """
		R Hi, I can't log in since this morning
		L Hi {you}, let me check... Your account was locked after 3 failed attempts
		L I've unlocked it, please try again
		R It worked, thank you!
	"""),
	(SUPPLIER, None, """
		L Hi {you}, the toner cartridges haven't arrived yet
		R Hi {me}, sorry, there was a delay at the warehouse
		R They'll be delivered tomorrow before noon
		L ok, thanks for letting me know
	"""),
	(SUPPLIER, None, """
		L Could you send me your new price list?
		R Sure
		R !file 734003 price list.pdf
		L Thanks! Prices went up 8%?
		R Yes, because of shipping costs. I can give you 3% off orders above 100 units
		L I'll check with my manager
	"""),
	(SUPPLIER, None, """
		R The new contract draft is ready. It's confidential until signed
		R !file 1210880 supply agreement - draft v3.docx
		L Received, our legal team will review it this week
		R Thanks
	"""),
	(SUPPLIER, None, """
		R Hi {me}, invoice 5590 is 10 days overdue
		L Let me check... it was approved yesterday, the payment goes out on Friday
		R Great, thanks
		L Sorry for the delay
	"""),
	(PERSONAL, None, """
		R what do you want for dinner?
		L pizza?
		R again? :P
		L ok ok, you choose
		R sushi then
		L deal, I'll pick it up on the way home
	"""),
	(PERSONAL, None, """
		R did you watch the game last night?
		L yes! what a goal in the last minute
		R the referee was an idiot though
		L haha, he was
		R tickets for Sunday?
		L can't, my in-laws are visiting
	"""),
	(PERSONAL, None, """
		R don't forget the party on Saturday!
		L of course not. what should I bring?
		R just yourself. and maybe some drinks
		L !emoticon
		R see you there
	"""),
	(PERSONAL, None, """
		R we're back from the trip!
		R !photo
		L wow, beautiful. where is that?
		R a small beach up north, I'll send you the location
		L we need to go there next summer
	"""),
	(PERSONAL, None, """
		R !voiceclip
		L haha, I'm at work, I can't listen now
		R it's just me singing happy birthday
		L thank you!! I'll listen later
	"""),
	(PERSONAL, None, """
		R can you pick up the kids at school today?
		L what time?
		R 5:30
		L ok, I'll leave a bit earlier
		R thank you! love you
		L love you too
	"""),
	(PERSONAL, None, """
		R poker night on Friday?
		L count me in
		R bring money, last time you were lucky
		L it's called skill ;)
	"""),
	(PERSONAL, None, """
		R bored?
		L a bit, waiting for a report
		R let's play a quick round
		R !games
		L you win again. back to work now
		R lol
	"""),
	(PERSONAL, None, """
		R found a torrent of the new season
		L not on the office network!
		R haha ok, I'll bring it on a usb stick
		L better
	"""),
)

class Contact(object):
	"""Someone a user can have as a buddy."""
	def __init__(self, username, displayname, first, kind, psm='', status='FLN'):
		self.username = username
		self.displayname = displayname
		self.first = first
		self.kind = kind
		self.psm = psm
		self.status = status

class Person(object):
	"""A monitored user, before it's saved."""
	def __init__(self, first, last, group, chattiness):
		login = ascii_lower('%s.%s' % (first, last) if first else last)
		self.username = '%s@%s' % (login, DOMAIN)
		self.first = first or login
		self.displayname = DISPLAY_NAMES.get(login, ('%s %s' % (first, last)).strip())
		self.group = group
		self.chattiness = chattiness
		self.isenabled = login not in DISABLED
		self.never_logged_in = login in NEVER_LOGGED_IN
		self.psm = ''
		self.status = 'FLN'
		self.last_day = None # Days ago they last logged in
		self.lastlogin = None
		self.ip = None
		self.buddies = [] # Contacts
		self.model = None # The saved User

	def as_contact(self):
		# Buddies see invisible users as offline
		status = 'FLN' if self.status == 'HDN' else self.status
		return Contact(self.username, self.displayname, self.first, COWORKER,
			self.psm, status)

class Line(object):
	def __init__(self, inbound, type, content):
		self.inbound = inbound
		self.type = type
		self.content = content

def ascii_lower(text):
	return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()

def parse_script(text):
	lines = []
	for line in text.strip().splitlines():
		who, content = line.strip().split(' ', 1)
		inbound = who == 'R'
		if content.startswith('!'):
			name, _, content = (content[1:] + ' ').partition(' ')
			lines.append(Line(inbound, EVENTS[name], content.strip()))
		else:
			lines.append(Line(inbound, Message.Type.MSG, content))
	return lines

def badword_patterns(badwords=BADWORDS):
	"""The patterns of the enabled badwords: words match whole words."""
	return [re.compile(word if isregex else r'\b%s\b' % re.escape(word), re.IGNORECASE)
		for (word, isregex, isenabled) in badwords if isenabled]

def format_counts(counts):
	"""'40 users, 7 groups' from [('users', 40), ('groups', 7)]"""
	return ', '.join('%d %s' % (count, name) for (name, count) in counts)

def tables_exist():
	return set(TABLES) <= set(connection.introspection.table_names())

def existing_rows():
	"""
	The number of rows load() would add to, by table, of the tables that
	already have some. The built-in group and the rules don't count.
	"""
	counts = (
		('groups', UserGroup.objects.filter(isbuiltin=False).count()),
		('group rules', GroupRule.objects.count()),
		('users', User.objects.count()),
		('buddies', Buddy.objects.count()),
		('acls', Acl.objects.count()),
		('badwords', Badword.objects.count()),
		('conversations', Conversation.objects.count()),
		('messages', Message.objects.count()),
	)
	return [(name, count) for (name, count) in counts if count]

def flush():
	"""
	Deletes what load() creates, and whatever else is in its tables: all the
	users, groups (except the built-in one), ACLs, badwords and conversations.
	"""
	cursor = connection.cursor()
	for statement in (
			'DELETE FROM messages',
			'DELETE FROM conversations',
			'DELETE FROM buddies',
			'DELETE FROM users',
			'DELETE FROM grouprules',
			'DELETE FROM usergroups WHERE isbuiltin = 0',
			'DELETE FROM acls',
			'DELETE FROM badwords'):
		cursor.execute(statement)

def load(days=DAYS, seed=SEED, now=None):
	"""
	Creates the sample data, with conversations from `days` days ago until
	`now`. The same seed creates the same data, relative to `now`.
	Returns the number of rows created, by table.
	"""
	return Generator(days, seed, now).run()

class Generator(object):
	def __init__(self, days, seed, now):
		self.days = days
		self.rng = random.Random(seed)
		self.now = (now or datetime.now()).replace(microsecond=0)
		self.today = datetime.combine(self.now.date(), time())
		self.patterns = badword_patterns()
		self.scripts = [(kind, groups, parse_script(text)) for (kind, groups, text) in SCRIPTS]

	def run(self):
		self.groups = self.create_groups()
		people = self.plan_people()
		self.plan_buddies(people)
		acls = self.create_acls(people)
		badwords = Badword.objects.bulk_create(
			[Badword(badword=w, isregex=r, isenabled=e) for (w, r, e) in BADWORDS])
		conversations = self.plan_conversations(people, acls)
		self.plan_logins(people, conversations)
		self.create_users(people)
		buddies = self.create_buddies(people)
		messages = self.create_conversations(conversations)
		return [
			('groups', len(self.groups) - 1), # The built-in 'guest' existed
			('users', len(people)),
			('buddies', buddies),
			('acls', len(acls)),
			('badwords', len(badwords)),
			('conversations', len(conversations)),
			('messages', messages),
		]

	#
	# Groups
	#
	def create_groups(self):
		"""Returns the groups by name, as (group, set of rule ids)."""
		guest = UserGroup.objects.get(groupname=GUEST)
		groups = {GUEST: (guest, set(GUEST_RULES))}
		for (name, isactive, description, rules) in GROUPS:
			group = UserGroup.objects.create(groupname=name, isactive=isactive,
				isbuiltin=False, description=description)
			groups[name] = (group, set(rules))
		GroupRule.objects.bulk_create([GroupRule(group=group, rule_id=rule_id)
			for (group, rules) in groups.values() for rule_id in sorted(rules)])
		return groups

	#
	# Users and their buddies
	#
	def plan_people(self):
		rng = self.rng
		people = []
		subnets = [GUEST] + [name for (name, _, _, _) in GROUPS]
		hosts = {}
		for (first, last, group, chattiness) in EMPLOYEES:
			person = Person(first, last, group, chattiness)
			hosts[group] = hosts.get(group, 19) + 1
			person.ip = '10.1.%d.%d' % (subnets.index(group) + 1, hosts[group])
			if rng.random() < 0.4:
				person.psm = rng.choice(PERSONAL_MESSAGES)
			if person.never_logged_in:
				pass
			elif not person.isenabled or group == INTERNS:
				# Gone for a while
				person.last_day = rng.randint(35, 75)
			elif rng.random() < 0.55:
				person.status = rng.choice(ONLINE_STATUSES)
				person.last_day = 0
			else:
				person.last_day = rng.choice((0, 0, 1, 1, 1, 2, 3, 4, 7))
			people.append(person)
		return people

	def plan_buddies(self, people):
		rng = self.rng
		contacts = {}
		for (username, displayname, first, kind) in CONTACTS:
			status = rng.choice(('NLN', 'NLN', 'AWY', 'BSY', 'FLN', 'FLN', 'FLN'))
			contacts.setdefault(kind, []).append(Contact(username, displayname,
				first, kind, rng.choice(EXTERNAL_PSMS), status))
		for person in people:
			others = [p for p in people if p is not person]
			teammates = [p for p in others if p.group == person.group]
			coworkers = rng.sample(teammates, min(len(teammates), rng.randint(2, 5)))
			coworkers += rng.sample([p for p in others if p not in coworkers], rng.randint(2, 4))
			person.buddies = [p.as_contact() for p in coworkers]
			for (kind, (low, high)) in sorted(BUDDIES[person.group].items()):
				person.buddies += rng.sample(contacts[kind], rng.randint(low, high))
			if rng.random() < 0.15:
				person.buddies.append(contacts[SPAM][0])
		# A recruiter keeps adding them
		for person in people:
			if person.username in ('daniel.kowalski@' + DOMAIN, 'richard.hale@' + DOMAIN):
				person.buddies.append(contacts[SPAM][1])

	def create_users(self, people):
		for person in people:
			person.model = User.objects.create(group=self.groups[person.group][0],
				username=person.username, displayname=person.displayname,
				psm=person.psm, status=person.status, lastlogin=person.lastlogin,
				isenabled=person.isenabled)

	def create_buddies(self, people):
		buddies = []
		for person in people:
			for contact in person.buddies:
				buddies.append(Buddy(user=person.model, username=contact.username,
					displayname=contact.displayname, psm=contact.psm,
					status=contact.status,
					# People block the contacts they don't want to hear from
					isblocked=contact.kind == SPAM))
		Buddy.objects.bulk_create(buddies)
		return len(buddies)

	#
	# ACLs
	#
	def create_acls(self, people):
		acls = list(ACLS)
		for person in people:
			if person.group == SUPPORT:
				acls += [(person.username, domain, Acl.ACTION_BLOCK) for domain in PERSONAL_DOMAINS]
		Acl.objects.bulk_create([Acl(localim=l, remoteim=r, action=a) for (l, r, a) in acls])
		return acls

	@staticmethod
	def is_blocked(acls, localim, remoteim):
		return any(action == Acl.ACTION_BLOCK and fnmatchcase(localim, l) and fnmatchcase(remoteim, r)
			for (l, r, action) in acls)

	#
	# Conversations
	#
	def plan_conversations(self, people, acls):
		"""
		Returns the conversations, in the order they started, as
		(person, contact, active, timestamped lines).
		"""
		rng = self.rng
		conversations = []
		for person in people:
			rules = self.groups[person.group][1]
			if RULE_HISTORY not in rules or person.last_day is None:
				continue
			partners = [c for c in person.buddies
				if c.kind != SPAM and not self.is_blocked(acls, person.username, c.username)]
			if not partners:
				continue
			weights = [CHAT_WEIGHTS[c.kind] for c in partners]
			for days_ago in range(self.days, person.last_day - 1, -1):
				day = self.today - timedelta(days=days_ago)
				weekend = day.weekday() >= 5
				rate = person.chattiness * (0.08 if weekend else 1.0)
				if not days_ago: # Only part of today went by
					workday = (self.now - day - timedelta(hours=8)) / timedelta(hours=10)
					rate *= min(max(workday, 0.15), 1.0)
				for _ in range(self.poisson(rate)):
					contact = rng.choices(partners, weights)[0]
					lines = self.script_for(person, contact, rules)
					if rng.random() < 0.15: # Some end abruptly
						lines = lines[:rng.randint(2, len(lines))]
					if days_ago:
						earliest = day + timedelta(hours=10 if weekend else 8)
						latest = day + timedelta(hours=23 if weekend else 19, minutes=30)
					else:
						# Today's ended a while ago: they aren't active
						earliest = day + timedelta(hours=8)
						latest = self.now - timedelta(minutes=15)
						if latest - earliest < timedelta(minutes=30): # Early bird
							earliest = day
						if latest <= earliest:
							continue
					conversations.append((person, contact, False,
						self.place(lines, earliest, latest)))
			# People online now may be talking to someone
			if person.status != 'FLN' and rng.random() < 0.5:
				conversations.append(self.active_conversation(person, partners, weights, rules))
		# Somebody's always talking
		if not any(active for (_, _, active, _) in conversations):
			for person in people:
				rules = self.groups[person.group][1]
				partners = [c for c in person.buddies if c.kind == COWORKER]
				if person.status != 'FLN' and RULE_HISTORY in rules and partners:
					conversations.append(self.active_conversation(person, partners,
						[1] * len(partners), rules))
					break
		conversations.sort(key=lambda c: c[3][0][0])
		return conversations

	def active_conversation(self, person, partners, weights, rules):
		rng = self.rng
		contact = rng.choices(partners, weights)[0]
		lines = self.script_for(person, contact, rules)
		lines = lines[:rng.randint(min(2, len(lines)), len(lines))]
		latest = max(self.today, self.now - timedelta(seconds=rng.randint(0, 480)))
		earliest = max(self.today, self.now - timedelta(minutes=45))
		return (person, contact, True, self.place(lines, earliest, latest, at_end=True))

	def script_for(self, person, contact, rules):
		"""The lines of a random script, without the features the rules block."""
		scripts = [lines for (kind, groups, lines) in self.scripts
			if kind == contact.kind and (groups is None or person.group in groups)]
		lines = []
		for line in self.rng.choice(scripts):
			if BLOCKING_RULES.get(line.type) in rules:
				continue
			content = line.content.replace('{me}', person.first).replace('{you}', contact.first)
			lines.append(Line(line.inbound, line.type, content))
		return lines

	def place(self, lines, earliest, latest, at_end=False):
		"""
		Times the lines between earliest and latest, a few seconds to a few
		minutes apart. at_end places the last one at latest.
		Returns (timestamp, line) pairs.
		"""
		rng = self.rng
		offsets = [0]
		for _ in lines[1:]:
			gap = rng.randint(120, 600) if rng.random() < 0.08 else rng.randint(4, 75)
			offsets.append(offsets[-1] + gap)
		room = int((latest - earliest).total_seconds())
		if offsets[-1] > room: # Talk faster
			offsets = [offset * room // offsets[-1] for offset in offsets]
		if at_end:
			start = latest - timedelta(seconds=offsets[-1])
		else:
			start = earliest + timedelta(seconds=rng.randint(0, room - offsets[-1]))
		return [(start + timedelta(seconds=offset), line) for (offset, line) in zip(offsets, lines)]

	def poisson(self, rate):
		# Knuth's algorithm: fine for small rates
		limit, k, p = math.exp(-rate), 0, self.rng.random()
		while p > limit:
			k += 1
			p *= self.rng.random()
		return k

	def plan_logins(self, people, conversations):
		"""Users log in a while before their first conversation of the day."""
		rng = self.rng
		first_chat = {}
		for (person, _, _, lines) in conversations:
			day = (self.today - datetime.combine(lines[0][0].date(), time())).days
			if day == person.last_day and person not in first_chat:
				first_chat[person] = lines[0][0]
		for person in people:
			if person.last_day is None:
				continue
			day = self.today - timedelta(days=person.last_day)
			if person in first_chat:
				login = first_chat[person] - timedelta(minutes=rng.randint(1, 40))
			else:
				login = day + timedelta(hours=8, minutes=rng.randint(0, 90))
				if login > self.now: # Before work: a while ago
					since = min(self.now - day, timedelta(hours=3))
					login = self.now - timedelta(seconds=rng.randint(0, int(since.total_seconds())))
			# Not before the day starts
			person.lastlogin = max(day, login)

	def create_conversations(self, conversations):
		"""Saves the conversations and their messages. Returns how many messages."""
		cursor = connection.cursor()
		rows = []
		for (person, contact, active, lines) in conversations:
			# Raw SQL: the models' timestamps are auto_now_add
			cursor.execute('INSERT INTO conversations (user_id, timestamp, status) '
				'VALUES (%s, %s, %s)', [person.model.id, lines[0][0], 1 if active else 0])
			conversation_id = cursor.lastrowid
			# Sometimes on the VPN
			ip = person.ip if self.rng.random() < 0.9 else '172.16.8.%d' % self.rng.randint(2, 250)
			clientip = ip_str_to_long(ip)
			for (timestamp, line) in lines:
				rows.append((timestamp, conversation_id, clientip, int(line.inbound),
					line.type, person.username, contact.username,
					int(self.is_filtered(person, line)), line.content))
		rows.sort(key=lambda row: row[0])
		for start in range(0, len(rows), 1000):
			cursor.executemany('INSERT INTO messages (timestamp, conversation_id, '
				'clientip, inbound, type, localim, remoteim, filtered, content) '
				'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', rows[start:start + 1000])
		return len(rows)

	def is_filtered(self, person, line):
		rules = self.groups[person.group][1]
		return line.type == Message.Type.MSG and RULE_BADWORDS in rules \
			and any(p.search(line.content) for p in self.patterns)
