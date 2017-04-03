$(document).ready(function(){
    var root  = $('#schema'),
        form  = $('.form'),
        flash = $('.flash'),
        url_base = $('body').data('url-base'),
        _csrf = form.children('input[name="_csrf"]'),
        _name = form.find('input[name="_collection"]'),
        _desc = form.find('input[name="_description"]'),
        _prev = form.find('input[name="_preview"]'),
        _send = form.find('input[name="_send"]'),
        _lang = form.find('#langs');
    
    // setup preview
    _prev.click(function(event){
        schema = {
            '_order': [],
            '_label': _desc.val()
        };
        processSchema(root, '');
        flash.css('display','none')
             .html(JSON.stringify(schema, null, ' ') )
             .fadeIn('fast');
        event.preventDefault();
    });
    
    // setup ajax
    _send.click(function(event){
        schema = {
            '_order': [],
            '_label': _desc.val()
        };
        processSchema(root, '');
        
        var langs = [];
        _lang.find('input:checked').each(function()
        {
            langs.push($(this).val());
        });
        collection = {
            '_name': _name.val(),
            '_langs': langs,
            '_schema': schema,
            '_csrf': _csrf.val()
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: url_base+'add/collection',
            data: JSON.stringify(collection),
            success: function(data){
                flash.css('display','none')
                     .html(data)
                     .fadeIn('fast');
                setTimeout(function(){window.location.replace(url_base+"collections")}, 1500);
            },
            error: function (xhr, status, error){
                try{
                    var response = JSON.parse(xhr.responseText);
                    flash.css('display','none')
                         .html(response.message)
                         .fadeIn('fast');
                    _csrf.val(response.csrf);
                } catch (err){
                    flash.css('display','none')
                         .html(xhr.responseText)
                         .fadeIn('fast');
                }
            }
        });
        event.preventDefault();
    });
    
    root.append(renderField());
});
