"""
    This library some tags that provide some slighty more "native" python
    functionality to the template language.
    
    Currently, it contains code from:
        * http://djangosnippets.org/snippets/130/  (pyif)
        * http://djangosnippets.org/snippets/9/    (pyexpr)
"""

from django import template
from django.template import Node, NodeList, TemplateSyntaxError, \
	VariableDoesNotExist
from django.utils.translation import gettext_lazy as _
import re
register = template.Library()

"""
    PyExpr (from http://djangosnippets.org/snippets/9/)
    
    This tag can be used to calculate a python expression, and 
    save it into a template variable which you can reuse later 
    or directly output to template. So if the default django tag 
    can not be suit for your need, you can use it.

    How to use it

        {% expr "1" as var1 %}
        {% expr [0, 1, 2] as var2 %}
        {% expr _('Menu') as var3 %}
        {% expr var1 + "abc" as var4 %}
        ...
        {{ var1 }}

        for 0.2 version

        {% expr 3 %}
        {% expr "".join(["a", "b", "c"]) %}

        Will directly output the result to template

        Syntax

        {% expr python_expression as variable_name %}

        python_expression can be valid python expression, and you can 
        even use _() to translate a string. Expr tag also can 
        used context variables.  
"""

#from django import template

class ExprNode(template.Node):
    def __init__(self, expr_string, var_name):
        self.expr_string = expr_string
        self.var_name = var_name

    def render(self, context):
        try:
            clist = list(context)
            clist.reverse()
            d = {}
            d['_'] = _
            for c in clist:
                d.update(c)
            if self.var_name:
                context[self.var_name] = eval(self.expr_string, d)
                return ''
            else:
                return str(eval(self.expr_string, d))
        except:
            raise

r_expr = re.compile(r'(.*?)\s+as\s+(\w+)', re.DOTALL)
def do_expr(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    m = r_expr.search(arg)
    if m:
        expr_string, var_name = m.groups()
    else:
        if not arg:
            raise template.TemplateSyntaxError, "%r tag at least require one argument" % tag_name

        expr_string, var_name = arg, None
    return ExprNode(expr_string, var_name)
do_expr = register.tag('expr', do_expr)

"""
    PyIf (from http://djangosnippets.org/snippets/130/)

    This is an adaptation/enhancement to Django's built in IfNode {% if ... %} 
    that combines if ifequal ifnotequal into one and then adds even more. 
    
    This Supports:
    
        1. ==, !=
        2. not ....
        3. v in (1,"y",z)
        4. <=, <, >=, >
        5. nesting (True and (False or (True or False)))

    How to use it:

        {% pyif i == 1 or (5 >= i and i != 7) and user.first_name in \
                ('John', 'Jacob') %} 'Tis true. {% else %} 'Tis false. {% endif %}
"""

#from django.template import Library
#import re

# For Python 2.3
if not hasattr(__builtins__, 'set'):
    from sets import Set as set

variable_re = re.compile(r'[\w._\|\"\']+')
string_re = re.compile(r'^([\"\']).*\1$')

TAGNAME = 'pyif' # Hopefully this can replace django's built-in if tag

class IfNode(Node):
    def __init__(self, expression, variables, nodelist_true, nodelist_false):
        self.expression = expression
        self.variables = variables
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<If node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        variable_context = {}
        expression = self.expression
        for variable in self.variables:
            try:
                value = variable.resolve(context, True)
            except VariableDoesNotExist:
                value = None

            context_name = 'var%s' % len(variable_context)
            expression = re.sub(r'(?<![\w._\|])%s(?![\w._\|])' % re.escape(variable.token), context_name, expression)
            variable_context[context_name] = value
        try:
            resultant = eval(expression, variable_context)
        except:
            resultant = False

        if not resultant:
            return self.nodelist_false.render(context)
        return self.nodelist_true.render(context)

def do_if(parser, token):
    bits = token.contents.split(None, 1)
    if len(bits) != 2:
        raise TemplateSyntaxError, "'if' statement requires at least one argument"
    expression = bits[1]
    variables = set([ parser.compile_filter(x) for x in variable_re.findall(expression) if x not in ('and', 'or', 'not', 'in') and not string_re.match(x) ])
    nodelist_true = parser.parse(('else', 'endif'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfNode(expression, variables, nodelist_true, nodelist_false)
do_if = register.tag(TAGNAME, do_if)
