"""
    Based on: http://www.djangosnippets.org/snippets/10/
	Author: limodou
	Posted: February 25, 2007

    Evaluate content and save it to myvar

    Examples:

        {% evaluate as myvar %} ... {% endevaluate %}
        {{ myvar }}
"""

from django import template
import re

register = template.Library()

class EvalNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name
        
    def render(self, context):
        output = self.nodelist.render(context)
        context[self.var_name] = output
        return ''

@register.tag(name='evaluate')
def do_evaluate(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, '%r tag should define as "%r as var_name"' % (tag_name, tag_name)
    var_name = m.groups()[0]
    nodelist = parser.parse(('endevaluate',))
    parser.delete_first_token()
    return EvalNode(nodelist, var_name)
