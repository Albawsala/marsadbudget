var budget_height = 280;
var level_width = 250;
var bar_width = 70;
var max_children = 5;
var bars_gap = 30;
var arc_width = level_width - bar_width;
var arc_coords = [0, arc_width/2-10, arc_width/2+10, arc_width];
var scale;


var render_branches = function(obj, gbo)
{
	var $branches = $('<div class="budget-level-1"></div>');

	if(gbo)
		$branches.addClass('gbo');

	for(var section in obj)
	{
		var node = obj[section];
		var bar_height = Math.max(node.montant * scale * 1.8, 2);
		var $bar = $('<div class="bar '+section+'"></div>');
		var $bar_label = $('<div class="bar-label">'+(budget_labels[section][lang])+'</div>');
		var $bar_value = $('<div class="bar-value">'+Math.round(node.montant*1000).toLocaleString()+'</div>');
		var $bar_paint = $('<div class="bar-paint"></div>');

		

		$bar_label.css('top', (bar_height/2 - 10)+'px');
		$bar_value.css('top', (bar_height/2 - 10)+'px');
		$bar_paint.css('height', bar_height+'px');
		$bar.append($bar_label)
			.append($bar_value)
			.append($bar_paint);
		$branches.append($bar);

		if(gbo)
			continue;

		var $childbars = $('<div class="childbars"></div>');
		var childbars_height = 0;
		var childbars_gap_height = 0;
		var $arcs = document.createElementNS(svgNS, 'svg');
		$arcs.setAttribute('version', '1.1');

		for(var i=0; i<node.children.length; i++)
		{
			var childnode = node.children[i];
			var childbar_height = Math.max(childnode.montant * scale * 1.8, 2);
			var $childbar = $('<div class="bar '+section+'"></div>');
			var $bar_label = $('<div class="bar-label">'+(childnode.titre && childnode.titre[lang] || budget_labels[childnode.ref][lang])+'</div>');
			var $bar_value = $('<div class="bar-value">'+Math.round(childnode.montant*1000).toLocaleString()+'</div>');
			var $bar_paint = $('<div class="bar-paint"></div>');
			var $arc = document.createElementNS(svgNS, "path");
			var hl = childbars_height + childbar_height/2, hr = childbars_gap_height + childbar_height/2;
			$arc.setAttribute("d", "M0,"+hl+" C50,"+hl+" 90,"+hr+" 130,"+hr);
			$arc.setAttribute("stroke-width", childbar_height+'px');
			$arcs.appendChild($arc);

			$bar_label.css('top', (childbar_height/2 - 10)+'px');
			$bar_value.css('top', (childbar_height/2 - 10)+'px');
			$bar_paint.css('height', childbar_height+'px');
			$childbar.append($bar_label)
				.append($bar_value)
				.append($bar_paint);
			$childbars.append($childbar);

			childbars_gap_height += childbar_height + 18;
			childbars_height += childbar_height;
		}
		$bar.css('height', Math.max(bar_height, childbars_gap_height)+'px');
		$bar.append($arcs)
			.append($childbars);
	}

	return $branches;
}



var render_branches_gbo = function(obj)
{
	var $branches = $('<div class="budget-level-1 gbo"></div>');

	for(var i=0; i<obj.length; i++)
	{
		var node = obj[i];
		var bar_height = Math.max(node.montant * scale * 1.8, 2);
		var $bar = $('<div class="bar"></div>');
		var $bar_label = $('<div class="bar-label">'+node.titre[lang]+'</div>');
		var $bar_value = $('<div class="bar-value">'+Math.round(node.montant*1000).toLocaleString()+'</div>');
		var $bar_paint = $('<div class="bar-paint"></div>');

		$bar_label.css('top', (bar_height/2 - 10)+'px');
		$bar_value.css('top', (bar_height/2 - 10)+'px');
		$bar_paint.css('height', bar_height+'px');
		$bar.append($bar_label)
			.append($bar_value)
			.append($bar_paint);
		$branches.append($bar);
	}
	
	return $branches;
}



var render_branchess = function(obj, level, direction)
{
	var result = {
		total: 0,
		elts: [],
		svg: document.createElementNS(svgNS, "svg")
	}
	
	var root_offset = 0;
	var leaf_offset = 0;
/*
	var head = obj.slice(0,max_children-1);
	var tail = obj.slice(max_children-1);
	
	if(tail.length)
	{
		var reduced = {'titre': 'autres ('+tail.length+')', 'montant':0, 'rel': true};

		for(var i=0; i<tail.length; i++)
		{
			reduced.montant += tail[i].montant;
		}
		//head.splice(0, 0, reduced);
		head.push(reduced);
	}
*/
	
	for(var i=0; i<obj.length; i++)
	{
		var node = obj[i];
		var montant = node.montant || 0;
		var $bar = $('<div class="bar '+node.ref+'"></div>');
		var $bar_paint = $('<div class="bar-paint"></div>');
		var $bar_label = $('<div class="bar-label"></div>');

		if(node.children)
		{
			var $childbars = $('<div class="childbars"></div>');
			var childresults = render_branches(node.children, level+1, direction)

			if(!montant)
			{
				montant = childresults.total;
			}

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
			$bar_label.click(bar_click);

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

		var bar_height = montant * scale * 2;
		
		$bar_label.append($(
			'<span class="bar-label-value">'+Math.round(montant * 1000).toLocaleString()+'</span>'+
			'<span class="bar-label-titre">'+(node.titre || node.ref)+'</span>'
		));

		if(level)
		{
			var $arc = document.createElementNS(svgNS, "path"),
				root_height = Math.round(root_offset + bar_height/2),
				leaf_height = Math.round(leaf_offset + bar_height/2),
				path;

			if(direction == 1)
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

		$bar_label.css('top', (bar_height/2 - 10)+'px');
		$bar.css('height', bar_height+'px');
		$bar.append($bar_paint)
			.append($bar_label);

		result.total += montant;
		result.elts.push($bar);
	}

	result.svg.setAttribute('height', leaf_offset);

	return result;
}
