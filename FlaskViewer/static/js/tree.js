'use strict';
function populatetree(){
	var $tree = $('#tree');
	desc = $('#description');
	var url = $tree.attr('data-url');
	$.getJSON(url, function(data) {
		console.log(data);
		$tree.tree({data: data.DATA}).bind('click', onclick);
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

var desc;
function onclick(event) {
		var node = $('#tree').tree('getSelectedNode');
		if (typeof(node.info) !== 'undefined'){
			desc.empty();
			node.info.forEach(function(info){
				desc.append('<h4>' + info[0] + '</h4>');
				info[1].forEach(function(prop){
					desc.append('<dt title="' + prop[0] + '">' + prop[0] + '</dt>');
					var value = $('<div/>').text(prop[1]).html();
					desc.append('<dd><pre>' + value + '</pre></dd>');
				});
			});
		}
}