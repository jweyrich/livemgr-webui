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
 * Horizontal bar chart, drawn in the browser as inline SVG.
 *
 * It replaces googlecharts.js, which built URLs for Google's Image Charts API
 * (chart.apis.google.com). Google turned that API off in 2019. Drawing the
 * chart here also keeps the usernames from leaving the network.
 *
 * Usage:
 *	new BarChart(element).draw({
 *		title: 'Most Active Users',
 *		rows: [['alice@example.com', 44], ['bob@example.com', 29]], // top to bottom
 *		axis_label: 'messages'
 *	});
 */

function BarChart(target) {
	var SVG_NS = 'http://www.w3.org/2000/svg';
	var defaults = {
		size: [672, 220],
		color: '#7f9bca',
		text_color: '#676767',
		grid_color: '#e5e5e5',
		font_size: 11.5,
		padding: 10
	};

	function element(parent, name, attributes, text) {
		var node = document.createElementNS(SVG_NS, name);
		for (var key in attributes)
			node.setAttribute(key, attributes[key]);
		if (text !== undefined)
			node.textContent = String(text); // Not markup: usernames come from users
		parent.appendChild(node);
		return node;
	}

	// The step between ticks: 1, 2 or 5 times a power of 10, for at most `count` steps
	function tickStep(max, count) {
		var step = Math.pow(10, Math.floor(Math.log(max / count) / Math.LN10));
		var multipliers = [1, 2, 5, 10];
		for (var i = 0; i < multipliers.length; ++i) {
			if (max / (step * multipliers[i]) <= count)
				return Math.max(1, step * multipliers[i]);
		}
		return Math.max(1, step * 10);
	}

	this.draw = function(options) {
		var o = {};
		for (var key in defaults)
			o[key] = defaults[key];
		for (var key in options)
			o[key] = options[key];
		var width = o.size[0], height = o.size[1], pad = o.padding;

		target.innerHTML = '';
		var svg = element(target, 'svg', {
			width: width, height: height,
			viewBox: '0 0 ' + width + ' ' + height,
			role: 'img',
			'font-family': 'inherit',
			'font-size': o.font_size,
			fill: o.text_color
		});
		element(svg, 'title', {}, o.title);

		var top = pad;
		if (o.title) {
			element(svg, 'text', {
				x: width / 2, y: top + o.font_size + 2,
				'text-anchor': 'middle', 'font-size': o.font_size + 2, 'font-weight': 'bold'
			}, o.title);
			top += o.font_size + 2 + pad;
		}
		var bottom = height - pad - (o.axis_label ? o.font_size + 6 : 0) - o.font_size - 8;

		// Labels on the left, as wide as the widest one
		var labels = [];
		var label_width = 0;
		for (var i = 0; i < o.rows.length; ++i) {
			var label = element(svg, 'text', {'text-anchor': 'end'}, o.rows[i][0]);
			labels.push(label);
			var measured = label.getComputedTextLength ? label.getComputedTextLength() : 0;
			label_width = Math.max(label_width, measured || o.rows[i][0].length * o.font_size * 0.55);
		}
		label_width = Math.min(label_width, width / 2);
		var left = pad + label_width + 8;
		var right = width - pad - 40; // Room for the values

		// Scale and grid
		var max = 0;
		for (var i = 0; i < o.rows.length; ++i)
			max = Math.max(max, o.rows[i][1]);
		var step = tickStep(Math.max(max, 1), 5);
		var scale_max = Math.ceil(Math.max(max, 1) / step) * step;
		var x = function(value) { return left + (right - left) * value / scale_max; };
		for (var value = 0; value <= scale_max; value += step) {
			element(svg, 'line', {
				x1: x(value), x2: x(value), y1: top, y2: bottom,
				stroke: value ? o.grid_color : o.text_color
			});
			element(svg, 'text', {
				x: x(value), y: bottom + o.font_size + 4, 'text-anchor': 'middle'
			}, value);
		}
		element(svg, 'line', {x1: left, x2: right, y1: bottom, y2: bottom, stroke: o.text_color});
		if (o.axis_label) {
			element(svg, 'text', {
				x: (left + right) / 2, y: height - pad, 'text-anchor': 'middle'
			}, o.axis_label);
		}

		// Bars
		var band = (bottom - top) / Math.max(o.rows.length, 1);
		var bar_height = Math.min(band * 0.7, 28);
		for (var i = 0; i < o.rows.length; ++i) {
			var middle = top + band * (i + 0.5);
			var value = o.rows[i][1];
			labels[i].setAttribute('x', left - 8);
			labels[i].setAttribute('y', middle);
			labels[i].setAttribute('dominant-baseline', 'central');
			var bar = element(svg, 'rect', {
				x: left, y: middle - bar_height / 2,
				width: Math.max(x(value) - left, 1), height: bar_height,
				fill: o.color
			});
			element(bar, 'title', {}, o.rows[i][0] + ': ' + value);
			element(svg, 'text', {
				x: x(value) + 6, y: middle, 'dominant-baseline': 'central'
			}, value);
		}
	};
}
