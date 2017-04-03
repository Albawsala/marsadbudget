var lang;
var $budget_wrapper;
var $budget;
var $budget_popup;
var $budget_popup_main;
var $budget_popup_years;
var $budget_popup_labels;
var $budget_popup_bar_active;

var texts = {
	'LF': {'fr':'Loi de Finance', 'ar':'قانون المالية'},
	'LFC': {'fr':'Loi de Finance Complémentaire', 'ar':'قانون المالية التكميلي'},
	'DT': {'fr':'DT', 'ar':'د'},
	'MDT': {'fr':'MDT', 'ar':'م.د.'},
	'evolution': {'fr':'Évolution par rapport à', 'ar':'نسبة التطور مقارنة ب'},
	'total': {'fr':'Total dépenses', 'ar':'مجموع نفقات'},
	'repartition_gbo': {'fr':'Répartition selon objectifs G.B.O', 'ar':'توزيع حسب الأهداف'},
	'repartition_classique': {'fr':'Répartition classique', 'ar': 'توزيع حسب الوسائل'},
}

$(document).ready(function()
{
	lang = $('html').attr('lang');
	$budget_wrapper = $('#budget-wrapper');
	$budget = $('#budget');
	$budget_popup = $('#budget-popup');
	$budget_popup_main = $('#budget-popup-main');
	$budget_popup_years = $('#budget-popup-years');
	$budget_popup_labels = $('#budget-popup-labels');
	
	$('#budget-popup-close').click(function()
	{
		$budget_popup.hide();
		return false;
	});

	$('.tab-link').click(function()
	{
		var $this = $(this);

		if($this.hasClass('active'))
			return false;

		$this.addClass('active').siblings().removeClass('active');

		var $tab = $('#'+$this.data('tab'));
		$tab.addClass('active').siblings().removeClass('active');
		if($this.data('tab') == 'ministere-contact' && !$tab.hasClass('setup'))
		{
			if(ministere_coords)
				renderGoogleMap(ministere_coords, ministere_geojson);
			$tab.addClass('setup');
		}
		return false;
	})

	$budget.prepend(render_budget_years());
});


var render_budget = function(node)
{
	var previous_year;
	
	if(node.type == 'LFC')
		previous_year = 'LF ' + (node.annee)
	else
		previous_year = node.annee - 1;

	var budget_evolution = node.budget.evolution;
	var budget_evolution_sign;

	if(budget_evolution > 0)
		budget_evolution_sign = 'positive';
	else if(budget_evolution < 0)
		budget_evolution_sign = 'negative';
	else
		budget_evolution_sign = 'null';

	var $budget_labels = $(
	'<div class="budget-label">'+
		'<div class="budget-label-value">'+(Math.round(node.budget.total * 1000)/1000)+' '+texts['MDT'][lang]+'</div>'+
		'<div class="grey">'+texts['total'][lang]+' '+node.annee+' '+node.type+'</div>'+
	'</div>'+
	'<div class="budget-label">'+
		'<div class="budget-label-evolution-sign float '+budget_evolution_sign+'"></div>'+
		'<div class="budget-label-evolution">'+(Math.round(budget_evolution * 1000)/10)+' %</div>'+
		'<div class="grey">'+texts['evolution'][lang]+' '+previous_year+'</div>'+
	'</div>');
	$budget_popup_labels.html($budget_labels);

	if(node.budget.children_gbo && node.annee == 2014 && node.type == 'LF')
	{
		var $budget_container = $('<div id="budget-container-labels">'+
			'<div>'+texts['repartition_gbo'][lang]+'</div>'+
			'<div>'+texts['repartition_classique'][lang]+'</div>'+
		'</div>');
		
		return [
			$budget_container,
			render_branches_gbo(node.budget.children_gbo),
			render_branches(node.budget.children, true)
		];
	}

	return render_branches(node.budget.children);
}


var render_budget_years = function()
{
	var $tab = $('<div id="budget-years"></div>');
	var max = 0;

	for(var i=0; i<budgets.length; i++)
		max = Math.max(max, budgets[i].budget.total);

	scale = 140.0 / max
	var y = 0;
	var $yeargroup;
	var $yeargroup_bars;
	var $popup_yeargroup;
	var $popup_yeargroup_bars;

	for(var i=0; i<budgets.length; i++)
	{
		var node = budgets[i],
			$bar = $('<a href="#" class="yeargroup-bar"></a>'),
			$popup_bar = $('<a href="#" class="popup-yeargroup-bar"></a>');

		if(y != node.annee)
		{
			y = node.annee;

			$yeargroup = $('<div class="yeargroup"></div>');
			$yeargroup_bars = $('<div class="yeargroup-bars"></div>');
			var $year = $('<div class="yeargroup-year">'+y+'</div>');
			$yeargroup.append($yeargroup_bars).append($year);
			$tab.append($yeargroup);

			$popup_yeargroup = $('<div class="popup-yeargroup"></div>');
			$popup_yeargroup_bars = $('<div class="popup-yeargroup-bars"></div>');
			var $popup_year = $('<div class="popup-yeargroup-year">'+y+'</div>');
			$popup_yeargroup.append($popup_yeargroup_bars).append($popup_year);
			$budget_popup_years.append($popup_yeargroup);
		}

		var $yeargroup_label = $('<div class="yeargroup-bar-label">'+node.type+'</div>');
		$bar.append($yeargroup_label);

		$bar[0].node = node;
		$bar[0].popup = $popup_bar[0];
		$bar.attr('title','Cliquez pour plus de détails').tooltip();
		$bar.click(function()
		{
			var $this_popup = $(this.popup);

			$(this).tooltip('hide');

			if($budget_popup_bar_active)
				$budget_popup_bar_active.removeClass('active');
			$this_popup.addClass('active');
			$budget_popup_bar_active = $this_popup;
			$budget_popup_main.html(render_budget(this.node));
			$budget_popup.show();
			return false;
		});

		$popup_bar[0].node = node;
		$popup_bar.click(function()
		{
			var $this = $(this);

			if($budget_popup_bar_active)
				$budget_popup_bar_active.removeClass('active');
			$this.addClass('active');
			$budget_popup_bar_active = $this;
			$budget_popup_main.html(render_budget(this.node));
			return false;
		});


		for(var section in node.budget.children)
		{
			var childnode = node.budget.children[section];
			var section_height = childnode.montant * scale;
			var section_percentage = Math.round(childnode.montant * 100 / node.budget.total);
			var $section = $('<div class="yeargroup-bar-section '+section+'"></div>');
			$section.css('height', section_height);
			$bar.append($section);

			$('#budget-legend > .'+section).show();
		}
		$yeargroup_bars.append($bar);

		var popup_bar_height = node.budget.total * scale / 3.5;
		$popup_bar.append($('<div style="height:'+popup_bar_height+'px;"></div>'));
		$popup_yeargroup_bars.append($popup_bar);
	}

	return $tab;
}


var map;
var google_maps_base = [
	{ "stylers": [ { "saturation": -100 } ] },
	{ "featureType": "road", "stylers": [ { "gamma": 0.59 } ] },
	{ "featureType": "administrative.province", "stylers": [ { "visibility": "off" } ] },
];

var renderGoogleMap = function(coords, geojson)
{
	map = new google.maps.Map(document.getElementById('ministere-adresse-map'), {
		center: new google.maps.LatLng(coords.lat, coords.lon),
		zoom: 14,
		panControl: false,
		mapTypeControl: false,
		zoomControl: false,
		disableDefaultUI: false,
		streetViewControl: false,
		styles: google_maps_base,
	});

	map_features = map.data.addGeoJson(geojson);
}