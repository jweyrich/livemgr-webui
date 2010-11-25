function getWindowSize() {
	var width;
	var height;
	if (typeof window.innerWidth != 'undefined') {
		// the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight
		width = window.innerWidth,
		height = window.innerHeight
	} else if (typeof document.documentElement != 'undefined'
		&& typeof document.documentElement.clientWidth !=
		'undefined' && document.documentElement.clientWidth != 0)
	{
		// IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)
		width = document.documentElement.clientWidth,
		height = document.documentElement.clientHeight
	} else {
		// older versions of IE
		width = document.getElementsByTagName('body')[0].clientWidth,
		height = document.getElementsByTagName('body')[0].clientHeight
	}
	return [width, height];
}
