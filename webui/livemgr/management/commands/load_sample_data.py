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

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from webui.livemgr import sample_data

class Command(BaseCommand):
	help = ('Fills the livemgr tables with sample data to try out the web UI: '
		'user groups, users and their buddies, ACLs, badwords, and conversations '
		'up to now. See webui/livemgr/sample_data.py.')

	def add_arguments(self, parser):
		parser.add_argument('--flush', action='store_true',
			help='Delete all the users, groups, ACLs, badwords and conversations first.')
		parser.add_argument('--noinput', '--no-input', action='store_false',
			dest='interactive', help="Don't ask before deleting anything.")
		parser.add_argument('--days', type=int, default=sample_data.DAYS,
			help='How many days of conversations to create before today\'s (default: %(default)s).')
		parser.add_argument('--seed', type=int, default=sample_data.SEED,
			help='Seed of the random data: the same seed creates the same data (default: %(default)s).')

	def handle(self, *args, **options):
		if options['days'] < 0:
			raise CommandError('--days must be 0 or more.')
		if not sample_data.tables_exist():
			raise CommandError('The livemgr tables are missing. Create them with '
				'bootstrap/db/create_tables.sql first.')
		existing = sample_data.existing_rows()
		if existing and not options['flush']:
			raise CommandError('The database already has %s. Run with --flush to '
				'replace them.' % sample_data.format_counts(existing))
		if existing and options['interactive']:
			answer = input('This deletes %s. Are you sure? (yes/no): ' % sample_data.format_counts(existing))
			if answer.strip().lower() != 'yes':
				raise CommandError('Cancelled.')
		with transaction.atomic():
			if existing:
				sample_data.flush()
			counts = sample_data.load(days=options['days'], seed=options['seed'])
		self.stdout.write(self.style.SUCCESS('Loaded %s.' % sample_data.format_counts(counts)))
