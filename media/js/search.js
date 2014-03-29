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

var Search = {
	current_criteria: null,
	onComplete: null,
	_onCompleteInternal: function() {
		Search.hookLinks();
		if (typeof(Search.onComplete) == 'function')
			Search.onComplete();
	},
	init: function() {
		if (window.location.hash == '#search') {
			$('#search').hide();
			$('#search_adv').show();
		}
		// Key bindings
		$('#search label:first').attr('accesskey', 'f');
		$('#search a#advanced').attr('accesskey', 'a');
		$('#search a#create').attr('accesskey', 'n');
		// Events
		$('#search a#advanced').click(function() {
			$('#search').hide('blind', { direction : 'vertical' }, 200);
			$('#search_adv').show('blind', { direction : 'vertical' }, 200);
			$('#search label:first').removeAttr('accesskey');
			$('#search_adv label:first').attr('accesskey', 's');
			$('#search a#advanced').removeAttr('accesskey');
			$('#search_adv a#simple').attr('accesskey', 'b');
		});
		$('#search_adv a#simple').click(function() {
			$('#search_adv').hide('blind', { direction : 'vertical' }, 200);
			$('#search').show('blind', { direction : 'vertical' }, 200);
			$('#search label:first').attr('accesskey', 's');
			$('#search_adv label:first').removeAttr('accesskey');
			$('#search_adv a#simple').removeAttr('accesskey');
			$('#search a#advanced').attr('accesskey', 'a');
		});
		Search.hookLinks();
	},
	search: function(form, url) {
		if (form != null)
			Search.current_criteria = $(form).serialize();
		$.ajax({
			type: 'POST',
			url: url,
			data: Search.current_criteria,
			dataType: 'html',
			success: function(response) {
				$('#list').html($('#list', response));
				Search._onCompleteInternal();
			},
			error: function(req, status, error) {
				alert('Error '+req.status+': '+req.responseText);
			}
		});
		return false;
	},
	searchViaLink: function() {
		return Search.search(null, this.href);
	},
	hookLinks: function() {
		// Hook sort & paging links
		$('#list thead tr a.sort').click(Search.searchViaLink);
		$('#list tfoot ul.pagination a').click(Search.searchViaLink);
	}
};

$(document).ready(Search.init);
