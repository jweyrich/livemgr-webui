# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Jardel Weyrich
#
# This file is part of livemgr-webui.
#
# livemgr-webui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# livemgr-webui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jardel Weyrich <jweyrich@gmail.com>

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
