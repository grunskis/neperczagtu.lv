jQuery.fn.limitMaxlength = function(options){

    var settings = jQuery.extend({
	attribute: "maxlength",
	onLimit: function(){},
	onEdit: function(){}
    }, options);

    // Event handler to limit the textarea
    var onEdit = function(){
	var textarea = jQuery(this);
	var maxlength = parseInt(textarea.attr(settings.attribute));

	if(textarea.val().length > maxlength){
	    textarea.val(textarea.val().substr(0, maxlength));

	    // Call the onlimit handler within the scope of the textarea
	    jQuery.proxy(settings.onLimit, this)();
	}

	// Call the onEdit handler within the scope of the textarea
	jQuery.proxy(settings.onEdit, this)(maxlength - textarea.val().length);
    }

    this.each(onEdit);

    return this.keyup(onEdit).keydown(onEdit).focus(onEdit);
};

$(document).ready(function(){
    var onEditCallback = function(remaining){
        $('.remaining').text(remaining);

        if (remaining > 0) {
    	    $(this).css('background-color', 'white');
        }
    }

    var onLimitCallback = function(){
        $(this).css('background-color', '#ed145b');
    }

    $('textarea[maxlength]').limitMaxlength({
        onEdit: onEditCallback,
        onLimit: onLimitCallback,
    });
});

