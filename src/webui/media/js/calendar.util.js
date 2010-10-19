if (typeof gettext == 'undefined') {
	//gettext = function(msgid) { return msgid; };
	// Temporary workaround for http://code.djangoproject.com/ticket/5494
	gettext = function(msgid) {
		var lang = i18nUtil.langCode;
		switch (lang) {
			case 'pt-BR':
				switch (msgid) {
					case 'Today': return 'Hoje'
					default: return msgid
				}
			default:
				return msgid;
		}
	}
}

var CalendarUtil = {
	date_format: null,
	date_format_js: null,
	init: function() {
		CalendarUtil._localize($('#language select').val());
		$('.datepicker').each(CalendarUtil._addCalendar);
	},
	dateNow: function(selector) {
		var date = new Date().format(CalendarUtil.date_format_js);
		$(selector).val(date);
		$(selector).trigger('focus');
	},
	_localize: function(langCode) {
		// Download localization from http://jquery-ui.googlecode.com/svn/trunk/ui/i18n/
		var lang = i18nUtil.langCode;
		if (lang == 'en') {
			CalendarUtil.date_format = 'mm/dd/yy';
		} else {
			$.datepicker.setDefaults($.datepicker.regional[lang]);
			CalendarUtil.date_format = $.datepicker.regional[lang].dateFormat;
		}
		CalendarUtil.date_format_js = CalendarUtil.date_format.replace('yy', 'yyyy');
	},
	_addCalendar: function() {
		var field_selector = '#' + this.id;
		// TODO: Use $('selector').after('<bla>...') ???
		var today_link = document.createElement('a');
		var calendar_img = document.createElement('img');
		var div = document.createElement('div');

		$(today_link).attr('href', 'javascript:CalendarUtil.dateNow(\''+field_selector+'\');');
		$(today_link).css('text-decoration', 'none');
		$(today_link).append(document.createTextNode(gettext('Today')));

		$(calendar_img).attr('src', '/media/img/django/icon_calendar.gif');
		$(calendar_img).css('vertical-align', 'middle');
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
			dateFormat: CalendarUtil.date_format,
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

$(document).ready(CalendarUtil.init);
