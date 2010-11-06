/**
 * Depends on:
 *   search.min.js
 *   selectbox.min.js
 */
var Selection = {
	currentSelection: function() {
		return $('#list tbody tr')
			.find('input[type="checkbox"][name="selection"]:not([disabled]):checked');
	},
	_onChange: function() {
		if (Selection.currentSelection().length == 0) {
			$('div.actions .action').attr('disabled', 'true');	
		} else {
			$('div.actions .action').removeAttr('disabled');
		}
	},
	onSelect: function(caller) {
		Selection._onChange();
	},
	selectAll: function(caller) {
		$('input[type="checkbox"][name="selection"]:not([disabled])')
			.attr('checked', caller.checked);
		Selection._onChange();
	},
	_execAction: function(args) {
		$.ajax({
			type: 'POST',
			url: args.url,
			data: args.items.serialize(),
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
						Search._onCompleteInternal();
					});
				}
			},
			error: function(req, status, error) {
				alert('Error '+req.status+': '+req.responseText);
				this.disabled = false;
			}
		});		
	},
	showActions: function(selector) {
		if (typeof(selector) == 'Array') {
			for (s in selector)
				Selection.showActions(s);
		} else {
			$('div.actions '+selector).css('display', 'inline');
		}
	},
	bindActionClick: function(args) {
		$('div.actions '+args.selector).click(function() {
			this.disabled = true;
			if (args.items == undefined)
				args.items = Selection.currentSelection();
			Selection._execAction(args);
			this.disabled = false;
		});
	},
	bindActionClickConfirm: function(args) {
		var callbacks = {
			yes: function() {
				if (typeof(args.onConfirm) == 'function')
					args.onConfirm(args);
				else
					Selection._execAction(args);
				args.caller.disabled = false;
			},
			no: function() {
				if (typeof(args.onCancel) == 'function')
					args.onCancel(args);
				if (typeof(args.hide) == 'function')
					args.hide();
				args.caller.disabled = false;
			}
		};
		$('div.actions '+args.selector).click(function() {
			if (typeof(args.onShow) == 'function') {
				args.caller = this;
				this.disabled = true;
				if (args.items == undefined)
					args.items = Selection.currentSelection();
				args.onShow(this, callbacks, args.items);
			}
		});
	},
	bindListRowClick: function(args) {
		$('#list tbody tr').click(function(event) {
			if ($(event.target).is('a') || event.target.type == 'checkbox')
				return;
			var id = $(this).find('input[type="checkbox"][name="selection"]').val();
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
		$(filter).keyup(function(e) {
			SelectFilter.filterKeyUp(e, field_id);
		});
		SelectBox.init(field_id);
	},
	filterKeyUp: function(event, field_id) {
		var filter = document.getElementById(field_id+'_filter');
        SelectBox.filter(field_id, filter.value);
        return true;
	}
};
