var lang;
var texts = {
	'MDT': {'fr':'MDT','ar':'م.د'}
}

var distance = 160;
var radius = 80;
var budget = {};
var budget_total_ref;
var budgets = [];
var budgets_map = {};
var $container;
var expand_autres = false;
var empty = 0;
var autres = {
	'id':'autres',
	'titre':{'fr':'autres<br> </sub>', 'ar':'أخرى<br> </sub>'},
}


$(document).ready(function()
{
	lang = $('html').attr('lang');
	$container = $("#depenses");
  url = $(".depenses-year.active").attr("href");
	$.ajax({
		url: url,
		success: function(data){
			budget.data = data['budgets']
			render_nodes(true);
		}
	});

	$('#depenses-sans-input , #compensations-sans-input').change(function()
	{
    t1 = $('#depenses-sans-input');
    t2 = $('#compensations-sans-input');
		if((t1.attr("checked") && !t2.attr("checked")) || (t2.attr("checked") && !t1.attr("checked"))) {
      if(t1.attr("checked"))
			refresh_nodes(budgets.concat([autres]), t1.attr("data-type"));
      else
      refresh_nodes(budgets.concat([autres]), t2.attr("data-type"));
    }
    else if (t1.attr("checked") && t2.attr("checked")) {
      refresh_nodes(budgets.concat([autres]), 'total_brute');
    }
		else
			refresh_nodes(budgets.concat([autres]), 'total');
	});

	$('.depenses-year').click(function()
	{
		var $this = $(this);
		if($this.hasClass('active'))
			return false;

		$this.addClass('active').siblings().removeClass('active');
		$('#depenses-sans-input').attr("checked", false);
		url = $this.attr('href');
		$.ajax({
			url: url,
			success: function(data){
				budget.data = data['budgets'];
				render_nodes()
			}
		});
		return false;
	});
});


var render_nodes = function(initial)
{
	var keys = Object.keys(budgets_map);
	budget.total = 0;
	budget.total_sans = 0;
  budget.total_comp = 0;
  budget.total_brute=0;
	autres.total = 0;
	autres.total_sans = 0;
  autres.total_comp = 0;
  autres.total_brute=0;

	for(var i=0; i<budget.data.length; i++)
	{
		var node = budget.data[i];

		if(typeof node.total != "number")
			continue

		if(expand_autres && node.total >= 1000)
			continue

		if(node.total_old)
			node.total = node.total_old;

		node.compensation = node.compensation || 0;
		budget.total += node.total;

		if(node.id in budgets_map)
		{
			budgets_map[node.id].total = node.total;
			budgets_map[node.id].compensation = node.compensation;
			node = budgets_map[node.id];
		}

		if(node.id == 'dette_publique')
		{
			node.total_sans = 0;
      node.total_brute=0;
      node.total_comp = node.total - node.compensation;
      budget.total_comp += node.total - node.compensation;
		}
		else
		{
			node.total_sans = node.total;
      node.total_brute= node.total - node.compensation;
      node.total_comp = node.total - node.compensation;
			budget.total_sans += node.total_sans;
      budget.total_comp += node.total_comp;
      budget.total_brute+= node.total_brute;
		}

		if(!expand_autres && node.total < 1000)
		{
			autres.total += node.total;
			autres.total_sans += node.total_sans;
      autres.total_comp += node.total_comp;
      autres.total_brute+= node.total_brute;
		}
		else if(node.id in budgets_map)
		{
			keys.splice(keys.indexOf(node.id),1);
		}
		else
		{
			render_node(node);
			budgets.push(node)
			budgets_map[node.id] = node;
		}
	}

	empty = keys.length;
	for(var i=0; i<keys.length; i++)
	{
		var node = budgets_map[keys[i]];
		node.total_old = node.total;
		node.total = 0;
		node.total_sans = 0;
    node.total_comp = 0;
    node.total_brute= 0;
	}

	if(initial)
	{
		budget_total_ref = budget.total;
		render_node(autres);
		autres.$circle.attr('id','circle-autres').append(autres.$label)
		autres.$circle.click(function()
		{
			expand_autres = !expand_autres;
			render_nodes();
		})
		refresh_nodes(budgets.concat([autres]), 'total');
	}
	else
	{
		budgets.sort(function(a,b){return b.total - a.total})
		if(expand_autres)
			setTimeout(function()
			{
				autres.total = budget.total;
				autres.total_sans = budget.total_sans;
        autres.total_comp = budget.total_comp;
        autres.total_brute= budget.total_brute;
				refresh_nodes(budgets, 'total');
			}, 10);
		else
			setTimeout(function(){refresh_nodes(budgets.concat([autres]), 'total');}, 10);
	}
}


refresh_nodes = function(data, key)
{
	var area_ratio = Math.PI * radius * radius / budget_total_ref;
	var gap = Math.PI / (data.length-empty);
	var arc = 0;

	for(var i=0; i<data.length; i++)
	{
		var node = data[i];
		var area = node[key] * area_ratio;
		node.r = Math.floor(Math.sqrt(area/Math.PI));
		if(node[key] == 0)
		{
			update_node(node, key);
			continue;
		}
		var arc_angle = Math.PI * node.total / budget.total + gap
		node.angle = arc + arc_angle/2;
		arc += arc_angle;
		if(arc_angle < 0.24)
			node.$label.addClass('small')
		else
			node.$label.removeClass('small')
		update_node(node, key);
	}

	if(expand_autres)
	{
		$('#depenses-total').hide();
		$('#depenses-total-circle').css({
			'top': '270px',
			'left': '250px',
			'width':0,
			'height':0,
		});
		var angle = Math.PI
		var area = autres[key] * area_ratio;
		autres.r = Math.floor(Math.sqrt(area/Math.PI));

		autres.$circle.css({
			'top': (270+autres.r)+'px',
			'left': (250+autres.r)+'px',
			'width': (autres.r*2)+'px',
			'height': (autres.r*2)+'px',
			'transform': 'rotate('+angle+'rad)',
			'transform-origin': '0px 0px',
		})
		autres.$label.css({
			'margin-top': (-autres.r+22)+'px',
		})
	}
	else
	{
		var area = budget[key] * area_ratio;
		var r = Math.floor(Math.sqrt(area/Math.PI));
		/*
		autres.$label.css({
			'left': '410px',
			'transform-origin': '-160px 0px 0px',
		})
		*/
		$('#depenses-total').show();
		$('#depenses-total-chiffre').text(Math.round(budget[key]));
		$('#depenses-total-circle').css({
			'top': (270-r)+'px',
			'left': (250-r)+'px',
			'width': (r*2)+'px',
			'height': (r*2)+'px',
		}).show();
	}
}


var render_node = function(node)
{
	var node_icon = 'url("/static/images/' + (node.icon || 'ministere_'+node.id+'_white.png")');
	node.$circle = $('<div class="circle"></div>');
  if(node.id == "autres") {
    node.$circle.css({
      'transform': 'rotate('+(Math.PI*1.5)+'rad)',
    });
    node.$label = $('<div class="label" id="label-'+node.id+'"><div>'+
  		'<div class="label-text">'+(node.titre[lang])+'<div class="label-total"></div></div>'+
  	'</div></div>');
  node.$label_total = $('');
  }
  else {
    node.$circle.css({
      'background-image': node_icon,
      'transform': 'rotate('+(Math.PI*1.5)+'rad)',
    });
	node.$label = $('<div class="label" id="label-'+node.id+'"><div>'+
		'<div class="label-text">'+(node.titre && node.titre[lang] || node.id)+'</div>'+
	'</div></div>');
  node.$label_total = $('<div class="label-total"></div>');
  }
	node.$label.css({
		'transform': 'rotate('+(Math.PI*1.5)+'rad)',
	})
	node.$label_total = $('<div class="label-total"></div>');
	node.$label.children().append(node.$label_total);
	$container.append(node.$circle).append(node.$label);
}


var update_node = function(node, key)
{
	node.$circle.css({
		'top': (270-node.r)+'px',
		'left': (410-node.r)+'px',
		'width': (node.r*2)+'px',
		'height': (node.r*2)+'px',
		'border-radius': (node.r*2)+'px',
		'transform-origin': (node.r-160)+'px '+(node.r)+'px',
	})
	if(node.id == 'autres')
		node.$label.css({
			'margin-top': (-node.r+22)+'px',
			'opacity': node[key] ? 1 : 0,
		});
	else
		node.$label.css({
			'padding-left': (node.r+7)+'px',
			'opacity': node[key] ? 1 : 0,
		});

	node.$label_total.html(Math.floor(node[key])+' <sub>'+texts['MDT'][lang]+'</sub>')

	if(key == 'total' && node.total)
	{
		var angle = node.angle-Math.PI/2
		node.$circle.css({'transform': 'rotate('+angle+'rad)'});
		if(node.id == 'autres')
			node.$label.css({'transform': 'rotate('+(0)+'rad)'});
		else
			node.$label.css({'transform': 'rotate('+angle+'rad)'});

		if(node.angle > Math.PI)
			node.$label.addClass('mirror');
		else
			node.$label.removeClass('mirror');
	}
}
