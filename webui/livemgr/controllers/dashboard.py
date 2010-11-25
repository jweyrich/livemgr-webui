from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from webui.common.db.query import fetchall_to_dict, fetchone_to_dict
from webui.common.decorators.rest import rest_get, rest_multiple
from webui.common.http import method
from webui.common.json import ComplexTypeEncoder

class DataTree:
	def __init__(self, limit, period, localdt=datetime.now()):
		self.total_users_online = query_total_users_online()
		self.total_active_conversations = query_total_active_conversations()
		self.latest_conversations = query_latest_conversations(limit)
		self.most_active_users = query_most_active_users(limit, period, localdt)
	def to_json(self):
		return self.__dict__
	class LatestConversation:
		def __init__(self, dict):
			self.id = dict['id']
			self.msg_id = dict['msg_id']
			self.timestamp = dict['timestamp'].strftime('%H:%M:%S %p')
			self.user_id = dict['user_id']
			self.localim = dict['localim']
			self.remoteim = dict['remoteim']
			self.total = dict['total']
		def to_json(self):
			return self.__dict__
	class MostActiveUser:
		def __init__(self, dict):
			self.user_id = dict['user_id']
			self.username = dict['username']
			self.total = dict['total']
		def to_json(self):
			return self.__dict__

@rest_get
@login_required
@permission_required('livemgr.see_dashboard')
def index(request):
	data = DataTree(5, 'day', datetime.now())
	data = simplejson.dumps(data, cls=ComplexTypeEncoder)
	context_instance = RequestContext(request)
	template_name = 'dashboard/index.html'
	extra_context = {
		'menu': 'dashboard',
		'data': data
	}
	return render_to_response(template_name, extra_context, context_instance)

#@rest_post
@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('livemgr.see_dashboard')
def query(request):
	limit = int(request.POST.get('limit', '5'))
	period = request.POST.get('period', 'day')
	data = DataTree(limit, period)
	result = simplejson.dumps(data, cls=ComplexTypeEncoder)
	return HttpResponse(result, mimetype='application/json')

def query_total_users_online():
	query = "SELECT count(*) as total FROM users where status<>'FLN'"
	result = fetchone_to_dict(query)
	return result['total']

def query_total_active_conversations():
	query = "SELECT count(*) as total FROM conversations WHERE status=1"
	result = fetchone_to_dict(query)
	#print result['total']
	return result['total']

def query_latest_conversations(limit):
	query = """
			SELECT
				m.conversation_id AS id,
				MAX(m.id) as msg_id,
				MAX(m.timestamp) AS timestamp,
				c.user_id AS user_id,
				m.localim AS localim,
				m.remoteim AS remoteim,
				count(m.id) as total
			FROM conversations as c
			LEFT OUTER JOIN messages as m ON m.conversation_id = c.id
			WHERE
				YEAR(m.timestamp) = %(year)i
				AND MONTH(m.timestamp) = %(month)i
				AND DAYOFMONTH(m.timestamp) = %(day)i
			GROUP BY c.id
			ORDER BY m.timestamp DESC
			LIMIT 0, %(limit)i
		"""
	localdate = datetime.now().timetuple()
	query = query % {
		'year':  localdate.tm_year,
		'month': localdate.tm_mon,
		'day': localdate.tm_mday,
		'limit': limit
	}
	#print query
	result = fetchall_to_dict(query)
	return [DataTree.LatestConversation(r) for r in result]

def query_most_active_users(limit, period, initial_localdate=datetime.now()):
	period_cond = {
		'day': lambda x: """
			YEAR(timestamp) = %(year)i
			AND MONTH(timestamp) = %(month)i
			AND DAYOFMONTH(timestamp) = %(day)i
			""",
		'week': lambda x: "WEEKOFYEAR(timestamp) = %(week)i",
		'month': lambda x: """
			YEAR(timestamp) = %(year)i
			AND MONTH(timestamp) = %(month)i
			""",
		'year': lambda x: "YEAR(timestamp) = %(year)i",
	}.get(period, lambda x: None)(period)
	if not period_cond:
		return []
	query = """
			SELECT
				u.id AS user_id,
				m.localim AS username,
				count(m.id) AS total,
				m.timestamp AS timestamp
			FROM messages as m
			LEFT OUTER JOIN users as u ON u.username = m.localim
			WHERE 
				m.inbound = 0 AND
		""" + period_cond + """
			GROUP BY user_id
			ORDER BY total DESC
			LIMIT 0, %(limit)i
		"""
	weekofyear = initial_localdate.isocalendar()[1]
	localdate = initial_localdate.timetuple()
	query = query % {
		'year':  localdate.tm_year,
		'month': localdate.tm_mon,
		'week': weekofyear,
		'day': localdate.tm_mday,
		'limit': limit
	}
	#print query
	result = fetchall_to_dict(query)
	return [DataTree.MostActiveUser(r) for r in result]
