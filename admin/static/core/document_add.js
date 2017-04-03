var collection = null, doc_id = null;

$(document).ready(function()
{
	collection = $('#content').data('collection');
    form = $('.form');
    flash = $('.flash');
    url_base = $('body').data('url-base');
    url_suffix = form.data('collection');
    url = url_base+'add/document/'+url_suffix;
    init();
});
