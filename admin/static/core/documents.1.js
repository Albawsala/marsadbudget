$(document).ready(function()
{
	var docs_click;

	$form = $('#search');
	$path = $form.children('[name="_path"]');
	render_fields(fields, 'root', 0);
	var is_iframe = $('body').data('iframe');

	if (is_iframe)
	{
		docs_click = function()
		{
			window.parent.postMessage({
				method: 'select_doc',
				doc_url: $(this).attr('href'),
				doc_id: this.id,
				doc_featured: this.innerHTML,
				iframe_uid: is_iframe
			}, window.location.origin)
			return false;
		}
		$('#close-iframe').click(function()
		{
			window.parent.postMessage({'method': 'close_iframe'}, window.location.origin);
			return false;
		})
	}
	else
		docs_click = function()
		{
			$(this).css('border-left', '1px solid red');
		}
	$('.table > a').click(docs_click)
});
