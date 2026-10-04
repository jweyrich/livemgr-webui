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
	Tests for the webui.common package (it has no models module, so its tests
	live here, in an app the test runner can find).
"""

from StringIO import StringIO
from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, QueryDict
from reportlab.lib.pagesizes import A4
from webui.common.color_dict import color_dict
from webui.common.custom_paginator import CustomPaginator
from webui.common.db.query import fetchall_to_dict, fetchone_to_dict
from webui.common.decorators.rest import rest_delete, rest_get, rest_multiple, \
	rest_post, rest_put
from webui.common.json import ComplexTypeEncoder
from webui.common.report import NumberedCanvas, coord_tl, coord_tr
from webui.common.utils import flash_error, flash_form_error, flash_success, \
	request_has_error
from webui.livemgr.controllers.acls import AclTable
from webui.livemgr.models import Acl
from webui.livemgr.tests.base import LivemgrTestCase
import json
import unittest

class FakeMessageStorage(object):
	def __init__(self):
		self.added = []
	def add(self, level, message, extra_tags=''):
		self.added.append((level, unicode(message)))

def make_request(method='GET', get=''):
	request = HttpRequest()
	request.method = method
	request.GET = QueryDict(get)
	request._messages = FakeMessageStorage()
	return request

class ColorDictTest(unittest.TestCase):
	def test_assigns_colors_in_order_and_remembers_them(self):
		colors = color_dict()
		self.assertEqual(colors.get('alice'), '#7ca380')
		self.assertEqual(colors.get('bob'), '#ad8282')
		self.assertEqual(colors.get('alice'), '#7ca380')

	def test_instances_do_not_share_the_palette(self):
		color_dict().get('alice')
		self.assertEqual(color_dict().get('bob'), '#7ca380')

	def test_custom_palette(self):
		self.assertEqual(color_dict([0x000001]).get('x'), '#000001')

class PageRangeTest(unittest.TestCase):
	def test_page_range(self):
		get_page_range = CustomPaginator.get_page_range
		self.assertEqual(get_page_range(1, 1), [1])
		self.assertEqual(get_page_range(3, 2), [1, 2, 3])
		self.assertEqual(get_page_range(20, 1), list(range(1, 12)))
		self.assertEqual(get_page_range(20, 10), list(range(5, 16)))
		self.assertEqual(get_page_range(20, 18), list(range(13, 21)))

	def test_page_from_request(self):
		self.assertEqual(CustomPaginator.get_page_from_request(make_request(get='page=3')), 3)
		self.assertEqual(CustomPaginator.get_page_from_request(make_request(get='page=x')), 1)
		self.assertEqual(CustomPaginator.get_page_from_request(make_request()), 1)

class CustomPaginatorTest(LivemgrTestCase):
	"""CustomPaginator overrides Paginator internals (_count, _num_pages)."""
	def setUp(self):
		for i in range(25):
			self.make_acl('user%02d@example.com' % i)

	def paginator(self):
		qset = Acl.objects.all()
		return CustomPaginator(qset).instantiate(AclTable, qset, order_by='localim')

	def test_page(self):
		page = self.paginator().page(2, 10)
		self.assertEqual(page.number, 2)
		self.assertEqual(page.paginator.num_pages, 3)
		self.assertEqual(page.paginator.count, 25)
		self.assertEqual([row.data.localim for row in page.object_list],
			['user%02d@example.com' % i for i in range(10, 20)])
		self.assertEqual(page.paginator.limited_page_range, [1, 2, 3])

	def test_page_number_from_request(self):
		page = self.paginator().with_request(make_request(get='page=3')).page(None, 10)
		self.assertEqual(page.number, 3)
		self.assertEqual(len(page.object_list), 5)

	def test_out_of_range_page_falls_back_to_the_first(self):
		self.assertEqual(self.paginator().page(99, 10).number, 1)

	def test_default_page_size(self):
		self.assertEqual(len(self.paginator().page(1, None).object_list), CustomPaginator.PER_PAGE)

	def test_page_requires_a_number_or_a_request(self):
		self.assertRaises(Exception, self.paginator().page, None, 10)

	def test_with_count_overrides_the_total(self):
		page = self.paginator().with_count(40).page(1, 10)
		self.assertEqual(page.paginator.count, 40)
		self.assertEqual(page.paginator.num_pages, 4)

	def test_group_by_counts_distinct_groups(self):
		qset = Acl.objects.all()
		Acl.objects.filter(localim__in=['user00@example.com', 'user01@example.com']) \
			.update(remoteim='shared@example.org')
		page = CustomPaginator(qset) \
			.instantiate(AclTable, qset, order_by='localim') \
			.group_by(True, 'remoteim') \
			.page(1, 10)
		self.assertEqual(page.paginator.count, 2) # 'shared@example.org', '*@example.org'

class FlashTest(unittest.TestCase):
	def test_flash_error_marks_the_request(self):
		request = make_request()
		self.assertFalse(request_has_error(request))
		flash_success(request, 'ok')
		self.assertFalse(request_has_error(request))
		flash_error(request, 'bad')
		self.assertTrue(request_has_error(request))
		self.assertEqual(request._messages.added,
			[(messages.SUCCESS, u'ok'), (messages.ERROR, u'bad')])

	def test_flash_form_error_prefers_non_field_errors(self):
		class Form(forms.Form):
			name = forms.CharField()
			def clean(self):
				raise forms.ValidationError('Whole form is wrong')
		request = make_request()
		form = Form({'name': 'x'})
		self.assertFalse(form.is_valid())
		flash_form_error(request, form)
		self.assertEqual(request._messages.added, [(messages.ERROR, u'Whole form is wrong')])

	def test_flash_form_error_falls_back_to_a_generic_message(self):
		class Form(forms.Form):
			name = forms.CharField()
		request = make_request()
		form = Form({})
		self.assertFalse(form.is_valid())
		flash_form_error(request, form)
		self.assertEqual(request._messages.added,
			[(messages.ERROR, u'Please, correct the fields below.')])

class RestDecoratorsTest(unittest.TestCase):
	def view(self, request):
		return HttpResponse('called')

	def assertAllows(self, decorated, method):
		self.assertEqual(decorated(make_request(method)).content, 'called')

	def assertRejects(self, decorated, method):
		response = decorated(make_request(method))
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, "You don't have permission to access this.")

	def test_rest_get(self):
		self.assertAllows(rest_get(self.view), 'GET')
		self.assertRejects(rest_get(self.view), 'POST')

	def test_rest_post(self):
		self.assertAllows(rest_post(self.view), 'POST')
		self.assertRejects(rest_post(self.view), 'GET')

	def test_rest_put_and_delete(self):
		self.assertAllows(rest_put(self.view), 'PUT')
		self.assertRejects(rest_put(self.view), 'POST')
		self.assertAllows(rest_delete(self.view), 'DELETE')
		self.assertRejects(rest_delete(self.view), 'GET')

	def test_rest_multiple(self):
		decorated = rest_multiple(['GET', 'POST'])(self.view)
		self.assertAllows(decorated, 'GET')
		self.assertAllows(decorated, 'POST')
		self.assertRejects(decorated, 'PUT')

	def test_view_arguments_are_forwarded(self):
		decorated = rest_get(lambda request, object_id: HttpResponse(object_id))
		self.assertEqual(decorated(make_request(), object_id='7').content, '7')

class ComplexTypeEncoderTest(unittest.TestCase):
	def test_uses_to_json(self):
		class Point(object):
			def to_json(self):
				return {'x': 1}
		self.assertEqual(json.loads(json.dumps([Point()], cls=ComplexTypeEncoder)), [{'x': 1}])

	def test_rejects_other_objects(self):
		self.assertRaises(TypeError, json.dumps, object(), cls=ComplexTypeEncoder)

class ReportTest(unittest.TestCase):
	def test_coordinates_from_top_corners(self):
		self.assertEqual(coord_tl((100, 200), 10, 20), (10, 180))
		self.assertEqual(coord_tr((100, 200), 10, 20), (90, 180))

	def test_numbered_canvas_knows_the_page_count(self):
		seen = []
		class Canvas(NumberedCanvas):
			def drawPageNumber(self, page_count):
				seen.append((self.getPageNumber(), page_count))
		buffer = StringIO()
		canvas = Canvas(buffer, pagesize=A4)
		canvas.drawString(10, 10, 'one')
		canvas.showPage()
		canvas.drawString(10, 10, 'two')
		canvas.showPage()
		canvas.save()
		self.assertEqual(seen, [(1, 2), (2, 2)])
		self.assertTrue(buffer.getvalue().startswith('%PDF'))

class RawQueryTest(LivemgrTestCase):
	def test_fetchone_to_dict(self):
		self.assertEqual(fetchone_to_dict("SELECT 1 AS a, %s AS b", 'x'), {'a': 1, 'b': 'x'})
		self.assertEqual(fetchone_to_dict("SELECT name FROM settings WHERE name = %s", 'nope'), None)

	def test_fetchall_to_dict(self):
		rows = list(fetchall_to_dict(
			"SELECT name FROM settings WHERE name LIKE %s ORDER BY name", '%protocol%'))
		self.assertEqual(rows, [{'name': 'max_protocol_version'}, {'name': 'min_protocol_version'}])
