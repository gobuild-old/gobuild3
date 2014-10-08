/* javascript */
$(function(){
	$(document).on("click", "input.click-select", function(e) {
		$(e.target).select();
	});

	$('[data-toggle=tooltip]').mouseover(function() {
		$(this).tooltip('show');
	})


	if (!String.prototype.format) {
	  String.prototype.format = function() {
		var args;
		args = arguments;
		if (args.length === 1 && args[0] !== null && typeof args[0] === 'object') {
		  args = args[0];
		}
		return this.replace(/{([^}]*)}/g, function(match, key) {
		  return (typeof args[key] !== "undefined" ? args[key] : match);
		});
	  };
	};
});
