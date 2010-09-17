
if (!String.prototype.format) {
	String.prototype.format = function() {
		var txt = this;
		for (var i = 0; i < arguments.length; i++) {
			var exp = new RegExp('\\{' + (i) + '\\}', 'gm');
			txt = txt.replace(exp, arguments[i]);
		}
		return txt;
	};
}

if (!String.format) {
	String.format = function() {
		for (var i = 1; i < arguments.length; i++) {
			var exp = new RegExp('\\{' + (i - 1) + '\\}', 'gm');
			arguments[0] = arguments[0].replace(exp, arguments[i]);
		}
		return arguments[0];
	};
}