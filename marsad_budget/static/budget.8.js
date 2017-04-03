var max_children = 6;
var bars_gap = 20;
var arc_width = level_width - bar_width;
var arc_coords = [0, arc_width/2-10, arc_width/2+10, arc_width];
var scale;


var get_popover_position = function(level, direction)
{
	if(direction > 0)
		return 'left';
	return 'right';
}

var texts = {
	'autres': {
		'recettes': {'fr': 'autres recettes', 'ar':'موارد أخرى'},
		'depenses': {'fr': 'autres ministères', 'ar':'وزارات أخرى'},
	}
}


var render_branches = function(obj, section, level, direction)
{
	var result = {
		elts: [],
		svg: document.createElementNS(svgNS, "svg")
	}
	
	var root_offset = 0;
	var leaf_offset = 0;

	var head = obj.slice(0,max_children-1);
	var tail = obj.slice(max_children-1);
	
	if(tail.length)
	{
		var reduced = {'titre': {'fr':texts['autres'][section].fr+' <span class="autres-count">('+tail.length+')</span>', 'ar':texts['autres'][section].ar+' <span class="autres-count">('+tail.length+')</span>'}, 'montant':0, 'rel': true};

		for(var i=0; i<tail.length; i++)
		{
			reduced.montant += tail[i].montant;
		}

		// insert at 0
		// head.splice(0, 0, reduced);
		
		head.push(reduced);
	}


	for(var i=0; i<head.length; i++)
	{
		var node = head[i];
		console.log(node);
		var bar_height = node.montant * scale;
		var bar_center = bar_height/2 - 10;
		var $bar = $('<div class="bar"></div>');
		var $bar_paint = $('<div class="bar-paint"></div>');
		var $bar_label_value = $('<span class="bar-label-value">'+Math.round(node.montant / 1000000).toLocaleString()+'</span>');
		var $bar_label_titre = $('<span class="bar-label-titre">'+(node.titre[lang])+'</span>');

		if(level)
		{
			/*
			$bar_paint
				.attr("title", "zegz gz zegzererz")
				.data("content", "lzeglzg zlzelgzg <br>zg zg zoereuer efuef uef")
				.popover({placement:get_popover_position(level, direction)});
			*/

			var $arc = document.createElementNS(svgNS, "path"),
				root_height = Math.round(root_offset + bar_height/2),
				leaf_height = Math.round(leaf_offset + bar_height/2),
				path;

			if(direction > 0)
				path = ["M", arc_coords[3]+","+root_height, "C", arc_coords[2]+","+root_height, arc_coords[1]+","+leaf_height, arc_coords[0]+","+leaf_height];
			else
				path = ["M", arc_coords[0]+","+root_height, "C", arc_coords[1]+","+root_height, arc_coords[2]+","+leaf_height, arc_coords[3]+","+leaf_height];

			$arc.setAttribute("d", path.join(" "));
			$arc.setAttribute("stroke-width", (bar_height < 1 ? 1 : bar_height) +'px');
			result.svg.appendChild($arc);
		}

		root_offset += bar_height;
		leaf_offset += bars_gap + bar_height;

		if(bar_height<10)
		{
			$bar.addClass('small');
		}

		if(bar_height<1)
		{
			$bar.addClass('tiny');
		}

		$bar_label_titre.css('top', bar_center+'px');
		$bar_label_value.css('top', bar_center+'px');
		$bar.css('height', bar_height+'px');

		$bar_paint.append($bar_label_value);
		$bar.append($bar_paint)
			.append($bar_label_titre);

		if(node.children)
		{
			var $childbars = $('<div class="childbars"></div>');
			var childresults = render_branches(node.children, section, level+1, direction)

			$childbars.append(childresults.elts);
			$bar[0].appendChild(childresults.svg);
			$bar.append($childbars);
			var bar_click = function(ev)
			{
				var $this = $(this.parentNode);

				ev.stopPropagation();

				$budget_wrapper.css('left', (level * level_width * direction)+'px');
				$this.find('.open, .transparent').removeClass('open transparent');

				if($this.hasClass('open'))
				{
					$this.removeClass('open').siblings().removeClass('transparent');
					$budget_wrapper.css('left', ((level-1) * level_width * direction)+'px');
					return false;
				}

				$this.addClass('open')
					 .removeClass('transparent')
					 .siblings()
					 	.removeClass('open').addClass('transparent')
						.find('.open, .transparent')
							.removeClass('open transparent');
			}

			$bar_paint.click(bar_click);
			$bar_label_titre.click(bar_click);
		}
		else
		{
			$bar.click(function(ev)
			{
				var $this = $(this);

				ev.stopPropagation();

				if($this.hasClass('transparent'))
				{
					$budget_wrapper.css('left', (level * level_width * direction)+'px');
					$this.parent().removeClass('open')
						.find('.transparent, .open')
							.removeClass('transparent open');
				}
			})
		}

		result.elts.push($bar);
	}

	result.svg.setAttribute('height', leaf_offset);

	return result;
}
