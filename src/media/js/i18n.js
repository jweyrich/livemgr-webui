var i18n = {
	langCode: 'en',
	changeLanguage: function(langCode) {
		i18n.langCode = i18n.fromRFC3282toISO3166(langCode);
	},
	fromRFC3282toISO3166: function(langCode) {
		if (langCode == undefined)
			return i18n.langCode;
		var arr = langCode.split('-', 2);
		if (arr.length != 2 || arr[1].length != 2)
			return i18n.langCode;
		return arr[0] + '-' + arr[1].toUpperCase();
	}
};
