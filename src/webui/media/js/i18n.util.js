
var i18nUtil = {
	langCode: 'en',
	init: function() {
		var active_language = $('#language select').val();
		i18nUtil.change_language(active_language);
	},
	change_language: function(langCode) {
		i18nUtil.langCode = i18nUtil._fromRFC3282_toISO3166(langCode);
	},
	_fromRFC3282_toISO3166: function(langCode) {
		var arr = langCode.split('-', 2);
		if (arr.length != 2 || arr[1].length != 2)
			return langCode;
		return arr[0] + '-' + arr[1].toUpperCase();
	}
};

$(document).ready(i18nUtil.init);
