"""
	Based on: http://www.djangosnippets.org/snippets/11/
	Author: limodou
	Posted: February 25, 2007

	Extended include tag with parameter support.
	The parameters can be accessed from within the include like normal variables.

	Examples:

		{% xinclude "foo/some_include" %}
		{% xinclude "foo/some_include", arg1, arg2, ..., argn %}

		{% xinclude "some.html" %}
		{% xinclude "some.html", "test spaces", "b"|capfirst, title="title1" %}
		{% xinclude "some.html", 123, "more spaces", title="title2"|capfirst %}

		{% for i in args %}{{ i }}{% endfor %}
		<h2>{{ title }}</h2>
		<p>{{ name }}</p>
		<h3>args</h3>
		{{ args }}
		<h3>kwargs</h3>
		{{ kwargs }}
"""
	
from django import template
from django.template.loader import get_template
from django.conf import settings
import tokenize
#import shlex
import StringIO

register = template.Library()

class CallNode(template.Node):
	def __init__(self, template_name, *args, **kwargs):
		self.template_name = template_name
		self.args = args
		self.kwargs = kwargs
	def render(self, context):
		try:
			template_name = self.template_name.resolve(context)
			t = get_template(template_name)
			d = {}
			args = d['args'] = []
			kwargs = d['kwargs'] = {}
			for i in self.args:
				args.append(i.resolve(context))
			for key, value in self.kwargs.items():
				kwargs[key] = d[key] = value.resolve(context)

			context.update(d)
			result = t.render(context)
			context.pop()
			return result
		except:
			if settings.TEMPLATE_DEBUG:
				raise
			return ''

def tag_split(value):
	params = []
	# TODO handle strings containing the separator
	for substring in value[8:].split(','):
		params.append(substring.strip())
	return params

@register.tag(name="xinclude")
def do_xinclude(parser, token):
	argslist = tag_split(token.contents.encode('ascii'))
	#print 'argslist=%s' % argslist
	if len(argslist) < 1:
		raise template.TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" % argslist[0]

	path = parser.compile_filter(argslist[0])
	if argslist:
		args = []
		kwargs = {}
		for i in argslist:
			if '=' in i:
				key, value = i.split('=', 1)
				key = key.strip()
				value = value.strip()
				#print 'key:' + key
				#print 'value:' + value
				buf = StringIO.StringIO(key)
				keys = list(tokenize.generate_tokens(buf.readline))
				if keys[0][0] == tokenize.NAME:
					kwargs[key] = parser.compile_filter(value)
				else:
					raise template.TemplateSyntaxError, "Invalid argument syntax: should be key=value"
			else:
				args.append(parser.compile_filter(i))
	return CallNode(path, *args, **kwargs)
