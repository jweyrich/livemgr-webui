"""
	Based on: http://www.djangosnippets.org/snippets/1627/
	Author: gregb
	Posted: July 13, 2009

	  This tag is designed to facilitate pagination in the case where both the
	page number and other parameters (eg. search criteria) are passed via GET.
	  It takes one argument - a dictionary of GET variables to be added to the
	current url
	
	Example usage:
	
	{% for page_num in results.paginator.page_range %}     
		<a href="{% append_to_get p=page_num %}">{{ page_num }}</a>
	{% endfor %}
	
	Note that the passed arguments are evaluated within the template context.
"""

from django import template
from webui.common.decorators.easy_tag import easy_tag

register = template.Library()

class AppendGetNode(template.Node):
	def __init__(self, dict):
		self.dict_pairs = {}
		for pair in dict.split(','):
			pair = pair.split('=')
			self.dict_pairs[pair[0]] = template.Variable(pair[1])
	def render(self, context):
		get = context['request'].GET.copy()
		for key in self.dict_pairs:
			get[key] = self.dict_pairs[key].resolve(context)
		path = context['request'].META['PATH_INFO']
		#print "&".join(["%s=%s" % (key, value) for (key, value) in get.items() if value])
		if len(get):
			path += "?%s" % "&".join(["%s=%s" % (key, value) for (key, value) in get.items() if value])
		return path

@register.tag(name='append_to_get')
@easy_tag
def do_append_to_get(_tag, dict):
	return AppendGetNode(dict)
