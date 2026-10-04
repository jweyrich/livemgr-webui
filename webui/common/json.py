from __future__ import absolute_import # or `import json` would import this module
import json

class ComplexTypeEncoder(json.JSONEncoder):
	def default(self, obj):
		#print 'Serializing %s' % repr(obj)
		if hasattr(obj, 'to_json'):
			return obj.to_json()
		return json.JSONEncoder.default(self, obj)
