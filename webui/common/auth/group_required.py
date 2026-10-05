"""
	Based on: http://djangosnippets.org/snippets/1703/
	Author: msanders
	Posted: August 27, 2009

	This snippet provides a @group_required decorator. You can pass in multiple
	groups, for example:
	
	@group_required('admins','editors')
	def myview(request, id):
	...
	Note: the decorator is based on the snippet here but extends it checking
	first that the user is logged in before testing for group
	membership - user_passes_test does not check for this by default.
	
	It is important to check that the user is first logged in, as anonymous
	users trigger an AttributeError when the groups filter is executed.
"""

from django.contrib.auth.decorators import user_passes_test
import django

def group_required(*group_names):
	"""Requires user membership in at least one of the groups passed in."""
	def in_groups(u):
		# Django 1.10 turns is_authenticated into a property, and deprecates
		# calling it. Before 1.10 it's a method, which is always truthy.
		authenticated = u.is_authenticated if django.VERSION >= (1, 10) else u.is_authenticated()
		if authenticated:
			if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
				return True
		return False
	return user_passes_test(in_groups)
