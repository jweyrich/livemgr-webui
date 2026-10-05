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
	Custom template tags and filters used by the templates. They're written
	against the template engine internals, which change across Django versions.
"""

from django import forms
from django.http import HttpRequest, QueryDict
from django.template import Context, Template, TemplateSyntaxError
from webui.common.color_dict import color_dict
import io
import os
import sys
import unittest
import warnings

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'templates')

def render(source, **context):
	return Template(source).render(Context(context))

class TemplatesTest(unittest.TestCase):
	def test_compile_without_deprecation_warnings(self):
		# e.g. the {% url %} syntax with unquoted view names, deprecated in
		# Django 1.4 and removed in 1.5, or {% load url from future %},
		# deprecated in 1.7. Pending deprecations are removed a version later.
		for module in list(sys.modules.values()):
			# Python 2 skips warnings it has already seen, even when ignored.
			getattr(module, '__warningregistry__', {}).clear()
		with warnings.catch_warnings():
			warnings.simplefilter('error', DeprecationWarning)
			warnings.simplefilter('error', PendingDeprecationWarning)
			for dirpath, dirnames, filenames in os.walk(TEMPLATES_DIR):
				for filename in filenames:
					path = os.path.join(dirpath, filename)
					try:
						Template(io.open(path, encoding='utf-8').read())
					except (DeprecationWarning, PendingDeprecationWarning) as e:
						self.fail('%s: %s' % (os.path.relpath(path, TEMPLATES_DIR), e))

class SwitchTagTest(unittest.TestCase):
	SOURCE = ('{% load switch %}{% switch value %}'
		'{% case 1 %}one{% endcase %}'
		'{% case "a" %}letter{% endcase %}'
		'{% case other %}variable{% endcase %}'
		'{% endswitch %}')

	def test_matches_cases(self):
		self.assertEqual(render(self.SOURCE, value=1), 'one')
		self.assertEqual(render(self.SOURCE, value='a'), 'letter')
		self.assertEqual(render(self.SOURCE, value='z', other='z'), 'variable')

	def test_no_match_renders_nothing(self):
		self.assertEqual(render(self.SOURCE, value=99), '')
		self.assertEqual(render(self.SOURCE), '')

	def test_requires_one_argument(self):
		self.assertRaises(TemplateSyntaxError, Template,
			'{% load switch %}{% switch %}{% endswitch %}')

class EvaluateTagTest(unittest.TestCase):
	def test_captures_output(self):
		self.assertEqual(
			render('{% load evaluate %}{% evaluate as greeting %}hi {{ name }}{% endevaluate %}<{{ greeting }}>',
				name='bob'),
			'<hi bob>')

	def test_requires_as(self):
		self.assertRaises(TemplateSyntaxError, Template,
			'{% load evaluate %}{% evaluate greeting %}x{% endevaluate %}')

class XIncludeTagTest(unittest.TestCase):
	# Quirk: the template name is also passed as the first positional argument.
	# Harmless today because every template only passes keyword arguments.
	def test_passes_positional_and_keyword_arguments(self):
		self.assertEqual(
			render('{% load xinclude %}{% xinclude "tests/xinclude.html", 1, name, title="t"|upper %}',
				name='bob'),
			'[tests/xinclude.html][1][bob]<T>')

	def test_does_not_leak_arguments(self):
		self.assertEqual(
			render('{% load xinclude %}{% xinclude "tests/xinclude.html", title="t" %}[{{ title }}]',
				title='outer'),
			'[tests/xinclude.html]<t>[outer]')

class AppendToGetTagTest(unittest.TestCase):
	def render_for(self, path, query, **context):
		request = HttpRequest()
		request.META['PATH_INFO'] = path
		request.GET = QueryDict(query)
		return render('{% load append_to_get %}{% append_to_get page=number %}',
			request=request, **context)

	def test_replaces_the_parameter_and_keeps_the_others(self):
		result = self.render_for('/acls/', 'sort=localim&page=1', number=3)
		path, query = result.split('?')
		self.assertEqual(path, '/acls/')
		self.assertEqual(sorted(query.split('&')), ['page=3', 'sort=localim'])

	def test_adds_the_parameter(self):
		self.assertEqual(self.render_for('/acls/', '', number=2), '/acls/?page=2')

class CustomFiltersTest(unittest.TestCase):
	def test_split_index_and_index_start(self):
		# How conversations/show.html renders file transfers ("<size> <filename>")
		self.assertEqual(
			render('{% load custom_filters %}{% with content|split as info %}'
				'{{ info|index:0 }}|{{ info|index_start:1 }}{% endwith %}',
				content='1024 my report.pdf'),
			'1024|my report.pdf')

	def test_dict_get(self):
		colors = color_dict()
		self.assertEqual(
			render('{% load custom_filters %}{{ colors|dict_get:who }}', colors=colors, who='alice'),
			'#7ca380')

	def test_langcode(self):
		source = '{% load custom_filters %}{{ code|langcode }}'
		self.assertEqual(render(source, code='pt-br'), 'pt-BR')
		self.assertEqual(render(source, code='en-us'), 'en-US')
		self.assertEqual(render(source, code='en'), 'en')
		self.assertEqual(render(source, code='zh-hant'), 'zh-hant')

	def test_selected_if(self):
		source = '{% load custom_filters %}{{ menu|selected_if:"acls" }}'
		self.assertEqual(render(source, menu='acls'), 'selected')
		self.assertEqual(render(source, menu='users'), '')

	def test_is_checkbox(self):
		class Form(forms.Form):
			flag = forms.BooleanField()
			name = forms.CharField()
		form = Form()
		source = '{% load custom_filters %}{{ field|is_checkbox }}'
		self.assertEqual(render(source, field=form['flag']), 'True')
		self.assertEqual(render(source, field=form['name']), 'False')
