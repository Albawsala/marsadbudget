var collection = null, doc_id = null;


$(document).ready(function()
{
    collection = $('#content').data('collection');
    doc_id = $('#content').data('doc');
    form = $('.form');
    flash = $('.flash');
    url_base = $('body').data('url-base');
    url_suffix = form.data('collection')+'/'+form.data('id');
    url = url_base+'edit/document/'+url_suffix;
    
    setInterval(
        function(){ $.ajax({ url: url_base+'touch/document/'+url_suffix}) },
        60 * 1000
    );
    
    init();
});
