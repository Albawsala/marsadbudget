var ministeres_scroll = 25;
var $ministeres;
var window_height;
var ministeres_height;
var $body;


$(document).ready(function()
{
	$ministeres = $('#ministeres');
    $body= $('body');

    if($body.data('endpoint') == 'ministere')
    {
        $ministeres.find('.ministère_'+$body.data('args').ministere_id).addClass('active');
    }

    window_height = $(window).height();
    ministeres_height = $ministeres.height() + 50;

	$ministeres.mousewheel(function(ev)
	{
        var ministeres_top = ($ministeres.data('top') || 0) + ev.deltaY * ministeres_scroll / Math.abs(ev.deltaY);
        ministeres_top = Math.min(0, ministeres_top);
        ministeres_top = Math.max(ministeres_top, window_height-ministeres_height);
        $ministeres.data('top', ministeres_top);
        $ministeres.css('top', ministeres_top+'px');
	})
	.mousedown(function(ev)
    {
        $ministeres
            .data('down', true)
            .data('x', ev.clientY)
            .data('top', parseInt($ministeres.css('top')));
            
        return false;
    })
    .hover(
    	function(){
            window.no_scroll = true;
            $body.addClass('ministeres-expand');
        },
    	function(){
            window.no_scroll = false;
            $body.removeClass('ministeres-expand');
        }
    )

    $ministeres.children()
    .mousedown(function(ev)
    {
        this._mousedown_ = true;
    })
    .mousemove(function(ev)
    {
        if (this._mousedown_)
            this._mousemove_ = true;
    })
    .click(function(ev)
    {
        this._mousedown_ = false;
        if(this._mousemove_)
        {
            this._mousemove_ = false;
            return false;
        }
    })
})
.mousemove(function(ev)
{
    if($ministeres.data('down'))
    {
        var ministeres_top = $ministeres.data('top') - ($ministeres.data('x') - ev.clientY);
        ministeres_top = Math.min(0, ministeres_top);
        ministeres_top = Math.max(ministeres_top, window_height-ministeres_height);
        $ministeres.css('top', ministeres_top+'px');
    }
})
.mouseup(function()
{
    $ministeres.data('down', false);
})


var onChildMouseWheel = function(ev)
{
	if(window.no_scroll)
	{
		event = ev || window.event;
	    
	    if (event.preventDefault)
	        event.preventDefault();
	    
	    event.returnValue = false;
	}
}

if (window.addEventListener)
{
    window.addEventListener("DOMMouseScroll", onChildMouseWheel, false);
}
window.onmousewheel = document.onmousewheel = onChildMouseWheel;
