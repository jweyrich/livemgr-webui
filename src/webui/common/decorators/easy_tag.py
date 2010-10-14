"""
	Based on: http://www.djangosnippets.org/snippets/300/
	Author: jacobian
	Posted: July 3, 2007

	Decorator to facilitate template tag creation
"""

from django import template

def easy_tag(func):
	"""deal with the repetitive parts of parsing template tags"""
	def inner(parser, token):
		#print token
		try:
			return func(*token.split_contents())
		except TypeError:
			raise template.TemplateSyntaxError('Bad arguments for tag "%s"' % token.split_contents()[0])
		inner.__name__ = func.__name__
		inner.__doc__ = inner.__doc__
	return inner