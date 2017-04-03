window.onload = function() {
  var mySlider = $("input.slider").slider();
  $('select').selectric();
  $.get( "govs/"+$('html').attr('lang'), function( data ) {
    for(gov in data["govs"]) {
      gov_name = data["govs"][gov];
      $('#filtre-gov').append('<option>' + (gov_name ? gov_name : 'Empty') + '</option>');
    }
  });
  $.get( "ministeres/"+$('html').attr('lang'), function( data ) {
    for(minis in data["ministeres"]) {
      minis_name = data["ministeres"][minis];
      $('#filtre-minis').append('<option>' + (minis_name ? minis_name : 'Empty') + '</option>');
    }
    $('select').selectric('refresh');
  });

    $.get( "secteurs/"+$('html').attr('lang'), function( data ) {
    for(sect in data["secteurs"]) {
      sect_name = data["secteurs"][sect];
      $('#filtre-sect').append('<option>' + (sect_name ? sect_name : 'Empty') + '</option>');
    }
    $('select').selectric('refresh');
  });
  $( function() {
    $( "#slider-range" ).slider({
      range: true,
      min: 0000,
      max: 1000,
      values: [ 3, 900 ],
      slide: function( event, ui ) {
        $( "#amount" ).val( "" + ui.values[ 0 ] + " - " + ui.values[ 1 ] );
      }
    });
    $( "#amount" ).val( " " + $( "#slider-range" ).slider( "values", 0 ) +
    " - " + $( "#slider-range" ).slider( "values", 1 ) );
  } );
}
