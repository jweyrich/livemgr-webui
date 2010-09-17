from django.utils.safestring import mark_safe
from webui.imdata.models.acl import Acl
from webui.imdata.models.user import lookup_user_status
from webui.imdata.utils.resources import Resources
import socket
import struct

def _default(value):
	raise "Unhandled value: %s" % value
	
def format_boolean(value):
	img = {
		True: lambda x: Resources.img_accept,
		False: lambda x: Resources.img_accept_gray,
	}.get(value, _default)(value)
	if not img:
		return ""
	return mark_safe("<img src='%s' />" % img)

def format_acl_action(value):
	img = {
		Acl.ACTION_ALLOW: lambda x: Resources.img_tick,
		Acl.ACTION_BLOCK: lambda x: Resources.img_cross,
	}.get(value, _default)(value)
	if not img:
		return ""
	return mark_safe("<img src='%s' />" % img)

def format_user_status(value):
	status = lookup_user_status(value)
	if not status:
		return "" 
	img = {
		'NLN': lambda x: Resources.img_online,
		'BSY': lambda x: Resources.img_busy,
		'IDL': lambda x: Resources.img_away,
		'AWY': lambda x: Resources.img_away,
		'BRB': lambda x: Resources.img_away,
		'PHN': lambda x: Resources.img_busy,
		'LUN': lambda x: Resources.img_away,
		'HDN': lambda x: Resources.img_offline,
		'FLN': lambda x: Resources.img_offline,
	}.get(status[0], _default)(status[0])
	if not img:
		return ""
	text = unicode(status[1]).encode('utf-8', 'strict') 
	return mark_safe("<img src='%s' /> %s" % (img, text))

def ip_long_to_str(ip_as_long):
	#return socket.inet_ntoa(struct.pack('L', socket.ntohl(ip_as_long)))
	# We decided to store it as BigEndian on the database
	return socket.inet_ntoa(struct.pack('L', ip_as_long))
