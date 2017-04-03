var overlays;
var map = null;
var $visual_editor;

var black_icon = {
	path: google.maps.SymbolPath.CIRCLE,
	scale: 5,
	strokeColor: 'black',
};

var red_icon = {
	path: google.maps.SymbolPath.CIRCLE,
	scale: 5,
	strokeColor: 'red',
};

var geojson_types = {
	'Polygon': 'polygon',
	'LineString': 'polyline',
	'Point': 'marker',
}


var setupWidget = function(root)
{
	var trigger = $('<a href="#" class="trigger">visual editor</a>');

	trigger.click(function()
    {
        if(!$visual_editor)
            renderVisualEditor(root);
        else
        	$visual_editor.show();

        return false;
    });

    root.children('.buttons').append(trigger);
}


var renderVisualEditor = function(root)
{
	$.ajax({
        url: '/widgets/visual_editor',
        success: function(html)
        {
            $('.form').before(html);
            $visual_editor = $('#visual-editor');

            $visual_editor.children('#close').click(function()
            {
            	$visual_editor.hide();
            	return false;
            });

            $visual_editor.children('#generate-data').click(function()
            {
            	dumpOverlays(root);
            	$visual_editor.hide();
            	return false;
            });

			map = new google.maps.Map(document.getElementById('map_canvas'), {
				center: new google.maps.LatLng(33.85, 9.6),
				zoom: 7,
				mapTypeControl: true,
				mapTypeId: google.maps.MapTypeId.ROADMAP
			});
/*
			var input = (document.getElementById('pac-input'));
			
			map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

			var searchBox = new google.maps.places.SearchBox((input));

			google.maps.event.addListener(searchBox, 'places_changed', function()
			{
			    var places = searchBox.getPlaces();

			    if (places.length == 0) {
			    	return;
			    }

			    var bounds = new google.maps.LatLngBounds();
			    for (var i = 0, place; place = places[i]; i++)
			    {
			    	bounds.extend(place.geometry.location);
			    }

			    map.fitBounds(bounds);
			});
*/
			loadOverlays(root);

			drawingManager = new google.maps.drawing.DrawingManager(
			{
				drawingMode: google.maps.drawing.OverlayType.POLYGON,
				drawingControl: true,
				drawingControlOptions: {
					position: google.maps.ControlPosition.TOP_RIGHT,
					drawingModes: [
						google.maps.drawing.OverlayType.MARKER,
						google.maps.drawing.OverlayType.POLYLINE,
						google.maps.drawing.OverlayType.POLYGON
					]
				},
				polygonOptions: {
					editable: true,
					draggable: true,
				},
				polylineOptions: {
					editable: true,
				},
				markerOptions: {
					draggable: true,
					icon: black_icon,
				},
				map: map,
			});
			
			google.maps.event.addListener(drawingManager, 'overlaycomplete', function(event){ overlays.push(event); });
        }
    });
}


var loadOverlays = function(root)
{
	if(overlays)
		for(var i=0; i<overlays.length; i++)
			overlays[i].setMap(null);

	overlays = []
	var lat = root.find('#coords #lat .data').val(),
		lon = root.find('#coords #lon .data').val(),
		zoom = root.find('#coords #zoom .data').val(),
		geojson = root.find('#geojson .data').val();

	if(lat && lon && zoom && geojson)
	{
		map.setCenter(new google.maps.LatLng(parseFloat(lat), parseFloat(lon)))
		map.setZoom(parseFloat(zoom))
		var features = JSON.parse(geojson);

		for(var i=0; i<features.features.length; i++)
			loadOverlay(features.features[i]);
	}
	
}



var dumpOverlays = function(root)
{
	root.find('#geojson .data').val(JSON.stringify({
		"type": "FeatureCollection",
		"features": overlays.map(dumpOverlay),
	}));

	var center = map.getCenter();
	root.find('#coords #lat .data').val(center.lat());
	root.find('#coords #lon .data').val(center.lng());
	root.find('#coords #zoom .data').val(map.getZoom());
}



var dumpOverlay = function(elt)
{
	switch(elt.type)
	{
		case 'polygon':
		return {
			'type': 'Feature',
			'geometry': {
				'type': 'Polygon',
				'coordinates': [ getCoordinates(elt.overlay.getPath(), true) ]
			}
		}

		case 'polyline':
		return {
			'type': 'Feature',
			'geometry': {
				'type': 'LineString',
				'coordinates': getCoordinates(elt.overlay.getPath())
			}
		}

		case 'marker':
		var position = elt.overlay.getPosition();
		return {
			'type': 'Feature',
			'geometry': {
				'type': 'Point',
				'coordinates': [position.lng(), position.lat()]
			}
		}
	}
}



var getCoordinates = function(vertices, close)
{
	var coords = [];

	for(var i=0; i<vertices.length; i++)
	{
		var xy = vertices.getAt(i);
		coords.push([xy.lng(), xy.lat()]);
	}
	
	if(close)
	{
		var xy = vertices.getAt(0);
		coords.push([xy.lng(), xy.lat()]);
	}

	return coords;
}



var getVertices = function(coordinates, closed)
{
	if (closed)
		coordinates = coordinates.slice(0, coordinates.length-1);

	return coordinates.map(function(x){
		return new google.maps.LatLng(x[1], x[0]);
	});
}



var loadOverlay = function(geojson, name)
{
	var coordinates = geojson.geometry.coordinates,
		type = geojson.geometry.type,
		ev;

	switch(type)
	{
		case 'Polygon':
			ev = {
				type: 'polygon',
				overlay: new google.maps.Polygon(
				{
					paths: [getVertices(coordinates[0], true)],
					editable: true,
					draggable: true,
				})
			}
			break;

		case 'LineString':
			ev = {
				type: 'polyline',
				overlay: new google.maps.Polyline(
				{
					path: getVertices(coordinates),
					editable: true,
				})
			}
			break;

		case 'Point':
			ev = {
				type: 'marker',
				overlay: new google.maps.Marker(
				{
					position: new google.maps.LatLng(coordinates[1], coordinates[0]),
					draggable: true,
					icon: black_icon,
				})
			}
			break;
	}
	
	ev.overlay.setMap(map);
	overlays.push(ev);
}