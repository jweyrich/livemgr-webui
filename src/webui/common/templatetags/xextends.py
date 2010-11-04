"""
	Code from: http://bitbucket.org/miracle2k/djutils/src/beddfd57f6d5/djutils/template/django/tags/extends.py
	Author: Michael Elsdoerfer
	Posted: ?

    Extended extends tag that supports passing parameters, which will be made
    available in the context of the extended template (and all the way up the
    hierarchy).

    It wraps around the orginal extends tag, to avoid code duplication, and to
    not miss out on possible future django enhancements.
    **NOTE**: The current implementation will override variables passed from your
    view, too, so be careful.

    Some of the argument parsing code is based on:
        http://www.djangosnippets.org/snippets/11/

    Examples:

        {% xextends "some.html" %}
        {% xextends "some.html" with title="title1" %}
        {% xextends "some.html" with title="title2"|capfirst %}
"""

from django import template
from django.template.loader_tags import ExtendsNode, do_extends
import StringIO
import tokenize

register = template.Library()

class XExtendsNode(ExtendsNode):
	def render(self, context):
		# resolve all expressons first
		kwargs = self.kwargs.copy()
		for arg in kwargs:
			kwargs[arg] = kwargs[arg].resolve(context)

		# update() would add the var at the top of the stack, we need our 
		# vars to be at the bottom though; this is semantically correct, 
		# and also required to allow further overriding of extends parameters 
		# by our own child templates, in case there are multiple levels of 
		# inheritance.
		context.dicts.append(kwargs)
		try:
			return super(XExtendsNode, self).render(context)
		finally:
			context.pop()

@register.tag(name='xextends')
def do_xextends(parser, token):
	bits = token.split_contents()
	kwargs = {}
	if 'with' in bits:
		pos = bits.index('with')
		argslist = bits[pos + 1:]
		bits = bits[:pos]
		for i in argslist:
			try:
				a, b = i.split('=', 1); a = a.strip(); b = b.strip()
				keys = list(tokenize.generate_tokens(StringIO.StringIO(a).readline))
				if keys[0][0] == tokenize.NAME:
					kwargs[str(a)] = parser.compile_filter(b)
				else: raise ValueError
			except ValueError:
				raise template.TemplateSyntaxError, "Argument syntax wrong: should be key=value"
		# before we are done, remove the argument part from the token contents,
		# or django's extends tag won't be able to handle it.
		# TODO(jweyrich): Find a better solution that preserves the orginal token including whitespace etc.
		token.contents = " ".join(bits)

	# let the orginal do_extends parse the tag, and wrap the ExtendsNode
	node = do_extends(parser, token)
	node.__class__ = XExtendsNode
	node.kwargs = kwargs
	return node
