import types
from django import http

class http_dict(dict):
	def __init__(self, method_dict):
		assert isinstance(method_dict, http.QueryDict)
		super(http_dict, self).__init__()
		self.dict = method_dict
	def from_fields(self, keylist):
		assert isinstance(keylist, types.ListType)
		count = 0
		for k in keylist:
			val = self.dict.get(k)
			if val:
				count += 1
			self[k] = val
		return count