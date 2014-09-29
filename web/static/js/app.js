/* javascript */
$(function(){
	$(document).on("click", "input.click-select", function(e) {
		$(e.target).select();
	});

	$('[data-toggle=tooltip]').mouseover(function() {
		$(this).tooltip('show');
	})
});
