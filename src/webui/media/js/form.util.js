var FormUtil = {
	make_field_hint : function(parent, field_id) {
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
