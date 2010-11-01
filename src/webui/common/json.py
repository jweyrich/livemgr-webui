from django.utils import simplejson

class ComplexTypeEncoder(simplejson.JSONEncoder):
	def default(self, obj):
		#print 'Serializing %s' % repr(obj) 
		if hasattr(obj, 'to_json'):
			return obj.to_json()
		return simplejson.JSONEncoder.default(self, obj)
