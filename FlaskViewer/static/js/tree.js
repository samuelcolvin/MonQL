'use strict';

function populatetree(url){
	var $tree = $('#tree');
	$.getJSON(url, function(data) {
		console.log(data);
		$tree.tree({data: data.DATA});
		if (typeof(data.ERROR) != 'undefined'){
			bootbox.alert(str2html(data.ERROR));
		}
	}).fail(function(e) {
		bootbox.alert('Connection Error, check the server is running and the url is correct.');
	});
}

function str2html(str){
	var re = new RegExp('\n', 'g');
	return '<p>' + str.replace(re,'</p>\n<p>') + '</p>';
}