/*
 * Copyright (C) 2010 Jardel Weyrich
 *
 * This file is part of livemgr-webui.
 *
 * livemgr-webui is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * livemgr-webui is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
 *
 * Authors:
 *   Jardel Weyrich <jweyrich@gmail.com>
 */

/**
 * Depends on:
 *   i18n.min.js
 *   jquery-ui-1.8.2.custom.min.js
 *   jquery.ui.datepicker-<LANG>.min.js
 */
var Calendar = {
	init: function() {
		$('.datepicker').each(Calendar._addCalendar);
	},
	dateNow: function(selector, format) {
		var date = new Date().format(format);
		$(selector).val(date);
		$(selector).trigger('focus');
	},
	getLocalizedFormat: function(extended_year) {
		var lang = i18n.langCode;
		if (lang === 'en')
			lang = '';
		// This depends on specific localization files (see layout_extra.html)
		var format = $.datepicker.regional[lang].dateFormat;
		return extended_year === true ? format.replace('yy', 'yyyy') : format;
	},
	_addCalendar: function() {
		var field_selector = '#' + this.id;
		// TODO(jweyrich): Any advantage using $('selector').after('<tag>...') ?
		var today_link = document.createElement('a');
		var calendar_img = document.createElement('img');
		var div = document.createElement('div');
		var date_format = Calendar.getLocalizedFormat();
		var date_format_yyyy = Calendar.getLocalizedFormat(true);

		$(today_link).attr('href', 'javascript:Calendar.dateNow(\''
			+field_selector+'\', \''+date_format_yyyy+'\');');
		$(today_link).css('text-decoration', 'none');
		$(today_link).append(document.createTextNode(gettext('Today')));

		$(calendar_img).attr('src', '/media/img/trans1x1.gif');
		$(calendar_img).attr('class', 'icon calendar');
		//$(calendar_img).css('vertical-align', 'middle');
		$(calendar_img).css('cursor', 'pointer');

		$(div).addClass('datepicker');
		$(div).append(document.createTextNode('\240'));
		$(div).append(today_link);
		$(div).append(document.createTextNode('\240|\240'));
		$(div).append(calendar_img);
		$(div).insertAfter(this);

		$(this).css('float', 'left');
		$(this).css('position', 'relative');
		$(this).css('z-index', '1');
		$(this).attr('maxlength', $(this).attr('format').length);
		$(this).datepicker({
			dateFormat: date_format,
			showOn: 'none',
			showAnim: 'blind',
			onSelect: function(dateText, inst) {
				$(field_selector).trigger('focus');
			}
		});
		$(calendar_img).click(function() {
			$(field_selector).datepicker('show');
		});
	}
};

$(document).ready(Calendar.init);
