from django import template
from django.forms.widgets import CheckboxInput
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='field_type')
def filter_field_type(field, type):
	try:
		t = field.field.widget.__class__.__name__
		return t.lower() == type
	except:
		pass
	return False

@register.filter(name='is_checkbox')
def filter_is_checkbox(field):
	return isinstance(field.field.widget, CheckboxInput)

@register.filter(name='index')
def filter_index(array, index):
	"Returns the value from the array at the given index"
	return array[index]

@register.filter(name='index_start')
def filter_index_start(array, index_start):
	"Returns a concatenated string containing all values"
	"from the array starting at the given index"
	return ' '.join(array[index_start:])

@register.filter(name='split')
@stringfilter
def filter_split(str, separator=' '):
	"Split the string using a separator and"
	"return the results in an array"
	return str.split(separator)

@register.filter(name='strip')
@stringfilter
def filter_strip(str, arg):
	"Removes all values of arg from the given string"
	return str.replace(arg, '')

@register.filter(name='selected_if')
@stringfilter
def filter_selected_if(value, arg):
	if (value == arg):
		return mark_safe("selected")
	else:
		return mark_safe("")
filter_selected_if.is_safe = True

@register.filter(name='escape')
def filter_escape(value, autoescape=None):
	"Returns the respective escaped value"
	if autoescape:
		esc = conditional_escape
	else:
		esc = lambda x: x
	return esc(value)
filter_escape.needs_autoescape = True

@register.filter(name='langcode')
@stringfilter
def filter_langcode(value):
	arr = value.split('-', 2);
	if len(arr) != 2 or len(arr[1]) != 2:
		return value
	return arr[0] + '-' + arr[1].upper();	

@register.filter(name='dict_get')
def filter_dict_get(dict, key):
	return dict.get(key)
