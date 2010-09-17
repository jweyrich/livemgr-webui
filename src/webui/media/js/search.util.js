
var SearchUtil = {
	current_criteria: null,
	afterSearchFunc: null,
	afterSearch: function(func) {
		SearchUtil.afterSearchFunc = func; 
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
		$('#search_adv a#simple').attr('accesskey', 'b');
		// Events
		$('#search a#advanced').click(function() {
			$('#search').hide('blind', { direction : 'vertical' }, 200);
			$('#search_adv').show('blind', { direction : 'vertical' }, 200);
			$('#search label:first').removeAttr('accesskey');
			$('#search_adv label:first').attr('accesskey', 's');
		});
		$('#search_adv a#simple').click(function() {
			$('#search_adv').hide('blind', { direction : 'vertical' }, 200);
			$('#search').show('blind', { direction : 'vertical' }, 200);
			$('#search label:first').attr('accesskey', 's');
			$('#search_adv label:first').removeAttr('accesskey');
		});
		SearchUtil.hook_links();
	},
	search: function(form, url) {
		if (form != null)
			SearchUtil.current_criteria = $(form).serialize();
		$.ajax({
			type: 'POST',
			url: url,
			data: SearchUtil.current_criteria,
			dataType: 'html',
			success: function(response) {
				$('#list').html($('#list', response));
				SearchUtil.hook_links();
				if (typeof SearchUtil.afterSearchFunc == 'function') {
					SearchUtil.afterSearchFunc();
				}
			},
			error: function(req, status, error) {
				alert('Error '+req.status+': '+req.responseText);
			}
		});
		return false;
	},
	search_via_link: function() {
		return SearchUtil.search(null, this.href);
	},
	hook_links: function() {
		// Hook sort & paging links
		$('#list thead tr a.sort').click(SearchUtil.search_via_link);
		$('#list tfoot ul.pagination a').click(SearchUtil.search_via_link);
	}
};

$(document).ready(SearchUtil.init);
