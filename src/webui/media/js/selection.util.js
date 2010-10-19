var SelectionUtil = {
	_selection_count: function() {
		return $('input[type="checkbox"][name="selection"]:not([disabled]):checked').length;
	},
	_selection_changed: function() {
		if (SelectionUtil._selection_count() == 0) {
			$('div.actions .action').attr('disabled', 'true');	
		} else {
			$('div.actions .action').removeAttr('disabled');
		}
	},
	select_one: function(caller) {
		SelectionUtil._selection_changed();
	},
	select_all: function(caller) {
		$('input[type="checkbox"][name="selection"]:not([disabled])')
			.attr('checked', caller.checked);
		SelectionUtil._selection_changed();
	},
	_exec_action: function(args) {
		$.ajax({
			type: 'POST',
			url: args.url,
			data: $('#list tbody tr').find('input[type="checkbox"][name="selection"]').serialize(),
			dataType: 'html',
			success: function(response) {
				// FIXME: Chromium has a problem with AJAX
				// Steps to reproduce:
				// 	1. Select 1+ items;
				//	2. Navigate to another page;
				//	3. Go back to the previous page;
				//	4. Apply any action on the selected items;
				// What happens:
				//	The #list isn't reloaded.
				// What is expected:
				//	It should be reloaded.
				if (true) {
					window.location.reload();
				} else {
					$.get(window.location, function(response) {
						$('#list').html($('#list', response));
						SearchUtil.hook_links();
						if (typeof SearchUtil.afterSearchFunc == 'function') {
							SearchUtil.afterSearchFunc();
						}
					});
				}
			},
			error: function(req, status, error) {
				alert('Error '+req.status+': '+req.responseText);
				this.disabled = false;
			}
		});		
	},
	show_actions: function(selector) {
		if (typeof(selector) == 'Array') {
			for (s in selector)
				SelectionUtil.show_actions(s);
		} else {
			$('div.actions '+selector).css('display', 'inline');
		}
	},
	bind_action_click: function(args) {
		$('div.actions '+args.selector).click(function() {
			this.disabled = true;
			SelectionUtil._exec_action(args);
			this.disabled = false;
		});
	},
	bind_action_click_confirm: function(args) {
		var callbacks = {
			yes: function() {
				SelectionUtil._exec_action(args);
				args.caller.disabled = false;
			},
			no: function() {
				if (typeof(args.hide) == 'function')
					args.hide();
				args.caller.disabled = false;
			}
		};
		$('div.actions '+args.selector).click(function() {
			if (typeof(args.show) == 'function') {
				args.caller = this;
				this.disabled = true;
				var items = $('#list tbody tr').find('[name="selection"]:checked');
				args.show(this, callbacks, items);
			}
		});
	},
	bind_list_tr_click: function(args) {
		$('#list tbody tr').click(function(event) {
			if ($(event.target).is('a') || event.target.type == 'checkbox')
				return;
			var id = $(this).find('[name="selection"]').val();
			if (id == undefined)
				return;
			id = encodeURIComponent(id);
			if (args.url)
				window.location = args.url.format(id);
			else if (args.callback)
				args.callback(id);
		});
	}
};

var SelectFilter = {
	init: function(field_id) {
		var target = document.getElementById(field_id);
		var filter = document.getElementById(field_id+'_filter');
		$(filter).keyup(function(e) { SelectFilter.filter_key_up(e, field_id); });
		SelectBox.init(field_id);
	},
	filter_key_up: function(event, field_id) {
		var filter = document.getElementById(field_id+'_filter');
        SelectBox.filter(field_id, filter.value);
        return true;
	}
};
