var form,
	flash,
	url,
	url_base,
	url_suffix,
	is_iframe,
	refs_index = {};


var init = function()
{
	setupField(form);
	setupLang();
	is_iframe = $('body').data('iframe');

	window.addEventListener("message", function(ev)
	{
		console.log(ev.data);
		switch (ev.data.method)
		{
			case 'close_iframe':
				$('.popup').hide();
				break;
			case 'select_doc':
			case 'update_doc':
				var $ref_root = $(refs_index[ev.data.iframe_uid]);
				$ref_root.children('.data').val(ev.data.doc_id);
				$ref_root.children('.ref_obj').html(ev.data.doc_featured);
				$ref_root.find('> .ref_commands > .ref_edit').attr('href', ev.data.doc_url);
				$('.popup').hide();
				break;
		}
	}, false);

	if (is_iframe)
	{
		$('#close-iframe').click(function()
		{
			window.parent.postMessage({'method': 'close_iframe'}, window.location.origin);
			return false;
		})
	}

	$('input.submit').click(function(ev)
	{
		ev.preventDefault();
		doc = processObject(form);
		data = {
			"doc": doc,
			"_csrf": form.data('csrf'),
			"mtime": form.data('mtime'),
			"draft": $('input[name="_draft"]').is(':checked')
		}

		$.ajax({
			type: 'POST',
			contentType: 'application/json',
			url: url,
			data: JSON.stringify(data),
			success: function(data){
				var response = JSON.parse(data);
				flash.html(response.message);
				if (is_iframe)
					window.parent.postMessage({
						method: 'update_doc',
						doc_url: response.edit_url,
						doc_id: response._id,
						doc_featured: response.featured,
						iframe_uid: is_iframe
					}, window.location.origin);
				else
					setTimeout(function(){ window.location.replace(url_base+"documents/"+form.data('collection')) }, 1500);
			},
			error: function(xhr, status, error){
				try {
					var response = JSON.parse(xhr.responseText);
					flash.html(response.message);
					form.data('csrf', response.csrf);
				} catch (err) {
					flash.text(xhr.responseText);
				}
			}
		});
	});
}


var setupReference = function(root)
{
	var $popup = root.children('.popup');
	
	root.find('> .ref_commands > :not(.ref_clear)').click(function()
	{
		var $this = $(this);
		var url = $this.attr('href');
		if (url == '#') return false;
		
		var uid = Date.now() +'_'+ Math.floor(Math.random() * 10000);
		var $iframe = $('<iframe src="'+url+'?iframe='+uid+'"></iframe>')
		refs_index[uid] = root.get(0);
		$popup.html($iframe).fadeIn(250);
		return false;
	});

	root.find('> .ref_commands > .ref_clear').click(function()
	{
		root.children('.data').val('');
		root.children('.ref_obj').html($('<span>...</span>'));
		root.find('> .ref_commands > .ref_edit').attr('href','#');
		return false;
	})
}

/*
var st = {
	hide: function(obj){
		if(obj.parent().hasClass('formated')){
			obj.next('.mceEditor').css('display','none'); 
			obj.css('display','none');
		} else {
			obj.css('display','none');
		}
	},
	show: function(obj){
		if(obj.parent().hasClass('formated')){
			obj.next('.mceEditor').css('display','block');
		} else {
			obj.css('display','block');
		}
	}
};
*/

var setupLang = function()
{
	$('#langs').children().click(function()
	{
		var that = $(this)
		
		if (!that.hasClass('active'))
		{
			setLang(that.data('lang'));
		}
	});
}


var setLang = function(ln)
{
	var old = $('#langs .active').data('lang');
	$('#langs .'+ ln).addClass('active').siblings().removeClass('active');
	$('.form').addClass(ln).removeClass(old);
}


var tinymce_conf = {
	script_url: '/admin/static/tinymce/js/tinymce/tinymce.min.js',
	menubar: false,
	statusbar: false,
	inline: true,
	relative_urls: false,
	remove_script_host: false,
	convert_urls: false,
	plugins: 'linkmanager media imagemanager code fullscreen textcolor',
	toolbar: 'styleselect bold italic forecolor numlist bullist blockquote alignleft aligncenter alignright alignjustify link unlink imagemanager media fullscreen code',
	extended_valid_elements: 'script[language|type|src],link[rel|href]',
	browser_spellcheck : true,
	//spellchecker_languages : "French=fr,Arabic=ar,English=en",

}


var setupString = function(field)
{
	if(field.hasClass('formated'))
	{
		/*
		field.children('.data').each(function(){ aloha(this); });
		*/
		field.children('.data').removeAttr("id");
		
		setTimeout(function()
		{
			field.children('.data').tinymce(tinymce_conf)
		}, 10);
	}
}


var two_digits = function(digit)
{
	return digit < 10 ? '0'+digit : digit;
}


var setupDate = function(field)
{
	var $today = $('<a class="today" href="#">today</a>');
	$today.click(function()
	{
		var today = new Date();
		var today_str = two_digits(today.getDate())+'/'+two_digits(today.getMonth()+1)+'/'+today.getFullYear();
		field.find('input').val(today_str);
		return false;
	})
	field.find('.buttons').prepend($today);
}


var setupDatetime = function(field)
{
	var $now = $('<a class="now" href="#">now</a>');
	$now.click(function()
	{
		var now = new Date();
		var today_str = two_digits(now.getDate())+'/'+two_digits(now.getMonth()+1)+'/'+now.getFullYear();
		var now_str = two_digits(now.getHours())+':'+two_digits(now.getMinutes())+':'+two_digits(now.getSeconds());
		field.find('input').val(today_str+' '+now_str);
		return false;
	})
	field.find('.buttons').prepend($now);
}


var setupClone = function(field, idx)
{
	var $clone = $('<span class="trigger clone"></span>');
	var $del = $('<span class="trigger del"></span>');
	var $up = $('<a href="#" class="trigger up">☝</a>');
	var $down = $('<a href="#" class="trigger down">☟</a>');
	
	$clone.click(function()
	{
		var cloned = field.clone();
		setupClone(cloned, 1);
		field.after(cloned);
	});
	$del.click(function()
	{
		field.remove();
	});
	$up.click(function()
	{
		field.prev().before(field);
		return false;
	});
	$down.click(function()
	{
		field.next().after(field);
		return false;
	});

	field.find('.buttons, .popup').children().remove();
	field.children('.buttons')
		.append($clone)
		.append($del)
		.append($up)
		.append($down);
	
	setupField(field);
}


var setupCondition = function(field)
{
	var conds = field.data('conditions');
	
	for (path in conds)
	{
		var lsn_field = $('.docfield[data-path="'+ path +'"]'),
			lsn = lsn_field.children('.data');
		
		lsn.change(function(cond)
		{
			var handler;
			
			if (lsn_field.hasClass('boolean')) handler = function()
			{
				if (cond == "true" && lsn.is(':checked') || cond == "false" && !lsn.is(':checked'))
					field.removeClass('hide');
				else
					field.addClass('hide');
			};
			else handler = function()
			{
				if (typeof(cond) == "string" && lsn.val() == cond || typeof(cond) == "object" && $.inArray(lsn.val(), cond) >= 0)
					field.removeClass('hide');
				else
					field.addClass('hide');
			};
			
			handler();
			return handler;
		
		}(conds[path]));
	}
}


var setupField = function(field){
	if(field.hasClass('string') || field.hasClass('multilang')){
		setupString(field);
	} else if(field.hasClass('object')){
		setupObject(field);
	} else if(field.hasClass('reference') || field.hasClass('file')){
		setupReference(field);
	} else if(field.hasClass('datetime')){
		setupDatetime(field);
	} else if(field.hasClass('date')){
		setupDate(field);
	}
	setupCondition(field);
}


var setupObject = function(root)
{
	root.children('.docfield').each(function(){
		setupField($(this));
	});

	root.children('.multiple').each(function(){
		$(this).children('.docfield').each(function(idx){
			setupClone($(this), idx);
		});
	});

	if(root.hasClass('widget'))
		setupWidget(root);
}


var processObject = function(object){
	var obj = {};
	object.children('.docfield:not(.hide)').each( function(i){
		var docfield = $(this), key = docfield.attr('id');
		obj[key] = processField(docfield);
	});
	object.children('.multiple:not(.hide)').each( function(i){
		var docfield = $(this), key = docfield.attr('id');
		obj[key] = processArray(docfield);
	});
	return obj;
}


var dict_is_empty = function(dict)
{
	for(var k in dict)
		if(typeof dict[k] == "object") {
			if(!dict_is_empty(dict[k]))
				return false;
		}
		else if(dict[k] != '')
			return false;
	return true;
}


var processArray = function(array){
	var obj = [];
	array.children('.docfield').each( function(i)
	{
		var $this = $(this);
		var field = processField($this);
		if(($this.hasClass('multilang') || $this.hasClass('object')) && dict_is_empty(field) || field == '')
			return;
		obj.push(field);
	});
	return obj;
}


var processField = function(field){
	if(field.hasClass("options")){
		var value = new Array();
		field.find('input:checked').each(function(i){
			value.push($(this).val());
		});
		return value;
	}
	else if(field.hasClass("object")){
		return processObject(field);
	}
	else if(field.hasClass("choice")){
		return field.children('select').val();
	}
	else if(field.hasClass("boolean")){
		return field.children('input').is(':checked');
	}
	else if(field.hasClass("string")){
		if(field.hasClass('list'))
			return field.children('.data').html();
		return field.children('.data').val();
	}
	else if(field.hasClass("multilang"))
	{
		var value = {};
		
		if (field.hasClass('list'))
			field.children('.data').each(function()
			{
				var that = $(this);
				value[that.data('lang')] = that.html();
			});
		else
			field.children('.data').each(function()
			{
				var that = $(this);
				value[that.data('lang')] = that.val();
			});
		return value;
	}
	else if(field.hasClass("reference") || field.hasClass("file")){
		return field.children('input[name="ref_id"]').val();
	}
	else {
		return field.children('.data').val();
	}
}
