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

var Form = {
	makeFieldHint: function(parent, field_id) {
		label = $(parent + ' label[for=' + field_id + ']');
		field = $(parent + ' #' + field_id);
		field.attr('title', label.attr('textContent'));
		field.focus(function() {
			$(parent + ' label[for=' + field_id + ']').hide();
		});
		field.blur(function() {
			if ($(this).val().length == 0)
				$(parent + ' label[for=' + field_id + ']').show();
		});
		label.click(function() {
			$(parent + ' #' + field_id).focus();
		});
		// NOTE: The following is required because Firefox keeps
		// form data whenever a page reload occurs.
		if (field.val().length > 0)
			$(parent + ' label[for=' + field_id + ']').hide();
	}
};
