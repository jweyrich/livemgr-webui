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
 * GoogleChartTools API
 * by Jardel Weyrich <jweyrich@gmail.com>
 *
 * This generates those awful URLs ;-)
 * Supports Bar charts only.
 *
 * References:
 * 	http://code.google.com/apis/chart/docs/chart_wizard.html
 * 	http://code.google.com/apis/chart/docs/data_formats.html#axis_scale
 *  http://code.google.com/apis/chart/docs/gallery/bar_charts.html#gcharts_legend
 */

function BarChart(target) {
	// Make this _const_ whenever IE starts supporting. Never? :-)
	var params = {
		url: 'http://chart.apis.google.com/chart?',
		title: '&chtt={0}', // {string}
		margins: '&chma={0}', // {[left,right,top,bottom]}
		size: '&chs={0}', // {[w,h]}
		bar_width: '&chbh={0}', // {automatic=a || relative=r || specify=%d}
		bar_options: '&cht=b{0}', // {horizontal=h || vertical=v + stacked=s || grouped=g}
		data: {
			legend_position: '&chdlp={0}', // {left=l || right=r || top=t || bottom=b}
			axes: {
				type: '&chxt={0}', // {x,y,r,t}
				labels: '&chxl={0}', // {[label_1,label_2,...,label_n]}
				values: '&chd=t:{0}',  // {[value_1,value_2,...,value_n]}
				color: '&chco={0}', // {color} eg: 0x4D89F9
				scale: '&chds={0}', // {[x,y]}
				range: '&chxr={0}', // {index},{x},{y} | ...
				style: '&chxs={0}', // {index} {labels.color} {labels.font_size} {labels.alignment} {_ || l + t} {ticks.color}
				//legend: '&chdl={0}', // {string}
			},
		},
	};
	var target = target;
	this.draw = function(options) {
		target.innerHTML = '<img src="'+this._formatUrl(options)+'">';
	};
	this._formatLabelsInternal = function(index, labels) {
		if (labels == null || labels == undefined || labels.length == 0)
			return '';
		var result = index + ':';
		for (i in labels) {
			// Inverse order
			result += '|' + encodeURIComponent(labels[labels.length-i-1]);
		}
		return result;
	};
	this._formatLabels = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var tmp = this._formatLabelsInternal(i, options.data.axes[i].labels);
			if (tmp != '')
				array.push(tmp);
		}
		var result = '';
		if (array.length > 0)
			result = params.data.axes.labels.format(array.join('|'));
		delete array;
		return result;
	};
	this._formatValues = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var obj = options.data.axes[i].values;
			if (obj == undefined || obj == null || obj.length == 0)
				obj = [-i];
			array.push(obj.join(','));
		}
		var result = params.data.axes.values.format(array.join('|'));
		delete array;
		return result;
	};
	this._formatColors = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var obj = options.data.axes[i].color;
			if (obj == undefined || obj == null)
				obj = 0x4D89F9;
			array.push(this.colorToStr(obj));
		}
		var result = params.data.axes.color.format(array.join(','));
		delete array;
		return result;
	};
	this._formatScales = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var obj = options.data.axes[i].scale;
			if (obj == undefined || obj == null || obj.length == 0)
				obj = [0,100];
			array.push(obj);
		}
		var result = params.data.axes.scale.format(array.join(','));
		delete array;
		return result;
	};
	this._formatRanges = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var obj = options.data.axes[i].range;
			if (obj == undefined || obj == null || obj.length == 0)
				obj = [0,100];
			obj.unshift(i);
			array.push(obj);
		}
		var result = params.data.axes.range.format(array.join('|'));
		delete array;
		return result;
	};
	this._formatStyles = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var obj = options.data.axes[i].style;
			if (obj == undefined || obj == null || obj.length == 0)
				obj = {};
			// Default values
			if (obj.labels == undefined)
				obj.labels = {};
			if (obj.labels.color == undefined)
				obj.labels.color = 0x676767;
			if (obj.labels.font_size == undefined)
				obj.labels.font_size = 11.5
			if (obj.labels.alignment == undefined)
				obj.labels.alignment = 0;
			if (obj.line == undefined)
				obj.line = {};
			if (obj.line.show == undefined)
				obj.line.show = true;
			if (obj.ticks == undefined)
				obj.ticks = {};
			if (obj.ticks.show == undefined)
				obj.ticks.show = false;
			if (obj.ticks.color == undefined)
				obj.ticks.color = 0x676767;

			var tmp = new Array();
			tmp.push(i);
			tmp.push(this.colorToStr(obj.labels.color));
			tmp.push(obj.labels.font_size);
			tmp.push(obj.labels.alignment);
			var lt = '';
			if (obj.line.show)
				lt += 'l';
			if (obj.ticks.show)
				lt += 't';
			if (!obj.line.show && !obj.ticks.show)
				lt += '_';
			tmp.push(lt);
			tmp.push(this.colorToStr(obj.ticks.color));
			array.push(tmp);
			delete tmp;
		}
		result = params.data.axes.style.format(array.join('|'));
		delete array;
		return result;
	};
	this._formatAxes = function(options) {
		var array = new Array();
		for (i in options.data.axes) {
			var obj = options.data.axes[i].type;
			if (obj == undefined || obj == null || obj === '')
				obj = 'x';
			array.push(obj);
		}
		var result = params.data.axes.type.format(array.join(','));
		delete array;
		return result;
	};
	this._formatUrl = function(options) {
		var result = params.url;
		result += this._formatLabels(options);
		result += this._formatRanges(options); //options.ranges;
		result += this._formatStyles(options);
		result += this._formatAxes(options);
		result += params.bar_width.format(options.bar_width);
		result += params.size.format(options.size.join('x'));
		result += params.bar_options.format(options.bar_options);
		result += this._formatColors(options);
		result += this._formatScales(options);
		result += this._formatValues(options);
		result += params.data.legend_position.format(options.data.legend_position);
		result += params.margins.format(options.margins);
		result += params.title.format(encodeURIComponent(options.title));
		return result;
	};
	this.colorToStr = function(color) {
		var r = (color & 0xFF0000) >> 16;
		var g = (color & 0x00FF00) >> 8;
		var b = color & 0x0000FF;
	    r = r.toString(16);
	    g = g.toString(16);
	    b = b.toString(16);
	    if (r.length == 1) r = '0' + r;
	    if (g.length == 1) g = '0' + g;
	    if (b.length == 1) b = '0' + b;
	    return r + g + b;
	};
	this.getScale = function(rows, getter) {
		if (getter == undefined)
			getter = function(row){return row[0];};
		var min = getter(rows[0]);
		var max = getter(rows[0]);
		for (i in rows) {
			var value = getter(rows[i]);
			if (value < min)
				min = value;
			if (value > max)
				max = value;
		}
		return [min, max];
	};
	this.roundUp = function(value) {
		var factor = 1;
		while (Math.floor(value / factor) >= 10) {
			factor *= 10;
		}
		var mod = value % factor;
		if (mod != 0)
			value = value + factor - mod;
		return value;
	};
}
