$(document).ready(function(){
    var root  = $('#schema'),
        form  = $('.form'),
        flash = $('.flash'),
        url_base = $('body').data('url-base'),
        _csrf = form.children('input[name="_csrf"]'),
        _name = form.children('input[name="_collection"]'),
        _desc = form.find('input[name="_description"]'),
        _prev = form.find('input[name="_preview"]'),
        _send = form.find('input[name="_send"]');
        
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
        collection = {
            '_schema': schema, 
            '_csrf': _csrf.val()
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: url_base+'edit/collection/'+ _name.val(),
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
    
    // setup fields dynamics
    root.find('.field').each(function()
    {
        var field = $(this),
            row = field.children('.row'),
            setup = row.children('#setup');

        row.children('.trigger.clone').click(function(){
            field.after(renderField());
        });

        row.children('.trigger.del').click(function(){
            field.remove();
        })

        setup.children().click(function(){
            $(this).toggleClass('on');
        });
    });
});
