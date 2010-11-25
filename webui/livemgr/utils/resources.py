from django.conf import settings

class Resources:
	_media = settings.MEDIA_URL
	img_trans1x1 = _media + 'img/trans1x1.gif'
	tag_img_sucess = "<img class='icon success' src='%s' />" % img_trans1x1
	tag_img_accept = "<img class='icon accept' src='%s' />" % img_trans1x1
	tag_img_accept_gray = "<img class='icon accept-gray' src='%s' />" % img_trans1x1
	tag_img_status_away = "<img class='icon status-away' src='%s' />" % img_trans1x1
	tag_img_status_busy = "<img class='icon status-busy' src='%s' />" % img_trans1x1
	tag_img_status_offline = "<img class='icon status-offline' src='%s' />" % img_trans1x1
	tag_img_status_online = "<img class='icon status-online' src='%s' />" % img_trans1x1
	tag_img_tick = "<img class='icon tick' src='%s' />" % img_trans1x1
	tag_img_cross = "<img class='icon cross' src='%s' />" % img_trans1x1
