/**
 * Color API
 * by Jardel Weyrich <jweyrich@gmail.com>
 *
 * Color and ColorSerie.
 */

function Color(color) {
	var r = 0,
		g = 0,
		b = 0;
	this.fromRGB = function(r, g, b) {
		this.r = r; this.g = g; this.b = b;
		return this;
	};
	this.add = function(color) {
		this.r += color.r; this.g += color.g; this.b += color.b;
		return this;
	};
	this.addRGB = function(r, g, b) {
		this.r += r; this.g += g; this.b += b;
		return this;
	};
	this.toHex = function() {
	    var r = this.r.toString(16);
	    var g = this.g.toString(16);
	    var b = this.b.toString(16);
	    if (r.length == 1) r = '0' + r;
	    if (g.length == 1) g = '0' + g;
	    if (b.length == 1) b = '0' + b;
	    return '#' + r + g + b;
	};
	this._decompose = function(color) {
		if (color == undefined)
			return;
		if (typeof(color) == 'number') {
			this.r = (color & 0xFF0000) >> 16;
			this.g = (color & 0x00FF00) >> 8;
			this.b = color & 0x0000FF;
		} else {
			alert('Invalid color input.');
			// My mind told me to not use alert(), but I didn't care.
		}
	};
	this._decompose(color);
}

function ColorSerie() {
	var fromColor, toColor;
	this.from = function(fromColor) {
		this.fromColor = fromColor;
		return this;
	};
	this.to = function(toColor) {
		this.toColor = toColor;
		return this;
	};
	this.get = function(samples) {
		var fromColor = new Color(this.fromColor);
		var toColor = new Color(this.toColor);
		var diffColor = new Color().fromRGB(
			toColor.r - fromColor.r,
			toColor.g - fromColor.g,
			toColor.b - fromColor.b
		);
		var stepColor = new Color().fromRGB(
			Math.floor(diffColor.r / (samples-1)),
			Math.floor(diffColor.g / (samples-1)),
			Math.floor(diffColor.b / (samples-1))
		);
		var result = new Array();
		result.push(fromColor.toHex());
		for (var i=1; i<samples-1; i++) {
			fromColor.add(stepColor);
			result.push(fromColor.toHex());
		}
		result.push(toColor.toHex());
		delete stepColor;
		delete diffColor;
		delete toColor;
		delete fromColor;
		return result;		
	};
}
