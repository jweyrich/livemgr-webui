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
